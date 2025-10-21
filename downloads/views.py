from django.shortcuts import render, redirect
from django.http import Http404
from django.views import View
from django.conf import settings
import requests
from payments.models import DownloadToken


class DownloadPageView(View):
    """
    Renders the download page for a given token
    Consumes the API to get token data
    """
    template_name = 'downloads/download.html'
    expired_template_name = 'downloads/expired.html'
    
    def get(self, request, token):
        # Check if this is a direct download request
        if request.GET.get('download') == '1':
            return self.handle_direct_download(request, token)
        
        # Otherwise, show the download page
        try:
            download_token = DownloadToken.objects.get(token=token)
        except DownloadToken.DoesNotExist:
            raise Http404("Invalid download token")
        
        # Check if token is valid
        if not download_token.is_valid():
            return render(request, self.expired_template_name, {
                'token': download_token,
                'error': 'Download token has expired or exceeded maximum downloads'
            }, status=410)
        
        # Render the download page
        context = {
            'token': download_token,
            'purchase': download_token.purchase,
            'batch': download_token.purchase.batch,
        }
        return render(request, self.template_name, context)
    
    # def handle_direct_download(self, request, token):
    #     """
    #     Handle direct download links (e.g., from email)
    #     This initiates the download immediately
    #     """
    #     try:
    #         download_token = DownloadToken.objects.get(token=token)
    #     except DownloadToken.DoesNotExist:
    #         raise Http404("Invalid download token")
        
    #     # Validate token
    #     if not download_token.is_valid():
    #         return render(request, self.expired_template_name, {
    #             'token': download_token,
    #             'error': 'Download token has expired or exceeded maximum downloads'
    #         }, status=410)
        
    #     # Check if file exists
    #     if not download_token.purchase.batch.zip_file:
    #         return render(request, self.template_name, {
    #             'token': download_token,
    #             'error': 'Download file not available'
    #         }, status=404)
        
    #     try:
    #         from cloudinary import CloudinaryImage
    #         from django.utils import timezone
            
    #         # Get download URL from Cloudinary
    #         zip_image = CloudinaryImage(download_token.purchase.batch.zip_file)
    #         download_url = zip_image.build_url(
    #             resource_type='raw',
    #             sign_url=True,
    #             expires_at=int(timezone.now().timestamp()) + 300
    #         )
            
    #         # Increment download count
    #         download_token.increment_download()
            
    #         # Redirect to Cloudinary download URL
    #         return redirect(download_url)
            
    #     except Exception as e:
    #         return render(request, self.template_name, {
    #             'token': download_token,
    #             'error': 'Download temporarily unavailable'
    #         }, status=503)

    def handle_direct_download(self, request, token):
        """
        Handle direct download links (e.g., from email)
        This calls the API endpoint to initiate the download
        """
        try:
            download_token = DownloadToken.objects.get(token=token)
        except DownloadToken.DoesNotExist:
            raise Http404("Invalid download token")
        
        # Validate token exists and file exists before calling API
        if not download_token.is_valid():
            return render(request, self.expired_template_name, {
                'token': download_token,
                'error': 'Download token has expired or exceeded maximum downloads'
            }, status=410)
        
        if not download_token.purchase.batch.zip_file:
            return render(request, self.template_name, {
                'token': download_token,
                'error': 'Download file not available'
            }, status=404)
        
        try:
            # Build the API endpoint URL
            api_url = request.build_absolute_uri(f'/api/downloads/initiate/{token}/')
            
            # Make POST request to the API
            response = requests.post(api_url)
            
            # Check if API call was successful
            if response.status_code == 200:
                data = response.json()
                download_url = data.get('download_url')
                
                if download_url:
                    # Redirect to the Cloudinary download URL
                    return redirect(download_url)
                else:
                    return render(request, self.template_name, {
                        'token': download_token,
                        'error': 'Download URL not generated'
                    }, status=500)
            
            elif response.status_code == 410:
                # Token expired or max downloads exceeded
                return render(request, self.expired_template_name, {
                    'token': download_token,
                    'error': 'Download token has expired or exceeded maximum downloads'
                }, status=410)
            
            elif response.status_code == 404:
                # Invalid token or file not found
                return render(request, self.template_name, {
                    'token': download_token,
                    'error': 'Download file not available'
                }, status=404)
            
            else:
                return render(request, self.template_name, {
                    'token': download_token,
                    'error': 'Download temporarily unavailable'
                }, status=503)
        
        except requests.RequestException as e:
            # Network error calling the API
            return render(request, self.template_name, {
                'token': download_token,
                'error': 'Download temporarily unavailable',
                'detail': str(e)
            }, status=503)
        except Exception as e:
            # Unexpected error
            return render(request, self.template_name, {
                'token': download_token,
                'error': 'Download temporarily unavailable',
                'detail': str(e)
            }, status=503)
