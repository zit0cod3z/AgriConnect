from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views import View
from .models import AdminAuditLog
from .services import log_admin_action, get_dashboard_stats
from apps.listings.models import Listing, FreshnessScore
from apps.listings.services import deactivate_listing


class StaffRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_staff:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class AdminDashboardView(StaffRequiredMixin, View):
    def get(self, request):
        stats = get_dashboard_stats()
        return render(request, 'admin_panel/dashboard.html', {'stats': stats})


class AuditLogView(StaffRequiredMixin, View):
    def get(self, request):
        from django.core.paginator import Paginator
        logs = AdminAuditLog.objects.select_related('admin_user').all()
        paginator = Paginator(logs, 30)
        page = paginator.get_page(request.GET.get('page', 1))
        return render(request, 'admin_panel/audit_log.html', {'logs': page})


class ModerationQueueView(StaffRequiredMixin, View):
    def get(self, request):
        flagged_listings = Listing.objects.filter(is_flagged=True, is_active=True)
        flagged_reviews = FreshnessScore.objects.filter(is_flagged=True)
        return render(request, 'admin_panel/moderation.html', {
            'flagged_listings': flagged_listings,
            'flagged_reviews': flagged_reviews,
        })


class DeactivateListingView(StaffRequiredMixin, View):
    def post(self, request, pk):
        listing = get_object_or_404(Listing, pk=pk)
        deactivate_listing(listing)
        log_admin_action(
            admin_user=request.user,
            entity_type='Listing',
            entity_id=str(pk),
            action='deactivate',
            detail=f'Deactivated listing: {listing.produce_name}',
        )
        messages.success(request, f'Listing "{listing.produce_name}" deactivated.')
        return redirect('admin_panel:moderation')


class RemoveReviewView(StaffRequiredMixin, View):
    def post(self, request, pk):
        review = get_object_or_404(FreshnessScore, pk=pk)
        log_admin_action(
            admin_user=request.user,
            entity_type='FreshnessScore',
            entity_id=str(pk),
            action='delete_review',
            detail=f'Removed review for farmer {review.farmer_phone}',
        )
        review.delete()
        messages.success(request, 'Review removed.')
        return redirect('admin_panel:moderation')
