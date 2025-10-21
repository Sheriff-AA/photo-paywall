import os
import uuid
import requests
import zipfile
from io import BytesIO
from decimal import Decimal
from functools import cached_property

from django.db import models, transaction
from django.core.cache import cache
from django.core.exceptions import ValidationError
from cloudinary.models import CloudinaryField
from cloudinary import uploader, CloudinaryImage
from PIL import Image, ImageDraw, ImageFont


class BatchQuerySet(models.QuerySet):
    def with_photo_counts(self):
        return self.annotate(photo_count=models.Count('photos'))


class Batch(models.Model):
    CATEGORY_CHOICES = [
        ('wedding', 'Wedding'),
        ('corporate', 'Corporate'),
        ('celebration', 'Celebration'),
        ('other', 'Other'),
    ]
    
    # Processing status choices
    ZIP_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    zip_file = CloudinaryField('zip', blank=True, null=True)
    zip_status = models.CharField(
        max_length=20, 
        choices=ZIP_STATUS_CHOICES, 
        default='pending'
    )
    zip_error = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = BatchQuerySet.as_manager()
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Batches'
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['category', '-created_at']),
        ]
    
    def __str__(self):
        return self.title
    
    def clean(self):
        if self.price and self.price < Decimal('0'):
            raise ValidationError({'price': 'Price cannot be negative'})
        
    @cached_property
    def preview_image_url(self):
        """Get preview image URL from first photo"""
        first_photo = self.photos.only('preview_image', 'original_image').first()
        if first_photo:
            return first_photo.preview_url
        return None
    
    # def get_preview_image_url(self):
    #     """Get cached preview image URL"""
    #     cache_key = f'batch_preview_{self.id}'
    #     url = cache.get(cache_key)
        
    #     if not url:
    #         first_photo = self.photos.only('preview_image', 'original_image').first()
    #         if first_photo:
    #             url = first_photo.get_preview_url()
    #             cache.set(cache_key, url, 3600)  # Cache for 1 hour
        
    #     return url
    
    def schedule_zip_generation(self):
        """Queue ZIP generation as async task"""
        # Import here to avoid circular imports
        from .tasks import generate_batch_zip
        
        if not self.photos.exists():
            return
        
        self.zip_status = 'pending'
        self.zip_error = None
        self.save(update_fields=['zip_status', 'zip_error'])
        
        # Queue Celery task
        generate_batch_zip.delay(str(self.id))

    def generate_zip_file_sync(self):
        """
        Synchronous ZIP generation with streaming - should only be called from background task.
        Returns tuple: (success: bool, error_message: str or None)
        """
        if not self.photos.exists():
            return False, "No photos in batch"
        
        self.zip_status = 'processing'
        self.save(update_fields=['zip_status'])
        
        import tempfile
        import shutil
        
        # Use temporary file instead of in-memory buffer
        temp_zip = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
        
        try:
            with zipfile.ZipFile(temp_zip.name, 'w', zipfile.ZIP_DEFLATED) as zipf:
                photos = self.photos.select_related('batch').only(
                    'id', 'original_image', 'batch_id'
                )
                
                for photo in photos:
                    if not photo.original_image:
                        continue
                    
                    try:
                        cloudinary_image = CloudinaryImage(str(photo.original_image))
                        download_url = cloudinary_image.build_url(
                            resource_type='image',
                            type='upload'
                        )
                        
                        # Stream download directly to ZIP without loading into memory
                        img_response = requests.get(download_url, timeout=30, stream=True)
                        img_response.raise_for_status()
                        
                        # Extract clean filename
                        public_id_parts = str(photo.original_image).split('/')
                        base_name = public_id_parts[-1] if public_id_parts else str(photo.id)
                        filename = f"{photo.id}_{base_name}.jpg"
                        
                        # Write streamed content directly to ZIP
                        with zipf.open(filename, 'w') as zip_entry:
                            for chunk in img_response.iter_content(chunk_size=8192):
                                if chunk:
                                    zip_entry.write(chunk)
                        
                    except Exception as e:
                        print(f"Failed to add photo {photo.id} to ZIP: {e}")
                        continue
            
            # Upload the temp file to Cloudinary
            with open(temp_zip.name, 'rb') as zip_file:
                upload_result = uploader.upload(
                    zip_file,
                    resource_type='raw',
                    public_id=f'batch_zips/{self.id}',
                    format='zip',
                    overwrite=True
                )
            
            self.zip_file = upload_result['public_id']
            self.zip_status = 'completed'
            self.zip_error = None
            self.save(update_fields=['zip_file', 'zip_status', 'zip_error'])
            
            return True, None
            
        except Exception as e:
            error_msg = str(e)
            self.zip_status = 'failed'
            self.zip_error = error_msg
            self.save(update_fields=['zip_status', 'zip_error'])
            return False, error_msg
            
        finally:
            # Clean up temp file
            try:
                os.unlink(temp_zip.name)
            except:
                pass


