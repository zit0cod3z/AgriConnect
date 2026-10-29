from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('',                                    views.OrderListView.as_view(),              name='list'),
    path('farmer-inbox/',                       views.FarmerInboxView.as_view(),            name='farmer_inbox'),
    path('my-ratings/',                         views.MyRatingsView.as_view(),              name='my_ratings'),
    path('farmer-rep/<str:farmer_phone>/',      views.FarmerReputationView.as_view(),       name='farmer_reputation'),
    path('<int:pk>/',                           views.OrderDetailView.as_view(),            name='detail'),
    path('<int:pk>/confirm/',                   views.ConfirmOrderView.as_view(),           name='confirm'),
    path('<int:pk>/payment-choice/',            views.PaymentChoiceView.as_view(),          name='payment_choice'),
    path('<int:pk>/provide-address/',           views.ProvideAddressView.as_view(),         name='provide_address'),
    path('<int:pk>/cancel/',                    views.CancelOrderView.as_view(),            name='cancel'),
    path('<int:pk>/delivered/',                 views.MarkDeliveredView.as_view(),          name='delivered'),
    path('<int:pk>/rate/',                      views.RateOrderView.as_view(),              name='rate'),
    path('<int:pk>/farmer-accept/',             views.FarmerAcceptOrderView.as_view(),      name='farmer_accept'),
    path('<int:pk>/farmer-reject/',             views.FarmerRejectOrderView.as_view(),      name='farmer_reject'),
    path('<int:pk>/farmer-ready/',              views.FarmerMarkReadyView.as_view(),        name='farmer_ready'),
    path('<int:pk>/farmer-in-transit/',         views.FarmerMarkInTransitView.as_view(),    name='farmer_in_transit'),
    path('<int:pk>/farmer-set-pickup/',         views.FarmerSetPickupAddressView.as_view(), name='farmer_set_pickup'),
]
