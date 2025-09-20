from rest_framework import serializers
from .models import Batch, Photo

class PhotoSerializer(serializers.ModelSerializer):
    preview_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Photo
        fields = ['id', 'preview_url', 'created_at']
    
    def get_preview_url(self, obj):
        if obj.preview_image:
            return obj.preview_image.url
        return None

class BatchListSerializer(serializers.ModelSerializer):
    photo_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Batch
        fields = ['id', 'title', 'description', 'price', 'photo_count', 'created_at']
    
    def get_photo_count(self, obj):
        return obj.photos.count()

class BatchDetailSerializer(serializers.ModelSerializer):
    photos = PhotoSerializer(many=True, read_only=True)
    photo_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Batch
        fields = ['id', 'title', 'description', 'price', 'photos', 'photo_count', 'created_at']
    
    def get_photo_count(self, obj):
        return obj.photos.count()
    
