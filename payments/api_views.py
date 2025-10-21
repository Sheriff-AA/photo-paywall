import stripe
import logging
from django.conf import settings
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

from photos.models import Batch
from .models import Purchase
from .serializers import CheckoutSerializer, PurchaseSerializer
from downloads.utils import send_download_email

logger = logging.getLogger(__name__)
stripe.api_key = settings.STRIPE_SECRET_KEY


class CreateCheckoutSessionAPIView(APIView):
    """
    API endpoint to create a Stripe checkout session
    Returns checkout URL and session ID in JSON
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = CheckoutSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                serializer.errors, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        email = serializer.validated_data['email']
        batch_id = serializer.validated_data['batch_id']
        
        logger.info(f"API Checkout request - Email: {email}, Batch ID: {batch_id}")
        
        try:
            batch = Batch.objects.get(id=batch_id)
        except Batch.DoesNotExist:
            return Response(
                {'error': 'Batch not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            # Create Stripe checkout session
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': batch.title,
                            'description': batch.description or f'Photos from {batch.title}',
                        },
                        'unit_amount': int(batch.price * 100),  # Convert to cents
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=f"{settings.SITE_URL}/payments/success/?session_id={{CHECKOUT_SESSION_ID}}",
                cancel_url=f"{settings.SITE_URL}/photos/batch/{batch_id}/",
                customer_email=email,
                metadata={
                    'batch_id': str(batch_id),
                    'customer_email': email,
                }
            )
            
            logger.info(f"Stripe session created successfully: {checkout_session.id}")
            
            # Create purchase record
            purchase = Purchase.objects.create(
                email=email,
                batch=batch,
                stripe_session_id=checkout_session.id,
                amount=batch.price,
                payment_status='pending'
            )
            
            return Response({
                'success': True,
                'checkout_url': checkout_session.url,
                'session_id': checkout_session.id,
                'purchase_id': purchase.id,
                'amount': str(batch.price),
                'batch_title': batch.title
            }, status=status.HTTP_201_CREATED)
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error: {str(e)}")
            return Response(
                {'error': f'Payment processing error: {str(e)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Unexpected error creating checkout: {str(e)}")
            return Response(
                {'error': 'Failed to create checkout session'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PaymentSuccessAPIView(APIView):
    """
    API endpoint to retrieve successful payment information
    Returns purchase details in JSON
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        session_id = request.query_params.get('session_id')
        
        if not session_id:
            return Response(
                {'error': 'No session ID provided'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            purchase = Purchase.objects.get(stripe_session_id=session_id)
            serializer = PurchaseSerializer(purchase)
            
            return Response({
                'success': True,
                'purchase': serializer.data,
                'message': 'Payment completed successfully'
            }, status=status.HTTP_200_OK)
            
        except Purchase.DoesNotExist:
            return Response(
                {'error': 'Purchase not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )


@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhookAPIView(APIView):
    """
    Stripe webhook endpoint
    Handles payment events from Stripe
    Already API-only, no changes needed
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except ValueError as e:
            logger.error(f"Invalid webhook payload: {str(e)}")
            return HttpResponse(status=400)
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Invalid webhook signature: {str(e)}")
            return HttpResponse(status=400)
        
        # Handle checkout session completed
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            
            logger.info(f"Checkout completed for session: {session['id']}")
            
            try:
                purchase = Purchase.objects.get(stripe_session_id=session['id'])
                purchase.stripe_payment_intent_id = session.get('payment_intent', '')
                purchase.mark_completed()
                
                logger.info(f"Purchase {purchase.id} marked as completed")
                
                # Send download email
                send_download_email(purchase)
                logger.info(f"Download email sent for purchase {purchase.id}")
                
            except Purchase.DoesNotExist:
                logger.error(f"Purchase not found for session: {session['id']}")
        
        return HttpResponse(status=200)


