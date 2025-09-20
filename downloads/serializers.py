from rest_framework import serializers
from .models import DownloadToken

class DownloadTokenSerializer(serializers.ModelSerializer):
    is_valid = serializers.SerializerMethodField()
    batch_title = serializers.CharField(source='purchase.batch.title', read_only=True)
    
    class Meta:
        model = DownloadToken
        fields = ['token', 'expires_at', 'download_count', 'max_downloads', 'is_valid', 'batch_title']
    
    def get_is_valid(self, obj):
        return obj.is_valid()
    
