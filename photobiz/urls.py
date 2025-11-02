"""
URL configuration for photobiz project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

from users.views import SubmitContactView

urlpatterns = [
    path('jide-admin/', admin.site.urls),
   
    path('', TemplateView.as_view(template_name='base/home.html'), name='home'),
    path('about/', TemplateView.as_view(template_name='base/about.html'), name='about'),
    path('contact/', TemplateView.as_view(template_name='base/contact.html'), name='contact'),
    path('contact/submit/', SubmitContactView.as_view(), name='submit_contact'),
    # path('contact/submit/', views.submit_contact, name='submit_contact'),


    path('api/', include('apiservice.urls'), name='apiservice'),
    path('photos/', include('photos.urls'), name='photos'),
    path('payments/', include('payments.urls'), name='payments'),
    path('downloads/', include('downloads.urls'), name='downloads'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

