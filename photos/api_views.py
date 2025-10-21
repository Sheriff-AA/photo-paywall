from rest_framework import generics
from rest_framework.permissions import AllowAny
from .models import Batch
from .serializers import BatchListSerializer, BatchDetailSerializer


class BatchListAPIView(generics.ListAPIView):
    """
    API endpoint to list all batches
    Returns JSON only
    """
    queryset = Batch.objects.all()
    serializer_class = BatchListSerializer
    permission_classes = [AllowAny]


class BatchDetailAPIView(generics.RetrieveAPIView):
    """
    API endpoint to retrieve a single batch
    Returns JSON only
    """
    queryset = Batch.objects.all()
    serializer_class = BatchDetailSerializer
    permission_classes = [AllowAny]

