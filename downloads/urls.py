from django.urls import path
from . import views

app_name = 'downloads'

urlpatterns = [
    path('<uuid:token>/', views.DownloadView.as_view(), name='download'),
    path('status/<uuid:token>/', views.DownloadStatusView.as_view(), name='status'),
]
