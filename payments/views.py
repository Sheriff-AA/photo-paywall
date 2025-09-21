import stripe
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from rest_framework.permissions import AllowAny


from photos.models import Batch
from .models import Purchase
from .serializers import CheckoutSerializer, PurchaseSerializer
from downloads.utils import send_download_email

stripe.api_key = settings.STRIPE_SECRET_KEY

class CreateCheckoutSessionView(APIView):
    permission_classes = [AllowAny]
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    
    def post(self, request):
        serializer = CheckoutSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        email = serializer.validated_data['email']
        batch_id = serializer.validated_data['batch_id']
        
        try:
            batch = Batch.objects.get(id=batch_id)
        except Batch.DoesNotExist:
            return Response({'error': 'Batch not found'}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            # Create Stripe checkout session
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': batch.title,
                            'description': batch.description,
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
            
            # Create purchase record
            Purchase.objects.create(
                email=email,
                batch=batch,
                stripe_session_id=checkout_session.id,
                amount=batch.price
            )
            
            return Response({
                'checkout_url': checkout_session.url,
                'session_id': checkout_session.id
            })
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class PaymentSuccessView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = 'payments/success.html'
    
    def get(self, request):
        session_id = request.GET.get('session_id')
        if not session_id:
            return Response({'error': 'No session ID provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            purchase = Purchase.objects.get(stripe_session_id=session_id)
            return Response({'purchase': purchase})
        except Purchase.DoesNotExist:
            return Response({'error': 'Purchase not found'}, status=status.HTTP_404_NOT_FOUND)

@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhookView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except ValueError:
            return HttpResponse(status=400)
        except stripe.error.SignatureVerificationError:
            return HttpResponse(status=400)
        
        # Handle checkout session completed
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            
            try:
                purchase = Purchase.objects.get(stripe_session_id=session['id'])
                purchase.stripe_payment_intent_id = session.get('payment_intent', '')
                purchase.mark_completed()
                
                # Send download email
                send_download_email(purchase)
                
            except Purchase.DoesNotExist:
                pass
        
        return HttpResponse(status=200)
    
