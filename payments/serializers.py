from rest_framework import serializers
from .models import Purchase

class PurchaseSerializer(serializers.ModelSerializer):
    batch_title = serializers.CharField(source='batch.title', read_only=True)
    
    class Meta:
        model = Purchase
        fields = ['id', 'email', 'batch', 'batch_title', 'payment_status', 'amount', 'created_at']
        read_only_fields = ['id', 'payment_status', 'created_at']

class CheckoutSerializer(serializers.Serializer):
    email = serializers.EmailField()
    batch_id = serializers.UUIDField()