from django.urls import path
from . import views

app_name = 'delivery'

urlpatterns = [
    path('<int:order_id>/setup/',    views.DeliverySetupView.as_view(),           name='setup'),
    path('<int:order_id>/track/',    views.DeliveryTrackView.as_view(),           name='track'),
    path('<int:order_id>/update/',   views.DeliveryLocationUpdateView.as_view(),  name='update'),
    path('<int:order_id>/poll/',     views.DeliveryLocationPollView.as_view(),    name='poll'),
    path('<int:order_id>/complete/', views.DeliveryCompleteView.as_view(),        name='complete'),
]
