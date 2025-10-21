from django.core.management.base import BaseCommand
from django.db.models import Count, Q
from photos.models import Batch, Photo


class Command(BaseCommand):
    help = 'Display photo processing statistics'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== Photo Gallery Statistics ===\n'))
        
        # Batch statistics
        total_batches = Batch.objects.count()
        self.stdout.write(f'Total Batches: {total_batches}')
        
        batch_status = Batch.objects.values('zip_status').annotate(
            count=Count('id')
        )
        self.stdout.write('\nBatch ZIP Status:')
        for status in batch_status:
            self.stdout.write(f"  {status['zip_status']}: {status['count']}")
        
        # Photo statistics
        total_photos = Photo.objects.count()
        self.stdout.write(f'\nTotal Photos: {total_photos}')
        
        photo_status = Photo.objects.values('preview_status').annotate(
            count=Count('id')
        )
        self.stdout.write('\nPhoto Preview Status:')
        for status in photo_status:
            self.stdout.write(f"  {status['preview_status']}: {status['count']}")
        
        # Failed items
        failed_previews = Photo.objects.filter(preview_status='failed').count()
        failed_zips = Batch.objects.filter(zip_status='failed').count()
        
        if failed_previews > 0 or failed_zips > 0:
            self.stdout.write(self.style.WARNING(f'\n⚠ Failed Previews: {failed_previews}'))
            self.stdout.write(self.style.WARNING(f'⚠ Failed ZIPs: {failed_zips}'))
        
        # Batches without photos
        empty_batches = Batch.objects.annotate(
            photo_count=Count('photos')
        ).filter(photo_count=0).count()
        
        if empty_batches > 0:
            self.stdout.write(self.style.WARNING(f'\n⚠ Empty Batches: {empty_batches}'))

