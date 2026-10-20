from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('', views.NotificationListView.as_view(), name='list'),
    path('mark-read/<int:pk>/', views.MarkReadView.as_view(), name='mark_read'),
    path('unread-count/', views.unread_count_api, name='unread_count'),
]
