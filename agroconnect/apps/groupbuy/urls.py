from django.urls import path
from . import views

app_name = 'groupbuy'

urlpatterns = [
    path('join/<int:listing_pk>/', views.JoinGroupBuyView.as_view(), name='join'),
    path('leave/<int:listing_pk>/', views.LeaveGroupBuyView.as_view(), name='leave'),
]
