from django.core.management.base import BaseCommand
from cloudinary import api
from photos.models import Photo
import time


class Command(BaseCommand):
    help = 'Find and optionally delete orphaned Cloudinary images'

    def add_arguments(self, parser):
        parser.add_argument(
            '--delete',
            action='store_true',
            help='Actually delete orphaned images (default: dry run)',
        )
        parser.add_argument(
            '--folder',
            type=str,
            default='batches',
            help='Cloudinary folder to check (default: batches)',
        )

    def handle(self, *args, **options):
        delete = options['delete']
        folder = options['folder']
        
        self.stdout.write(f'Checking Cloudinary folder: {folder}')
        self.stdout.write(f'Mode: {"DELETE" if delete else "DRY RUN"}\n')
        
        # Get all public_ids from database
        db_public_ids = set(
            Photo.objects.values_list('original_image', flat=True)
        )
        db_public_ids.update(
            Photo.objects.values_list('preview_image', flat=True)
        )
        db_public_ids = {str(pid) for pid in db_public_ids if pid}
        
        self.stdout.write(f'Found {len(db_public_ids)} images in database')
        
        # Get all resources from Cloudinary
        orphaned = []
        next_cursor = None
        
        try:
            while True:
                response = api.resources(
                    type='upload',
                    prefix=folder,
                    max_results=500,
                    next_cursor=next_cursor
                )
                
                for resource in response.get('resources', []):
                    public_id = resource['public_id']
                    if public_id not in db_public_ids:
                        orphaned.append(public_id)
                
                next_cursor = response.get('next_cursor')
                if not next_cursor:
                    break
                
                time.sleep(0.5)  # Rate limiting
        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {e}'))
            return
        
        self.stdout.write(f'\nFound {len(orphaned)} orphaned image(s)')
        
        if orphaned:
            for public_id in orphaned[:10]:  # Show first 10
                self.stdout.write(f'  - {public_id}')
            
            if len(orphaned) > 10:
                self.stdout.write(f'  ... and {len(orphaned) - 10} more')
            
            if delete:
                self.stdout.write('\nDeleting orphaned images...')
                deleted = 0
                failed = 0
                
                for public_id in orphaned:
                    try:
                        api.delete_resources([public_id])
                        deleted += 1
                        if deleted % 10 == 0:
                            self.stdout.write(f'Deleted {deleted}/{len(orphaned)}')
                        time.sleep(0.2)  # Rate limiting
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(
                            f'Failed to delete {public_id}: {e}'
                        ))
                        failed += 1
                
                self.stdout.write(self.style.SUCCESS(
                    f'\n✓ Deleted {deleted} image(s)'
                ))
                if failed > 0:
                    self.stdout.write(self.style.WARNING(
                        f'⚠ Failed to delete {failed} image(s)'
                    ))
            else:
                self.stdout.write(self.style.WARNING(
                    '\n⚠ DRY RUN - Use --delete to actually remove these images'
                ))


