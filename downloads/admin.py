from django.contrib import admin
from .models import DownloadToken

@admin.register(DownloadToken)
class DownloadTokenAdmin(admin.ModelAdmin):
    list_display = ['token', 'purchase_email', 'batch_title', 'download_count', 'max_downloads', 'expires_at', 'is_valid_status']
    list_filter = ['expires_at', 'download_count', 'created_at']
    search_fields = ['purchase__email', 'purchase__batch__title', 'token']
    readonly_fields = ['token', 'created_at']
    
    def purchase_email(self, obj):
        return obj.purchase.email
    purchase_email.short_description = 'Email'
    
    def batch_title(self, obj):
        return obj.purchase.batch.title
    batch_title.short_description = 'Batch'
    
    def is_valid_status(self, obj):
        return obj.is_valid()
    is_valid_status.boolean = True
    is_valid_status.short_description = 'Valid'

