from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.views import View
from .models import GroupBuy
from .services import join_group_buy, leave_group_buy
from apps.listings.models import Listing


class JoinGroupBuyView(LoginRequiredMixin, View):
    def post(self, request, listing_pk):
        listing = get_object_or_404(Listing, pk=listing_pk, is_active=True)
        try:
            group_buy = listing.group_buy
        except GroupBuy.DoesNotExist:
            messages.error(request, 'No group buy available for this listing.')
            return redirect('listings:detail', ref_code=listing.reference_code)
        try:
            quantity = float(request.POST.get('quantity', 0))
            join_group_buy(group_buy, request.user, quantity)
            messages.success(request, f'Joined the group buy! You contributed {quantity} {listing.unit}.')
        except Exception as e:
            messages.error(request, str(e))
        return redirect('listings:detail', ref_code=listing.reference_code)


class LeaveGroupBuyView(LoginRequiredMixin, View):
    def post(self, request, listing_pk):
        listing = get_object_or_404(Listing, pk=listing_pk)
        try:
            group_buy = listing.group_buy
            leave_group_buy(group_buy, request.user)
            messages.success(request, 'You have left the group buy.')
        except Exception as e:
            messages.error(request, str(e))
        return redirect('listings:detail', ref_code=listing.reference_code)
