from django.urls import path
from . import views

app_name = 'broadcasts'

urlpatterns = [
    path('', views.BroadcastFeedView.as_view(), name='feed'),
    path('create/', views.CreateBroadcastView.as_view(), name='create'),
    path('<int:pk>/interest/', views.BroadcastInterestView.as_view(), name='interest'),
]
