from django.contrib import admin
from .models import Batch, Photo

class PhotoInline(admin.TabularInline):
    model = Photo
    extra = 0
    readonly_fields = ['id', 'preview_image', 'created_at']

@admin.register(Batch)
class BatchAdmin(admin.ModelAdmin):
    list_display = ['title', 'price', 'photo_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['title', 'description']
    readonly_fields = ['id', 'zip_file', 'created_at', 'updated_at']
    inlines = [PhotoInline]
    
    def photo_count(self, obj):
        return obj.photos.count()
    photo_count.short_description = 'Photos'

@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ['id', 'batch', 'created_at']
    list_filter = ['batch', 'created_at']
    readonly_fields = ['id', 'preview_image', 'created_at']