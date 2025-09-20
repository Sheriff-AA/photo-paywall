from rest_framework import generics
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from rest_framework.permissions import AllowAny
from .models import Batch
from .serializers import BatchListSerializer, BatchDetailSerializer

class BatchListView(generics.ListAPIView):
    queryset = Batch.objects.all()
    serializer_class = BatchListSerializer
    permission_classes = [AllowAny]
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = 'photos/batch_list.html'
    
    def get_context_data(self, **kwargs):
        return {'batches': self.get_queryset()}

class BatchDetailView(generics.RetrieveAPIView):
    queryset = Batch.objects.all()
    serializer_class = BatchDetailSerializer
    permission_classes = [AllowAny]
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = 'photos/batch_detail.html'
    
    def get_context_data(self, **kwargs):
        return {'batch': self.get_object()}
    
