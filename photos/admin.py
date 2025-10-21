from django.contrib import admin
from django import forms
from django.contrib import messages
from django.db import transaction
from django.utils.html import format_html
from cloudinary import uploader
from .models import Batch, Photo
from .tasks import process_batch_upload
from unfold.admin import ModelAdmin
from unfold.decorators import display, action


class MultipleFileInput(forms.ClearableFileInput):
    """Custom widget that allows multiple file selection"""
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    """Custom field that accepts multiple files"""
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput(attrs={
            'accept': 'image/*',
            'multiple': True
        }))
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = [single_file_clean(data, initial)] if data else []
        return result


class BatchAdminForm(forms.ModelForm):
    """Custom form that adds bulk upload field"""
    bulk_upload = MultipleFileField(
        required=False,
        label='Upload Multiple Photos',
        help_text='Select multiple image files. Processing will happen in the background.'
    )
    
    class Meta:
        model = Batch
        fields = '__all__'
    
    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price and price < 0:
            raise forms.ValidationError("Price cannot be negative")
        return price


@admin.register(Batch)
class BatchAdmin(ModelAdmin):
    form = BatchAdminForm
    list_display = [
        'title', 
        'category', 
        'price', 
        'photo_count', 
        'zip_status_display',
        'created_at'
    ]
    list_filter = ['category', 'zip_status', 'created_at']
    search_fields = ['title', 'description']
    readonly_fields = [
        'id', 
        'created_at', 
        'updated_at', 
        'zip_file_link',
        'photo_count_display',
        'zip_status_display',
        'view_photos_link'
    ]
    
    actions = ['regenerate_zip_files', 'regenerate_all_previews']
    
    fieldsets = (
        ('Batch Information', {
            'fields': ('title', 'description', 'category', 'price')
        }),
        ('Upload Photos', {
            'fields': ('bulk_upload',),
            'description': (
                '<strong>Upload Process:</strong><br/>'
                '1. Photos are uploaded to Cloudinary<br/>'
                '2. Watermarked previews are generated in the background<br/>'
                '3. A ZIP file is created automatically when all previews are ready<br/>'
                '<em>You will be notified when uploads complete. Processing continues in the background.</em>'
            )
        }),
        ('System Information', {
            'fields': (
                'id', 
                'photo_count_display',
                'view_photos_link',
                'zip_status_display',
                'zip_file_link', 
                'created_at', 
                'updated_at'
            ),
            # 'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queryset with aggregations"""
        qs = super().get_queryset(request)
        return qs.with_photo_counts()
    
    @display(description='Photos', ordering='photo_count')
    def photo_count(self, obj):
        """Display the number of photos in the batch"""
        if hasattr(obj, 'photo_count'):
            return obj.photo_count
        return obj.photos.count()
    
    @display(description='Photo Status')
    def photo_count_display(self, obj):
        """Detailed photo count with status breakdown"""
        if not obj.id:
            return "-"
        
        total = obj.photos.count()
        completed = obj.photos.filter(preview_status='completed').count()
        pending = obj.photos.filter(preview_status='pending').count()
        processing = obj.photos.filter(preview_status='processing').count()
        failed = obj.photos.filter(preview_status='failed').count()
        
        return format_html(
            '<strong>Total:</strong> {} | '
            '<span style="color: #22c55e;">✓ Completed: {}</span> | '
            '<span style="color: #f97316;">⏳ Pending: {}</span> | '
            '<span style="color: #3b82f6;">↻ Processing: {}</span> | '
            '<span style="color: #ef4444;">✗ Failed: {}</span>',
            total, completed, pending, processing, failed
        )
    
    @display(description='ZIP Status')
    def zip_status_display(self, obj):
        """Display ZIP status with color coding"""
        if not obj.id:
            return "-"
        
        status_icons = {
            'pending': '⏳',
            'processing': '↻',
            'completed': '✓',
            'failed': '✗',
        }
        
        status_colors = {
            'pending': '#f97316',
            'processing': '#3b82f6',
            'completed': '#22c55e',
            'failed': '#ef4444',
        }
        color = status_colors.get(obj.zip_status, '#9ca3af')
        icon = status_icons.get(obj.zip_status, '•')
        
        html = format_html(
            '<span style="color: {}; font-weight: bold; font-size: 14px;">{} {}</span>',
            color,
            icon,
            obj.get_zip_status_display().capitalize()
        )
        
        if obj.zip_status == 'failed' and obj.zip_error:
            html += format_html(
                '<br/><small style="color: #ef4444;" title="{}">{}</small>',
                obj.zip_error,
                obj.zip_error[:50] + '...' if len(obj.zip_error) > 50 else obj.zip_error
            )
        
        return html
    
    @display(description='ZIP File')
    def zip_file_link(self, obj):
        """Display a clickable link to the ZIP file if it exists"""
        if obj and obj.zip_file:
            try:
                from cloudinary import CloudinaryImage
                url = CloudinaryImage(str(obj.zip_file)).build_url(resource_type='raw')
                return format_html(
                    '<a href="{}" target="_blank" class="button" style="display: inline-block; padding: 8px 16px; background: linear-gradient(135deg, #f97316, #fb923c); color: white; text-decoration: none; border-radius: 6px; font-weight: 500;">⬇ Download ZIP</a>',
                    url
                )
            except:
                return format_html(
                    '<span style="color: #9ca3af;">ZIP file exists but URL unavailable</span>'
                )
        
        if obj.zip_status == 'processing':
            return format_html('<em style="color: #f97316;">↻ ZIP file is being generated...</em>')
        elif obj.zip_status == 'failed':
            return format_html('<em style="color: #ef4444;">✗ ZIP generation failed</em>')
        
        return format_html('<span style="color: #9ca3af;">No ZIP file yet</span>')
    
    @action(description='Regenerate ZIP files')
    def regenerate_zip_files(self, request, queryset):
        """Admin action to regenerate ZIP files for selected batches"""
        count = 0
        for batch in queryset:
            if batch.photos.exists():
                batch.schedule_zip_generation()
                count += 1
        
        self.message_user(
            request,
            f"✓ Queued ZIP regeneration for {count} batch(es).",
            messages.SUCCESS
        )
    
    @action(description='Regenerate all previews')
    def regenerate_all_previews(self, request, queryset):
        """Admin action to regenerate all previews for selected batches"""
        total_photos = 0
        for batch in queryset:
            photos = batch.photos.all()
            for photo in photos:
                photo.schedule_preview_generation()
                total_photos += 1
        
        self.message_user(
            request,
            f"✓ Queued preview regeneration for {total_photos} photo(s) across {queryset.count()} batch(es).",
            messages.SUCCESS
        )

    @display(description='Photos')
    def view_photos_link(self, obj):
        """Link to filtered photo admin showing this batch's photos"""
        if not obj.id:
            return "-"
        
        from django.urls import reverse
        url = reverse('admin:photos_photo_changelist') + f'?batch__id__exact={obj.id}'
        count = obj.photos.count()
        
        return format_html(
            '<a href="{}" class="button" style="display: inline-block; padding: 8px 16px; background: linear-gradient(135deg, #f97316, #fb923c); color: white; text-decoration: none; border-radius: 6px; font-weight: 500;">👁 View {} Photo(s)</a>',
            url,
            count
        )
    
    @transaction.atomic
    def save_model(self, request, obj, form, change):
        """
        Save the batch and handle photo uploads asynchronously.
        """
        # Save the batch first
        is_new = obj.pk is None
        super().save_model(request, obj, form, change)
        
        # Handle bulk photo uploads
        files = request.FILES.getlist('bulk_upload')
        
        if files:
            self._process_bulk_upload(request, obj, files)
    
    def _process_bulk_upload(self, request, batch, files):
        """Process bulk photo uploads asynchronously"""
        uploaded_count = 0
        failed_uploads = []
        photo_ids = []
        
        # First, upload all files to Cloudinary and create Photo objects
        for file in files:
            # Validate file size (e.g., max 25MB per file)
            if file.size > 25 * 1024 * 1024:
                failed_uploads.append({
                    'filename': file.name,
                    'error': 'File too large (max 25MB)'
                })
                continue
            
            try:
                # Upload to Cloudinary
                upload_result = uploader.upload(
                    file,
                    folder=f'batches/{batch.id}/originals',
                    resource_type='image',
                    use_filename=True,
                    unique_filename=True
                )
                
                # Create Photo object (preview will be generated asynchronously)
                photo = Photo.objects.create(
                    batch=batch,
                    original_image=upload_result['public_id']
                )
                
                photo_ids.append(str(photo.id))
                uploaded_count += 1
                
            except Exception as e:
                failed_uploads.append({
                    'filename': file.name,
                    'error': str(e)
                })
        
        # Queue background processing
        if photo_ids:
            # Import here to avoid circular imports
            from .tasks import process_batch_upload
            
            # Queue the processing task
            result = process_batch_upload.delay(str(batch.id), photo_ids)
            
            messages.success(
                request,
                f"✓ Successfully uploaded {uploaded_count} photo(s) to batch '{batch.title}'. "
                f"Preview generation and ZIP creation are running in the background."
            )
            
            messages.info(
                request,
                f"Processing task ID: {result.id}. Refresh this page in a few minutes to see updates."
            )
        
        # Report failures
        if failed_uploads:
            for failed in failed_uploads:
                messages.error(
                    request,
                    f"✗ Failed to upload '{failed['filename']}': {failed['error']}"
                )
            messages.warning(
                request,
                f"{len(failed_uploads)} photo(s) failed to upload"
            )


@admin.register(Photo)
class PhotoAdmin(ModelAdmin):
    list_display = [
        'id', 
        'batch_link',
        'preview_thumbnail', 
        'preview_status_display',
        'created_at'
    ]
    list_filter = ['preview_status', 'batch', 'created_at']
    list_select_related = ['batch']
    readonly_fields = [
        'id', 
        'batch',
        'preview_image', 
        'preview_status',
        'preview_error_display',
        'created_at',
        'preview_thumbnail_large'
    ]
    search_fields = ['id', 'batch__title']
    
    actions = ['retry_preview_generation', 'force_delete_previews']
    
    fieldsets = (
        ('Photo Information', {
            'fields': ('id', 'batch', 'created_at')
        }),
        ('Images', {
            'fields': ('original_image', 'preview_thumbnail_large')
        }),
        ('Preview Status', {
            'fields': ('preview_status', 'preview_error_display')
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queryset"""
        qs = super().get_queryset(request)
        return qs.select_related('batch')
    
    @display(description='Batch')
    def batch_link(self, obj):
        """Link to the batch"""
        from django.urls import reverse
        
        url = reverse('admin:photos_batch_change', args=[obj.batch.id])
        return format_html('<a href="{}" style="color: #f97316; text-decoration: none; font-weight: 500;">→ {}</a>', url, obj.batch.title)
    
    @display(description='Thumbnail')
    def preview_thumbnail(self, obj):
        """Display small thumbnail"""
        if obj.id:
            url = obj.thumbnail_url(width=80, height=80)
            if url:
                return format_html(
                    '<img src="{}" style="max-height: 80px; max-width: 80px; border-radius: 4px; border: 1px solid #374151;" />',
                    url
                )
        return format_html('<span style="color: #9ca3af;">No image</span>')
    
    @display(description='Preview Image')
    def preview_thumbnail_large(self, obj):
        """Display larger preview in detail view"""
        if obj.id:
            url = obj.preview_url()
            if url:
                return format_html(
                    '<img src="{}" style="max-width: 600px; height: auto; border-radius: 8px; border: 1px solid #374151; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);" />',
                    url
                )
        return format_html('<span style="color: #9ca3af;">No preview available</span>')
    
    @display(description='Status')
    def preview_status_display(self, obj):
        """Display status with color coding"""
        status_icons = {
            'pending': '⏳',
            'processing': '↻',
            'completed': '✓',
            'failed': '✗',
        }
        
        status_colors = {
            'pending': '#f97316',
            'processing': '#3b82f6',
            'completed': '#22c55e',
            'failed': '#ef4444',
        }
        color = status_colors.get(obj.preview_status, '#9ca3af')
        icon = status_icons.get(obj.preview_status, '•')
        
        return format_html(
            '<span style="color: {}; font-weight: bold; font-size: 14px;">{} {}</span>',
            color,
            icon,
            obj.get_preview_status_display().capitalize()
        )
    
    @display(description='Error Details')
    def preview_error_display(self, obj):
        """Display preview error if any"""
        if obj.preview_error:
            return format_html(
                '<pre style="color: #fca5a5; white-space: pre-wrap; background-color: rgba(239, 68, 68, 0.1); padding: 12px; border-radius: 6px; border-left: 4px solid #ef4444;">{}</pre>',
                obj.preview_error
            )
        return format_html('<span style="color: #22c55e; font-weight: 500;">✓ No errors</span>')
    
    @action(description='Retry preview generation')
    def retry_preview_generation(self, request, queryset):
        """Admin action to retry preview generation for selected photos"""
        count = 0
        for photo in queryset:
            if photo.preview_status in ['failed', 'pending']:
                photo.schedule_preview_generation()
                count += 1
        
        self.message_user(
            request,
            f"✓ Queued preview regeneration for {count} photo(s).",
            messages.SUCCESS
        )
    
    @action(description='Delete and regenerate previews')
    def force_delete_previews(self, request, queryset):
        """Admin action to delete and regenerate previews"""
        count = 0
        for photo in queryset:
            photo.preview_image = None
            photo.preview_status = 'pending'
            photo.preview_error = None
            photo.save(update_fields=['preview_image', 'preview_status', 'preview_error'])
            photo.schedule_preview_generation()
            count += 1
        
        self.message_user(
            request,
            f"✓ Deleted and queued regeneration for {count} preview(s).",
            messages.SUCCESS
        )
    
    def has_add_permission(self, request):
        """Don't allow adding photos directly (use batch admin)"""
        return False

# class PhotoInline(admin.TabularInline):
#     model = Photo
#     extra = 0
#     can_delete = True
#     show_change_link = True
#     readonly_fields = ['id', 'preview_thumbnail', 'preview_status_display', 'created_at']
#     fields = ['preview_thumbnail', 'preview_status_display', 'created_at']
    
#     # Limit inline to prevent page crashes
#     max_num = 50
    
#     def preview_thumbnail(self, obj):
#         """Display thumbnail of preview or original image"""
#         if obj.id:
#             url = obj.thumbnail_url(width=100, height=100)
#             if url:
#                 return format_html(
#                     '<img src="{}" style="max-height: 100px; max-width: 100px;" />',
#                     url
#                 )
#         return "No image"
#     preview_thumbnail.short_description = 'Preview'
    
#     def preview_status_display(self, obj):
#         """Display preview generation status with color coding"""
#         if not obj.id:
#             return "-"
        
#         status_colors = {
#             'pending': 'orange',
#             'processing': 'blue',
#             'completed': 'green',
#             'failed': 'red',
#         }
#         color = status_colors.get(obj.preview_status, 'gray')
        
#         html = format_html(
#             '<span style="color: {}; font-weight: bold;">{}</span>',
#             color,
#             obj.get_preview_status_display()
#         )
        
#         if obj.preview_status == 'failed' and obj.preview_error:
#             html += format_html(
#                 '<br/><small style="color: red;">{}</small>',
#                 obj.preview_error[:100]
#             )
        
#         return html
#     preview_status_display.short_description = 'Status'
    
#     def has_add_permission(self, request, obj=None):
#         # Don't allow adding photos through inline (use bulk upload instead)
#         return False
