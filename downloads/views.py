from time import timezone
from django.http import HttpResponse, Http404
from django.shortcuts import redirect
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from cloudinary import CloudinaryImage


from .models import DownloadToken
from .serializers import DownloadTokenSerializer

class DownloadView(generics.RetrieveAPIView):
    queryset = DownloadToken.objects.all()
    serializer_class = DownloadTokenSerializer
    permission_classes = [AllowAny]
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = 'downloads/download.html'
    lookup_field = 'token'
    
    def get(self, request, *args, **kwargs):
        try:
            token = self.get_object()
        except Http404:
            return Response({'error': 'Invalid download token'}, status=status.HTTP_404_NOT_FOUND)
        
        if not token.is_valid():
            return Response({
                'error': 'Download token has expired or exceeded maximum downloads',
                'token': token
            }, status=status.HTTP_410_GONE, template_name='downloads/expired.html')
        
        # If it's a direct download request (e.g., from email link with ?download=1)
        if request.GET.get('download') == '1':
            return self.initiate_download(token)
        
        # Otherwise show the download page
        return Response({'token': token})
    
    def initiate_download(self, token):
        """Initiate the actual download"""
        if not token.purchase.batch.zip_file:
            return Response({'error': 'Download file not available'}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            # Get download URL from Cloudinary
            zip_image = CloudinaryImage(token.purchase.batch.zip_file)
            download_url = zip_image.build_url(
                resource_type='raw',
                sign_url=True,
                expires_at=int(timezone.now().timestamp()) + 300  # 5 minutes
            )
            
            # Increment download count
            token.increment_download()
            
            # Redirect to Cloudinary download URL
            return redirect(download_url)
            
        except Exception as e:
            return Response({'error': 'Download temporarily unavailable'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

class DownloadStatusView(generics.RetrieveAPIView):
    queryset = DownloadToken.objects.all()
    serializer_class = DownloadTokenSerializer
    permission_classes = [AllowAny]
    lookup_field = 'token'