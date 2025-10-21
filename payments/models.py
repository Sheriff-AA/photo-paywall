import uuid
from django.db import models
from django.utils import timezone
from photos.models import Batch
from datetime import timedelta


class Purchase(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField()
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name='purchases')
    stripe_session_id = models.CharField(max_length=200, unique=True)
    stripe_payment_intent_id = models.CharField(max_length=200, blank=True)
    payment_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Purchase {self.id} - {self.email} - {self.batch.title}"
    
    def mark_completed(self):
        """Mark purchase as completed and create download token"""
        self.payment_status = 'completed'
        self.completed_at = timezone.now()
        self.save()
        
        # Create download token
        DownloadToken.objects.create(purchase=self)


class DownloadToken(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    purchase = models.OneToOneField(Purchase, on_delete=models.CASCADE, related_name='download_token')
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    expires_at = models.DateTimeField()
    download_count = models.PositiveIntegerField(default=0)
    max_downloads = models.PositiveIntegerField(default=3)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Download Token for {self.purchase.email} - {self.purchase.batch.title}"
    
    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(hours=24)
        super().save(*args, **kwargs)
    
    def is_valid(self):
        """Check if token is still valid for download"""
        return (
            timezone.now() < self.expires_at and 
            self.download_count < self.max_downloads
        )
    
    def increment_download(self):
        """Increment download count"""
        self.download_count += 1
        self.save(update_fields=['download_count'])


