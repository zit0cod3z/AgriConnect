from django.urls import path
from . import views

app_name = 'stories'

urlpatterns = [
    path('', views.StoryFeedView.as_view(), name='feed'),
    path('create/', views.CreateStoryView.as_view(), name='create'),
    path('<int:pk>/like/', views.LikeStoryView.as_view(), name='like'),
]
