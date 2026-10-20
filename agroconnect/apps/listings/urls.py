from django.urls import path
from . import views

app_name = 'listings'

urlpatterns = [
    path('', views.CatalogueView.as_view(), name='catalogue'),
    path('listings/new/', views.CreateListingView.as_view(), name='create'),
    path('listings/search/', views.SearchView.as_view(), name='search'),
    path('listings/<str:ref_code>/', views.ListingDetailView.as_view(), name='detail'),
    path('listings/<str:ref_code>/edit/', views.EditListingView.as_view(), name='edit'),
    path('listings/<str:ref_code>/delete/', views.DeleteListingView.as_view(), name='delete'),
]
