from django.urls import path
from . import views

app_name = 'photos'

urlpatterns = [
    path('', views.BatchListView.as_view(), name='batch-list'),
    path('batch/<uuid:pk>/', views.BatchDetailView.as_view(), name='batch-detail'),
]