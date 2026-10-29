from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views import View
from .models import Offer, CounterOffer
from .services import (
    submit_offer, submit_counter_offer, accept_offer,
    accept_counter_offer, reject_offer, get_negotiation_thread,
)
from apps.listings.models import Listing
from apps.listings.decorators import rate_limit


class SubmitOfferView(LoginRequiredMixin, View):
    @rate_limit('submit_offer', 20, 3600)
    def post(self, request, ref_code):
        listing = get_object_or_404(Listing, reference_code=ref_code, is_active=True)
        try:
            offer = submit_offer(
                customer=request.user,
                listing=listing,
                price=request.POST.get('proposed_price'),
                quantity=request.POST.get('proposed_quantity'),
                message=request.POST.get('message', ''),
            )
            messages.success(request, 'Offer submitted successfully!')
        except Exception as e:
            messages.error(request, str(e))
        return redirect('listings:detail', ref_code=ref_code)


class CounterOfferView(LoginRequiredMixin, View):
    def post(self, request, offer_id):
        offer = get_object_or_404(Offer, pk=offer_id)
        try:
            submit_counter_offer(
                listing=offer.listing,
                offer=offer,
                new_price=request.POST.get('proposed_price'),
                message=request.POST.get('message', ''),
            )
            messages.success(request, 'Counter-offer sent.')
        except Exception as e:
            messages.error(request, str(e))
        return redirect('listings:detail', ref_code=offer.listing.reference_code)


class AcceptOfferView(LoginRequiredMixin, View):
    def post(self, request, offer_id):
        offer = get_object_or_404(Offer, pk=offer_id)
        try:
            deal = accept_offer(offer)
            messages.success(request, 'Offer accepted! A deal and order have been created.')
            return redirect('orders:list')
        except Exception as e:
            messages.error(request, str(e))
        return redirect('listings:detail', ref_code=offer.listing.reference_code)


class AcceptCounterOfferView(LoginRequiredMixin, View):
    def post(self, request, counter_offer_id):
        co = get_object_or_404(CounterOffer, pk=counter_offer_id)
        try:
            deal = accept_counter_offer(co)
            messages.success(request, "Counter-offer accepted! Your order has been created.")
            return redirect('orders:list')
        except Exception as e:
            messages.error(request, str(e))
        return redirect('listings:detail', ref_code=co.offer.listing.reference_code)


class RejectOfferView(LoginRequiredMixin, View):
    def post(self, request, offer_id):
        offer = get_object_or_404(Offer, pk=offer_id)
        try:
            reject_offer(offer)
            messages.success(request, 'Offer rejected.')
        except Exception as e:
            messages.error(request, str(e))
        return redirect('listings:detail', ref_code=offer.listing.reference_code)


class NegotiationThreadView(LoginRequiredMixin, View):
    def get(self, request, ref_code):
        listing = get_object_or_404(Listing, reference_code=ref_code, is_active=True)

        # Is the user the farmer of this listing?
        is_farmer = (
            listing.farmer == request.user or
            listing.contact_phone == getattr(request.user, 'phone', None)
        )

        if is_farmer:
            # Farmer sees ALL offers on their listing
            all_offers = Offer.objects.filter(
                listing=listing
            ).prefetch_related('counter_offers').order_by('-created_at')
            thread = None
            can_offer = False
        else:
            # Buyer sees only their own thread
            thread = get_negotiation_thread(listing, request.user)
            all_offers = None
            can_offer = Offer.objects.filter(
                listing=listing, customer=request.user
            ).count() < 3

        return render(request, 'negotiations/thread.html', {
            'listing': listing,
            'thread': thread,
            'all_offers': all_offers,
            'can_offer': can_offer,
            'is_farmer': is_farmer,
        })
