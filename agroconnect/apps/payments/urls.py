from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('initiate/<int:order_id>/', views.InitiatePaymentView.as_view(), name='initiate'),
    path('callback/', views.PaystackCallbackView.as_view(), name='callback'),
    path('webhook/', views.PaystackWebhookView.as_view(), name='webhook'),
]
