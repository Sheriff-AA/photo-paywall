from django.urls import path
from . import views

app_name = 'downloads'

urlpatterns = [
    path('<str:token>/', views.DownloadPageView.as_view(), name='download-page'),
]

