from django.urls import path
from . import views

app_name = 'negotiations'

urlpatterns = [
    path('offer/<str:ref_code>/', views.SubmitOfferView.as_view(), name='submit_offer'),
    path('counter/<int:offer_id>/', views.CounterOfferView.as_view(), name='counter_offer'),
    path('accept/<int:offer_id>/', views.AcceptOfferView.as_view(), name='accept_offer'),
    path('accept-counter/<int:counter_offer_id>/', views.AcceptCounterOfferView.as_view(), name='accept_counter_offer'),
    path('reject/<int:offer_id>/', views.RejectOfferView.as_view(), name='reject_offer'),
    path('thread/<str:ref_code>/', views.NegotiationThreadView.as_view(), name='thread'),
]
