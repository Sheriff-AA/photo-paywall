from django.core.management.base import BaseCommand
from photos.models import Batch, Photo


class Command(BaseCommand):
    help = 'Retry failed photo processing tasks'

    def add_arguments(self, parser):
        parser.add_argument(
            '--previews',
            action='store_true',
            help='Retry failed preview generations',
        )
        parser.add_argument(
            '--zips',
            action='store_true',
            help='Retry failed ZIP generations',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Retry both previews and ZIPs',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=50,
            help='Maximum number of items to retry (default: 50)',
        )

    def handle(self, *args, **options):
        retry_previews = options['previews'] or options['all']
        retry_zips = options['zips'] or options['all']
        limit = options['limit']
        
        if not (retry_previews or retry_zips):
            self.stdout.write(self.style.ERROR(
                'Please specify --previews, --zips, or --all'
            ))
            return
        
        if retry_previews:
            failed_photos = Photo.objects.filter(
                preview_status='failed'
            )[:limit]
            
            count = 0
            for photo in failed_photos:
                photo.schedule_preview_generation()
                count += 1
            
            self.stdout.write(self.style.SUCCESS(
                f'✓ Queued {count} failed preview(s) for retry'
            ))
        
        if retry_zips:
            failed_batches = Batch.objects.filter(
                zip_status='failed'
            )[:limit]
            
            count = 0
            for batch in failed_batches:
                batch.schedule_zip_generation()
                count += 1
            
            self.stdout.write(self.style.SUCCESS(
                f'✓ Queued {count} failed ZIP(s) for retry'
            ))

            