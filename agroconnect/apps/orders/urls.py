from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('', views.OrderListView.as_view(), name='list'),
    path('<int:pk>/', views.OrderDetailView.as_view(), name='detail'),
    path('<int:pk>/confirm/', views.ConfirmOrderView.as_view(), name='confirm'),
    path('<int:pk>/cancel/', views.CancelOrderView.as_view(), name='cancel'),
    path('<int:pk>/delivered/', views.MarkDeliveredView.as_view(), name='delivered'),
    path('<int:pk>/rate/', views.RateOrderView.as_view(), name='rate'),
]
