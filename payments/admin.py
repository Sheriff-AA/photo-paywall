from django.contrib import admin
from .models import Purchase

@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ['id', 'email', 'batch', 'payment_status', 'amount', 'created_at']
    list_filter = ['payment_status', 'created_at', 'batch']
    search_fields = ['email', 'batch__title', 'stripe_session_id']
    readonly_fields = ['id', 'stripe_session_id', 'stripe_payment_intent_id', 'created_at', 'completed_at']

