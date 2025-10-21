from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    # Checkout page and form submission
    path('checkout/', views.CreateCheckoutView.as_view(), name='checkout'),
    path('checkout/<uuid:batch_id>/', views.CreateCheckoutView.as_view(), name='checkout-batch'),
    
    # Success page (after Stripe redirect)
    path('success/', views.PaymentSuccessView.as_view(), name='success'),
    
    # Cancel page (if user cancels on Stripe)
    path('cancel/', views.PaymentCancelView.as_view(), name='cancel'),
]

