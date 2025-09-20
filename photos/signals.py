from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Photo, Batch

@receiver(post_save, sender=Photo)
def photo_saved(sender, instance, created, **kwargs):
    """When a photo is saved, regenerate batch zip if needed"""
    if created:
        # Clear existing zip file so it gets regenerated with new photo
        if instance.batch.zip_file:
            instance.batch.zip_file = None
            instance.batch.save(update_fields=['zip_file'])

@receiver(post_delete, sender=Photo)
def photo_deleted(sender, instance, **kwargs):
    """When a photo is deleted, regenerate batch zip"""
    if instance.batch_id:
        try:
            batch = Batch.objects.get(id=instance.batch_id)
            if batch.zip_file:
                batch.zip_file = None
                batch.save(update_fields=['zip_file'])
        except Batch.DoesNotExist:
            pass

