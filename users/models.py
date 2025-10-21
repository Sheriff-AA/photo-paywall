from django.contrib.auth.models import AbstractUser
from django.db import models

import helpers

helpers.cloudinary_init()

class CustomUser(AbstractUser):
    """Extended user model for future scalability"""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.username


class Contact(models.Model):
    SUBJECT_CHOICES = [
        ('general', 'General Inquiry'),
        ('booking', 'Event Booking'),
        ('pricing', 'Pricing Information'),
        ('download', 'Download Issues'),
        ('technical', 'Technical Support'),
        ('other', 'Other'),
    ]
    
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, null=True)
    subject = models.CharField(max_length=50, choices=SUBJECT_CHOICES)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.subject}"
    
    class Meta:
        ordering = ['-created_at']


