from rest_framework import generics, permissions
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from django.contrib.auth import get_user_model
from .serializers import UserSerializer

User = get_user_model()

class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = 'users/user_list.html'

