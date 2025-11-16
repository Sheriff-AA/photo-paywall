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
    
    download_url = f"{settings.SITE_URL}/downloads/{token.token}"
    
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
    
    <p>Best regards,<br>DotNetLenses</p>
    """

    html_message = f"""
    <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 40px 20px; color: #333;">
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 12px 12px 0 0; text-align: center;">
            <h2 style="color: white; margin: 0; font-size: 28px; font-weight: 600;">Your photos are ready! 📸</h2>
        </div>
        
        <div style="background: #f8f9fa; padding: 40px 30px; border-radius: 0 0 12px 12px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
            
            <p style="font-size: 16px; line-height: 1.6; margin-bottom: 20px;">
                Thank you for your purchase of "<strong style="color: #667eea;">{purchase.batch.title}</strong>".
            </p>
            
            <p style="font-size: 16px; line-height: 1.6; margin-bottom: 30px;">
                Your photos are now ready for download:
            </p>
            
            <div style="text-align: center; margin: 35px 0;">
                <a href="{download_url}" style="display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 14px 32px; text-decoration: none; border-radius: 8px; font-weight: 600; font-size: 16px; box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4); transition: transform 0.2s;">Download Photos</a>
            </div>
            
            <div style="background: #fff3cd; border-left: 4px solid #ffc107; padding: 12px 16px; border-radius: 4px; margin: 30px 0;">
                <p style="margin: 0; font-size: 14px; color: #856404;">
                    ⏱️ <strong>Note:</strong> This link will expire in 24 hours and can be used up to 3 times.
                </p>
            </div>
            
            <p style="font-size: 16px; line-height: 1.6; margin-top: 30px; color: #666;">
                If you have any issues, please don't hesitate to contact us.
            </p>
            
            <div style="margin-top: 40px; padding-top: 30px; border-top: 2px solid #e9ecef;">
                <p style="margin: 0; font-size: 16px; color: #666;">
                    Best regards,<br>
                    <strong style="color: #667eea; font-size: 18px;">DotNetLenses</strong>
                </p>
            </div> 
        </div>         
    </div>
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
    

