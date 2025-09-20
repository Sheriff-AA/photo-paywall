import os
import uuid
import requests
import zipfile
import tempfile


from django.db import models
from django.core.files.base import ContentFile
from cloudinary.models import CloudinaryField
from cloudinary import uploader
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO


class Batch(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    zip_file = CloudinaryField('zip', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Batches'
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Generate zip file after batch is created and has photos
        if self.photos.exists() and not self.zip_file:
            self.generate_zip_file()

    def generate_zip_file(self):
        """Generate zip file containing all original photos in the batch"""
        if not self.photos.exists():
            return
        
        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as temp_zip:
            with zipfile.ZipFile(temp_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for photo in self.photos.all():
                    if photo.original_image:
                        # Download image from Cloudinary
                        response = uploader.explicit(photo.original_image.public_id, type="upload")
                        if response.get('secure_url'):
                            img_response = requests.get(response['secure_url'])
                            if img_response.status_code == 200:
                                # Add to zip with a clean filename
                                filename = f"{photo.id}_{photo.original_image.public_id.split('/')[-1]}.jpg"
                                zipf.writestr(filename, img_response.content)
            
            # Upload zip to Cloudinary
            with open(temp_zip.name, 'rb') as zip_file:
                upload_result = uploader.upload(
                    zip_file,
                    resource_type='raw',
                    public_id=f'batch_zips/{self.id}',
                    format='zip'
                )
                self.zip_file = upload_result['public_id']
                self.save(update_fields=['zip_file'])
            
            # Clean up temp file
            os.unlink(temp_zip.name)

class Photo(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name='photos')
    original_image = CloudinaryField('image')
    preview_image = CloudinaryField('image', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Photo {self.id} - {self.batch.title}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.original_image and not self.preview_image:
            self.generate_preview()

    def generate_preview(self):
        """Generate watermarked preview image"""
        if not self.original_image:
            return
        
        try:
            # Get image URL from Cloudinary
            original_url = self.original_image.url
            
            # Download original image
            response = requests.get(original_url)
            if response.status_code != 200:
                return
            
            # Open with PIL
            img = Image.open(BytesIO(response.content))
            
            # Resize for preview (max 800px width)
            if img.width > 800:
                ratio = 800 / img.width
                new_height = int(img.height * ratio)
                img = img.resize((800, new_height), Image.Resampling.LANCZOS)
            
            # Add watermark
            img = self.add_watermark(img)
            
            # Save to BytesIO
            output = BytesIO()
            img.save(output, format='JPEG', quality=85)
            output.seek(0)
            
            # Upload to Cloudinary
            upload_result = uploader.upload(
                output,
                public_id=f'previews/{self.id}',
                transformation=[
                    {'quality': 'auto:low'},
                    {'fetch_format': 'auto'}
                ]
            )
            
            self.preview_image = upload_result['public_id']
            self.save(update_fields=['preview_image'])
            
        except Exception as e:
            print(f"Error generating preview for photo {self.id}: {e}")
    
    def add_watermark(self, img):
        """Add watermark to image"""
        # Convert to RGBA if necessary
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        # Create transparent overlay
        overlay = Image.new('RGBA', img.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(overlay)
        
        # Watermark text
        watermark_text = "PREVIEW"
        
        # Try to use a font, fall back to default if not available
        try:
            font_size = max(20, min(img.width, img.height) // 20)
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()
        
        # Get text bounding box
        bbox = draw.textbbox((0, 0), watermark_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Add watermarks in a grid pattern
        spacing_x = text_width + 50
        spacing_y = text_height + 30
        
        for x in range(0, img.width + spacing_x, spacing_x):
            for y in range(0, img.height + spacing_y, spacing_y):
                draw.text(
                    (x, y), 
                    watermark_text, 
                    fill=(255, 255, 255, 100),
                    font=font
                )
        
        # Combine with original image
        watermarked = Image.alpha_composite(img, overlay)
        return watermarked.convert('RGB')