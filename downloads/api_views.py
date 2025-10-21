from django.utils import timezone
from django.http import HttpResponse, Http404
from django.shortcuts import redirect
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from cloudinary import CloudinaryImage


from payments.models import DownloadToken
from .serializers import DownloadTokenSerializer


class DownloadTokenAPIView(generics.RetrieveAPIView):
    """
    API endpoint to retrieve download token information
    Returns JSON only
    """
    queryset = DownloadToken.objects.all()
    serializer_class = DownloadTokenSerializer
    permission_classes = [AllowAny]
    lookup_field = 'token'
    
    def get(self, request, *args, **kwargs):
        try:
            token = self.get_object()
        except Http404:
            return Response(
                {'error': 'Invalid download token'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if token is valid
        if not token.is_valid():
            return Response({
                'error': 'Download token has expired or exceeded maximum downloads',
                'is_valid': False,
                'token_data': self.get_serializer(token).data
            }, status=status.HTTP_410_GONE)
        
        # Return token data
        serializer = self.get_serializer(token)
        return Response({
            'is_valid': True,
            'token_data': serializer.data
        }, status=status.HTTP_200_OK)


# class InitiateDownloadAPIView(APIView):
#     """
#     API endpoint to initiate a download and get the download URL
#     Returns the signed Cloudinary URL
#     """
#     permission_classes = [AllowAny]
    
#     def post(self, request, token):
#         """POST to initiate download and get URL"""
#         try:
#             download_token = DownloadToken.objects.get(token=token)
#         except DownloadToken.DoesNotExist:
#             return Response(
#                 {'error': 'Invalid download token'}, 
#                 status=status.HTTP_404_NOT_FOUND
#             )
        
#         # Validate token
#         if not download_token.is_valid():
#             return Response({
#                 'error': 'Download token has expired or exceeded maximum downloads',
#                 'is_valid': False
#             }, status=status.HTTP_410_GONE)
        
#         # Check if file exists
#         if not download_token.purchase.batch.zip_file:
#             print('non exist')
#             return Response(
#                 {'error': 'Download file not available'}, 
#                 status=status.HTTP_404_NOT_FOUND
#             )
        
#         try:
#             # Get download URL from Cloudinary
#             zip_image = CloudinaryImage(download_token.purchase.batch.zip_file)
#             download_url = zip_image.build_url(
#                 resource_type='raw',
#                 sign_url=True,
#                 expires_at=int(timezone.now().timestamp()) + 300  # 5 minutes
#             )
            
#             # Increment download count
#             download_token.increment_download()
            
#             # Return the download URL
#             return Response({
#                 'success': True,
#                 'download_url': download_url,
#                 'expires_in': 300,  # seconds
#                 'downloads_remaining': download_token.max_downloads - download_token.download_count
#             }, status=status.HTTP_200_OK)
            
#         except Exception as e:
#             return Response(
#                 {'error': 'Download temporarily unavailable', 'detail': str(e)}, 
#                 status=status.HTTP_503_SERVICE_UNAVAILABLE
#             )

class InitiateDownloadAPIView(APIView):    
    permission_classes = [AllowAny]
    
    def post(self, request, token):
        """POST to initiate download and get URL"""
        try:
            download_token = DownloadToken.objects.get(token=token)
        except DownloadToken.DoesNotExist:
            return Response(
                {'error': 'Invalid download token'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Validate token
        if not download_token.is_valid():
            return Response({
                'error': 'Download token has expired or exceeded maximum downloads',
                'is_valid': False
            }, status=status.HTTP_410_GONE)
        
        # Check if file exists
        if not download_token.purchase.batch.zip_file:
            return Response(
                {'error': 'Download file not available'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            # Get the public ID from the batch
            public_id = str(download_token.purchase.batch.zip_file)
            
            if not public_id.endswith('.zip'):
                public_id_with_ext = f"{public_id}.zip"
            else:
                public_id_with_ext = public_id
            
            zip_image = CloudinaryImage(public_id_with_ext)
            print(zip_image)
            print(public_id_with_ext)
            # cloudinary.utils.cloudinary_url(zip_image, resource_type = "raw")
            download_url = zip_image.build_url(
                resource_type='raw',
                # format='zip',
                attachment=True,  
                sign_url=True,
                expires_at=int(timezone.now().timestamp()) + 300  # 5 minutes
            )
        
            # Increment download count AFTER successful URL generation
            download_token.increment_download()
            
            # Return the download URL
            return Response({
                'success': True,
                'download_url': download_url,
                'expires_in': 300,  # seconds
                'downloads_remaining': download_token.max_downloads - download_token.download_count
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            # CHANGE 4: Better error logging for debugging
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Download initiation failed: {str(e)}", exc_info=True)
            print('Download initiation failed:')

            return Response(
                {'error': 'Download temporarily unavailable', 'detail': str(e)}, 
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )


class DownloadStatusAPIView(generics.RetrieveAPIView):
    """
    API endpoint to check download status
    Already API-only, no changes needed
    """
    queryset = DownloadToken.objects.all()
    serializer_class = DownloadTokenSerializer
    permission_classes = [AllowAny]
    lookup_field = 'token'


