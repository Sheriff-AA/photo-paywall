"""Monitoring utilities for production"""
from django.core.cache import cache
from photos.models import Batch, Photo
import logging

logger = logging.getLogger('photos')


def check_processing_health():
    """
    Check the health of photo processing pipeline.
    Returns dict with status information.
    """
    health = {
        'status': 'healthy',
        'issues': [],
        'stats': {}
    }
    
    # Check for stuck processing
    stuck_photos = Photo.objects.filter(
        preview_status='processing'
    ).count()
    
    stuck_batches = Batch.objects.filter(
        zip_status='processing'
    ).count()
    
    if stuck_photos > 10:
        health['status'] = 'degraded'
        health['issues'].append(f'{stuck_photos} photos stuck in processing')
    
    if stuck_batches > 5:
        health['status'] = 'degraded'
        health['issues'].append(f'{stuck_batches} batches stuck in processing')
    
    # Check failure rate
    total_photos = Photo.objects.count()
    failed_photos = Photo.objects.filter(preview_status='failed').count()
    
    if total_photos > 0:
        failure_rate = (failed_photos / total_photos) * 100
        health['stats']['photo_failure_rate'] = f'{failure_rate:.1f}%'
        
        if failure_rate > 10:
            health['status'] = 'unhealthy'
            health['issues'].append(f'High failure rate: {failure_rate:.1f}%')
    
    # Check pending queue size
    pending_photos = Photo.objects.filter(preview_status='pending').count()
    pending_batches = Batch.objects.filter(zip_status='pending').count()
    
    health['stats']['pending_previews'] = pending_photos
    health['stats']['pending_zips'] = pending_batches
    
    if pending_photos > 100:
        health['status'] = 'degraded'
        health['issues'].append(f'Large pending queue: {pending_photos} photos')
    
    logger.info(f'Health check: {health["status"]} - {health["issues"]}')
    
    return health


