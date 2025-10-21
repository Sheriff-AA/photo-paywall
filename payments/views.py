import stripe
import logging
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View

from photos.models import Batch
from .models import Purchase

logger = logging.getLogger(__name__)
stripe.api_key = settings.STRIPE_SECRET_KEY


class CreateCheckoutView(View):
    """
    Django view that handles checkout form submission
    Creates Stripe session and redirects to Stripe checkout
    """
    template_name = 'payments/checkout.html'
    error_template = 'payments/error.html'
    
    def get(self, request, batch_id=None):
        """
        Display checkout form (optional - if you have a checkout page)
        """
        if batch_id:
            batch = get_object_or_404(Batch, id=batch_id)
            context = {
                'batch': batch,
            }
            return render(request, self.template_name, context)
        return redirect('home')
    
    def post(self, request):
        """
        Handle checkout form submission
        """
        email = request.POST.get('email')
        batch_id = request.POST.get('batch_id')

        logger.info(f"Checkout request received - Email: {email}, Batch ID: {batch_id}")
        
        # Validate input
        if not email or not batch_id:
            return render(request, self.error_template, {
                'error': 'Email and batch ID are required'
            }, status=400)
        
        # Get batch
        try:
            batch = get_object_or_404(Batch, id=batch_id)
        except Exception as e:
            logger.error(f"Batch not found: {batch_id}")
            return render(request, self.error_template, {
                'error': 'Batch not found'
            }, status=404)
        
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
            Purchase.objects.create(
                email=email,
                batch=batch,
                stripe_session_id=checkout_session.id,
                amount=batch.price,
                payment_status='pending'
            )
            
            # Redirect directly to Stripe checkout
            return redirect(checkout_session.url)
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error: {str(e)}")
            return render(request, self.error_template, {
                'error': f'Payment processing error. Please try again.'
            }, status=400)
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return render(request, self.error_template, {
                'error': f'Failed to create checkout session. Please try again.'
            }, status=500)


class PaymentSuccessView(View):
    """
    Display payment success page after Stripe checkout
    """
    template_name = 'payments/success.html'
    error_template = 'payments/error.html'
    
    def get(self, request):
        session_id = request.GET.get('session_id')
        
        if not session_id:
            return render(request, self.error_template, {
                'error': 'No session ID provided'
            }, status=400)
        
        try:
            purchase = Purchase.objects.select_related('batch').get(
                stripe_session_id=session_id
            )
            
            context = {
                'purchase': purchase,
                'batch': purchase.batch,
                'success': True,
                'message': 'Payment completed successfully! Check your email for download instructions.'
            }
            return render(request, self.template_name, context)
            
        except Purchase.DoesNotExist:
            logger.error(f"Purchase not found for session: {session_id}")
            return render(request, self.error_template, {
                'error': 'Purchase not found. Please contact support if you were charged.'
            }, status=404)


class PaymentCancelView(View):
    """
    Display payment cancellation page
    """
    template_name = 'payments/cancel.html'
    
    def get(self, request):
        batch_id = request.GET.get('batch_id')
        
        context = {
            'message': 'Payment was cancelled. You have not been charged.',
        }
        
        if batch_id:
            try:
                batch = Batch.objects.get(id=batch_id)
                context['batch'] = batch
            except Batch.DoesNotExist:
                pass
        
        return render(request, self.template_name, context)


