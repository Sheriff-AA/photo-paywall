from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string

from payments.models import DownloadToken

def send_download_email(purchase):
    """Send download email to customer"""
    try:
        token = purchase.download_token
    except DownloadToken.DoesNotExist:
        return False
    
    download_url = f"{settings.SITE_URL}/downloads/{token.token}/?download=1"
    
    subject = f"Your photos are ready for download - {purchase.batch.title}"
    
    # Plain text message
    message = f"""
    Hi there!

    Thank you for your purchase of "{purchase.batch.title}".
    
    Your photos are now ready for download. Please use the link below:
    
    {download_url}
    
    This link will expire in 24 hours and can be used up to 3 times.
    
    If you have any issues, please contact us.
    
    Best regards,
    Your Photo Team
    """
    
    # HTML message (optional)
    html_message = f"""
    <h2>Your photos are ready!</h2>
    
    <p>Thank you for your purchase of "<strong>{purchase.batch.title}</strong>".</p>
    
    <p>Your photos are now ready for download:</p>
    
    <p><a href="{download_url}" style="background: #007cba; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Download Photos</a></p>
    
    <p><small>This link will expire in 24 hours and can be used up to 3 times.</small></p>
    
    <p>If you have any issues, please contact us.</p>
    
    <p>Best regards,<br>Your Photo Team</p>
    """
    
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[purchase.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False
    

