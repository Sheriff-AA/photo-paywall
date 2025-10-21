from django.urls import path

from users.api_views import UserListAPIView
from photos.api_views import BatchListAPIView, BatchDetailAPIView
from payments.api_views import CreateCheckoutSessionAPIView, PaymentSuccessAPIView, StripeWebhookAPIView
from downloads.api_views import DownloadTokenAPIView, InitiateDownloadAPIView, DownloadStatusAPIView

app_name = 'apiservice'

urlpatterns = [
    ## USERS ##
    path('users/', UserListAPIView.as_view(), name='user-list'),

    ## DOWNLOADS ##
    path('downloads/token/<str:token>/', DownloadTokenAPIView.as_view(), name='token-detail'),
    # Initiate download (POST to get download URL)
    path('downloads/initiate/<str:token>/', InitiateDownloadAPIView.as_view(), name='initiate-download'),
    # Check download status
    path('downloads/status/<str:token>/', DownloadStatusAPIView.as_view(), name='download-status'),

    ## PAYMENTS ##
    # Create checkout session
    path('payments/checkout/', CreateCheckoutSessionAPIView.as_view(), name='create-checkout'),
    # Get payment success info
    path('payments/success/', PaymentSuccessAPIView.as_view(), name='success'),
    # Stripe webhook
    path('payments/webhook/', StripeWebhookAPIView.as_view(), name='webhook'),


    ## PHOTOS ##
    path('photos/', BatchListAPIView.as_view(), name='batch-list'),
    path('photos/batch/<uuid:pk>/', BatchDetailAPIView.as_view(), name='batch-detail'),
]