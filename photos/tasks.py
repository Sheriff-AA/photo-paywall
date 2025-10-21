from celery import shared_task, group, chord
from django.core.cache import cache
from .models import Batch, Photo


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def generate_photo_preview(self, photo_id):
    """
    Background task to generate photo preview with watermark.
    Retries up to 3 times on failure.
    """
    try:
        photo = Photo.objects.get(id=photo_id)
        success, error = photo.generate_preview_sync()
        
        if not success:
            # Retry on failure
            raise Exception(f"Preview generation failed: {error}")
        
        return {
            'photo_id': photo_id,
            'status': 'success'
        }
        
    except Photo.DoesNotExist:
        # Don't retry if photo doesn't exist
        return {
            'photo_id': photo_id,
            'status': 'not_found'
        }
    except Exception as e:
        # Retry on any other error
        raise self.retry(exc=e)


@shared_task(bind=True, max_retries=2, default_retry_delay=120)
def generate_batch_zip(self, batch_id):
    """
    Background task to generate ZIP file for a batch.
    Retries up to 2 times on failure.
    """
    try:
        batch = Batch.objects.get(id=batch_id)
        success, error = batch.generate_zip_file_sync()
        
        if not success:
            raise Exception(f"ZIP generation failed: {error}")
        
        return {
            'batch_id': batch_id,
            'status': 'success'
        }
        
    except Batch.DoesNotExist:
        return {
            'batch_id': batch_id,
            'status': 'not_found'
        }
    except Exception as e:
        raise self.retry(exc=e)


@shared_task
def process_batch_upload(batch_id, photo_ids):
    """
    Orchestrates preview generation for multiple photos and then ZIP generation.
    Uses Celery's chord to wait for all previews before creating ZIP.
    """
    # Create a group of preview generation tasks
    preview_tasks = group(
        generate_photo_preview.s(photo_id) for photo_id in photo_ids
    )
    
    # # Use chord: run all previews in parallel, then generate ZIP when done
    # result = chord(preview_tasks)(generate_batch_zip.s(batch_id))

    # Use chord with immutable signature (si) so results aren't passed to callback
    result = chord(preview_tasks)(generate_batch_zip.si(batch_id))
    
    return {
        'batch_id': batch_id,
        'photo_count': len(photo_ids),
        'task_id': result.id
    }


@shared_task
def retry_failed_previews():
    """
    Periodic task to retry failed preview generations.
    Run this via Celery Beat (e.g., every hour).
    """
    failed_photos = Photo.objects.filter(
        preview_status='failed',
        preview_image__isnull=True
    )[:50]  # Process 50 at a time
    
    retry_count = 0
    for photo in failed_photos:
        photo.schedule_preview_generation()
        retry_count += 1
    
    return {
        'retried_count': retry_count
    }


@shared_task
def cleanup_old_cache():
    """
    Periodic task to clean up old cache entries.
    Run this via Celery Beat (e.g., daily).
    """
    # Django cache doesn't have built-in cleanup for pattern-based keys
    # This is a placeholder - implement based on your cache backend
    
    # For Redis, you could use:
    # from django_redis import get_redis_connection
    # redis_conn = get_redis_connection("default")
    # keys = redis_conn.keys("batch_preview_*")
    # if keys:
    #     redis_conn.delete(*keys)
    
    return {'status': 'completed'}

