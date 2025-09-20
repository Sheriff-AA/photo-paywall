from django.core.management.base import BaseCommand
from photos.models import Batch

class Command(BaseCommand):
    help = 'Generate zip files for batches that don\'t have them'
    
    def handle(self, *args, **options):
        batches_without_zip = Batch.objects.filter(zip_file__isnull=True)
        
        self.stdout.write(f"Found {batches_without_zip.count()} batches without zip files")
        
        for batch in batches_without_zip:
            if batch.photos.exists():
                self.stdout.write(f"Generating zip for batch: {batch.title}")
                batch.generate_zip_file()
                self.stdout.write(self.style.SUCCESS(f"✓ Generated zip for {batch.title}"))
            else:
                self.stdout.write(self.style.WARNING(f"⚠ Batch {batch.title} has no photos"))