class Photo(models.Model):
    PREVIEW_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    batch = models.ForeignKey(
        Batch, 
        on_delete=models.CASCADE, 
        related_name='photos',
        db_index=True
    )
    original_image = CloudinaryField('image')
    preview_image = CloudinaryField('image', blank=True, null=True)
    preview_status = models.CharField(
        max_length=20,
        choices=PREVIEW_STATUS_CHOICES,
        default='pending'
    )
    preview_error = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['batch', 'created_at']),
            models.Index(fields=['preview_status']),
        ]
    
    def __str__(self):
        return f"Photo {self.id} - {self.batch.title}"
    
    @cached_property
    def preview_url(self):
        """Get preview image URL - computed once per instance"""
        if self.preview_image:
            return CloudinaryImage(str(self.preview_image)).build_url()
        elif self.original_image:
            return CloudinaryImage(str(self.original_image)).build_url()
        return None
    
    def thumbnail_url(self, width=300, height=200):
        """Generate thumbnail URL - no caching needed, just string formatting"""
        public_id = self.preview_image or self.original_image
        if not public_id:
            return None
        return CloudinaryImage(str(public_id)).build_url(
            width=width, height=height, crop="fill", quality="auto"
        )
    
    def schedule_preview_generation(self):
        """Queue preview generation as async task"""
        from .tasks import generate_photo_preview
        
        if not self.original_image:
            return
        
        self.preview_status = 'pending'
        self.save(update_fields=['preview_status'])
        
        # Queue Celery task
        generate_photo_preview.delay(str(self.id))
    
    # def generate_preview_sync(self):
    #     """
    #     Synchronous preview generation - called from background task.
    #     Returns tuple: (success: bool, error_message: str or None)
    #     """
    #     if not self.original_image:
    #         return False, "No original image"
        
    #     self.preview_status = 'processing'
    #     self.save(update_fields=['preview_status'])
        
    #     try:
    #         cloudinary_image = CloudinaryImage(str(self.original_image))
    #         original_url = cloudinary_image.build_url()
            
    #         # Download with timeout and size limit
    #         response = requests.get(original_url, timeout=30, stream=True)
    #         response.raise_for_status()
            
    #         # Check file size (limit to 50MB)
    #         content_length = response.headers.get('content-length')
    #         if content_length and int(content_length) > 50 * 1024 * 1024:
    #             raise ValueError("Image too large (>50MB)")
            
    #         # Open image
    #         img = Image.open(BytesIO(response.content))
            
    #         # Convert to RGB if necessary (handles RGBA, P, etc.)
    #         if img.mode not in ('RGB', 'RGBA'):
    #             img = img.convert('RGB')
            
    #         # Resize BEFORE watermarking for better performance
    #         max_width = 800
    #         if img.width > max_width:
    #             ratio = max_width / img.width
    #             new_height = int(img.height * ratio)
    #             img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
            
    #         # Add watermark
    #         img = self.add_watermark(img)
            
    #         # Save with optimization
    #         output = BytesIO()
    #         img.save(output, format='JPEG', quality=85, optimize=True)
    #         output.seek(0)
            
    #         # Upload to Cloudinary with transformations
    #         upload_result = uploader.upload(
    #             output,
    #             public_id=f'previews/{self.id}',
    #             folder='previews',
    #             resource_type='image',
    #             overwrite=True,
    #             transformation=[
    #                 {'quality': 'auto:low'},
    #                 {'fetch_format': 'auto'}
    #             ]
    #         )
            
    #         self.preview_image = upload_result['public_id']
    #         self.preview_status = 'completed'
    #         self.preview_error = None
    #         self.save(update_fields=['preview_image', 'preview_status', 'preview_error'])
            
    #         # Invalidate cache
    #         cache.delete(f'batch_preview_{self.batch_id}')
            
    #         return True, None
            
    #     except Exception as e:
    #         error_msg = str(e)
    #         self.preview_status = 'failed'
    #         self.preview_error = error_msg
    #         self.save(update_fields=['preview_status', 'preview_error'])
    #         return False, error_msg

    def generate_preview_sync(self):
        """
        Synchronous preview generation using Cloudinary transformations.
        Returns tuple: (success: bool, error_message: str or None)
        """
        if not self.original_image:
            return False, "No original image"
        
        self.preview_status = 'processing'
        self.save(update_fields=['preview_status'])
        
        try:
            # Get the original image URL with transformations applied
            cloudinary_image = CloudinaryImage(str(self.original_image))
            
            # Build URL with watermark transformations
            watermarked_url = cloudinary_image.build_url(
                transformation=[
                    {'width': 800, 'crop': 'limit'},
                    {'quality': 'auto:low'},
                    # Center watermark
                    {'overlay': {'font_family': 'Arial', 'font_size': 40, 'font_weight': 'bold', 'text': 'PREVIEW'}},
                    {'flags': 'layer_apply', 'gravity': 'center', 'opacity': 50},
                    # Top-left watermark
                    {'overlay': {'font_family': 'Arial', 'font_size': 40, 'font_weight': 'bold', 'text': 'PREVIEW'}},
                    {'flags': 'layer_apply', 'gravity': 'north_west', 'x': 100, 'y': 100, 'opacity': 50},
                    # Top-right watermark
                    {'overlay': {'font_family': 'Arial', 'font_size': 40, 'font_weight': 'bold', 'text': 'PREVIEW'}},
                    {'flags': 'layer_apply', 'gravity': 'north_east', 'x': 100, 'y': 100, 'opacity': 50},
                    # Bottom-left watermark
                    {'overlay': {'font_family': 'Arial', 'font_size': 40, 'font_weight': 'bold', 'text': 'PREVIEW'}},
                    {'flags': 'layer_apply', 'gravity': 'south_west', 'x': 100, 'y': 100, 'opacity': 50},
                    # Bottom-right watermark
                    {'overlay': {'font_family': 'Arial', 'font_size': 40, 'font_weight': 'bold', 'text': 'PREVIEW'}},
                    {'flags': 'layer_apply', 'gravity': 'south_east', 'x': 100, 'y': 100, 'opacity': 50},
                ]
            )
            
            # Download the transformed image
            response = requests.get(watermarked_url, timeout=30, stream=True)
            response.raise_for_status()
            
            # Upload it as a new preview image
            preview_public_id = f'previews/{self.id}'
            upload_result = uploader.upload(
                BytesIO(response.content),
                public_id=preview_public_id,
                folder='previews',
                resource_type='image',
                overwrite=True
            )
            
            self.preview_image = upload_result['public_id']
            self.preview_status = 'completed'
            self.preview_error = None
            self.save(update_fields=['preview_image', 'preview_status', 'preview_error'])
            
            # Invalidate cache
            cache.delete(f'batch_preview_{self.batch_id}')
            
            return True, None
            
        except Exception as e:
            error_msg = str(e)
            self.preview_status = 'failed'
            self.preview_error = error_msg
            self.save(update_fields=['preview_status', 'preview_error'])
            return False, error_msg
    
    # def add_watermark(self, img):
    #     """Add watermark to image - optimized version"""
    #     # Convert to RGBA only if needed
    #     if img.mode != 'RGBA':
    #         img = img.convert('RGBA')
        
    #     # Create overlay
    #     overlay = Image.new('RGBA', img.size, (255, 255, 255, 0))
    #     draw = ImageDraw.Draw(overlay)
        
    #     watermark_text = "PREVIEW"
        
    #     # Calculate font size based on image dimensions
    #     font_size = max(20, min(img.width, img.height) // 20)
        
    #     try:
    #         # Try common font locations
    #         font_paths = [
    #             "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",  # Linux
    #             "/System/Library/Fonts/Helvetica.ttc",  # macOS
    #             "C:\\Windows\\Fonts\\arial.ttf",  # Windows
    #         ]
            
    #         font = None
    #         for path in font_paths:
    #             if os.path.exists(path):
    #                 font = ImageFont.truetype(path, font_size)
    #                 break
            
    #         if not font:
    #             font = ImageFont.load_default()
    #     except:
    #         font = ImageFont.load_default()
        
    #     # Get text dimensions
    #     bbox = draw.textbbox((0, 0), watermark_text, font=font)
    #     text_width = bbox[2] - bbox[0]
    #     text_height = bbox[3] - bbox[1]
        
    #     # Add watermarks in grid (optimized spacing)
    #     spacing_x = text_width + 100
    #     spacing_y = text_height + 60
        
    #     for x in range(-text_width, img.width + text_width, spacing_x):
    #         for y in range(-text_height, img.height + text_height, spacing_y):
    #             draw.text(
    #                 (x, y), 
    #                 watermark_text, 
    #                 fill=(255, 255, 255, 128),  # Slightly more visible
    #                 font=font
    #             )
        
    #     # Composite and convert back to RGB
    #     watermarked = Image.alpha_composite(img, overlay)
    #     return watermarked.convert('RGB')
    
    # def get_thumbnail_url(self, width=300, height=200):
    #     """Get cached thumbnail URL"""
    #     cache_key = f'photo_thumb_{self.id}_{width}x{height}'
    #     url = cache.get(cache_key)
        
    #     if not url:
    #         if self.preview_image:
    #             url = CloudinaryImage(str(self.preview_image)).build_url(
    #                 width=width, height=height, crop="fill", quality="auto"
    #             )
    #         elif self.original_image:
    #             url = CloudinaryImage(str(self.original_image)).build_url(
    #                 width=width, height=height, crop="fill", quality="auto"
    #             )
            
    #         if url:
    #             cache.set(cache_key, url, 3600)
        
    #     return url
    
    # def get_preview_url(self):
    #     """Get cached preview URL"""
    #     cache_key = f'photo_preview_{self.id}'
    #     url = cache.get(cache_key)
        
    #     if not url:
    #         if self.preview_image:
    #             url = CloudinaryImage(str(self.preview_image)).build_url()
    #         elif self.original_image:
    #             url = CloudinaryImage(str(self.original_image)).build_url()
            
    #         if url:
    #             cache.set(cache_key, url, 3600)
        
    #     return url
    
    