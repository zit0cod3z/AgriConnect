from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    path('', views.AdminDashboardView.as_view(), name='dashboard'),
    path('audit-log/', views.AuditLogView.as_view(), name='audit_log'),
    path('moderation/', views.ModerationQueueView.as_view(), name='moderation'),
    path('deactivate-listing/<int:pk>/', views.DeactivateListingView.as_view(), name='deactivate_listing'),
    path('remove-review/<int:pk>/', views.RemoveReviewView.as_view(), name='remove_review'),
]
