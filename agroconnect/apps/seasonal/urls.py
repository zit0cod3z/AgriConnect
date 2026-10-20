from django.urls import path
from . import views

app_name = 'seasonal'

urlpatterns = [
    path('guide/', views.SeasonalGuideView.as_view(), name='guide'),
    path('calendar/', views.AvailabilityCalendarView.as_view(), name='calendar'),
]
