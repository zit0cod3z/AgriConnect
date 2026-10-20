from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.http import Http404
from .models import Listing, ListingImage, CATEGORY_CHOICES
from .forms import ListingForm, GuestAccessForm
from .services import create_listing, get_catalogue, search_listings, verify_listing_access, deactivate_listing, get_farmer_freshness_score
from .decorators import rate_limit


class CatalogueView(View):
    def get(self, request):
        filters = {
            'category': request.GET.get('category', ''),
            'farm_state': request.GET.get('state', ''),
            'price_min': request.GET.get('price_min', ''),
            'price_max': request.GET.get('price_max', ''),
        }
        filters = {k: v for k, v in filters.items() if v}
        page = request.GET.get('page', 1)
        listings = get_catalogue(filters, page)
        return render(request, 'listings/catalogue.html', {
            'listings': listings,
            'filters': filters,
            'categories': CATEGORY_CHOICES,
        })


class CreateListingView(View):
    def get(self, request):
        return render(request, 'listings/create_listing.html', {'form': ListingForm()})

    @rate_limit('listing_create', 10, 3600)
    def post(self, request):
        form = ListingForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            if request.user.is_authenticated:
                data['farmer'] = request.user
            try:
                listing = create_listing(data)
                images = request.FILES.getlist('images')
                for img in images[:5]:
                    if img.size > 5 * 1024 * 1024:
                        messages.error(request, f'{img.name} exceeds 5MB limit.')
                        continue
                    ListingImage.objects.create(listing=listing, image=img)
                messages.success(request, f'Listing created! Your reference code is: {listing.reference_code}')
                return render(request, 'listings/listing_created.html', {'listing': listing})
            except Exception as e:
                messages.error(request, str(e))
        return render(request, 'listings/create_listing.html', {'form': form})


class ListingDetailView(View):
    def get(self, request, ref_code):
        listing = get_object_or_404(Listing, reference_code=ref_code, is_active=True)
        freshness = get_farmer_freshness_score(listing.contact_phone)
        from apps.seasonal.services import evaluate_season_signal
        season_status = evaluate_season_signal(listing.category, listing.farm_state)
        thread = []
        if request.user.is_authenticated:
            from apps.negotiations.models import Offer
            offers = Offer.objects.filter(listing=listing, customer=request.user)
            for offer in offers:
                thread.append({'actor': 'customer', 'price': offer.proposed_price, 'quantity': offer.proposed_quantity, 'message': offer.message, 'status': offer.status, 'timestamp': offer.created_at})
                for co in offer.counter_offers.all():
                    thread.append({'actor': 'farmer', 'price': co.proposed_price, 'quantity': offer.proposed_quantity, 'message': co.message, 'status': co.status, 'timestamp': co.created_at})
            thread.sort(key=lambda x: x['timestamp'])
        group_buy = None
        if listing.group_buy_eligible:
            try:
                group_buy = listing.group_buy
            except Exception:
                pass
        return render(request, 'listings/listing_detail.html', {
            'listing': listing,
            'freshness': freshness,
            'season_status': season_status,
            'thread': thread,
            'group_buy': group_buy,
        })


class EditListingView(View):
    def get(self, request, ref_code):
        return render(request, 'listings/edit_listing.html', {'form': GuestAccessForm(), 'ref_code': ref_code, 'step': 'verify'})

    def post(self, request, ref_code):
        if 'verified' in request.POST:
            listing = get_object_or_404(Listing, reference_code=ref_code)
            form = ListingForm(request.POST, initial={
                'produce_name': listing.produce_name, 'category': listing.category,
                'quantity': listing.quantity, 'unit': listing.unit,
                'price_per_unit': listing.price_per_unit, 'farm_state': listing.farm_state,
                'farm_lga': listing.farm_lga, 'contact_phone': listing.contact_phone,
                'description': listing.description,
            })
            if form.is_valid():
                d = form.cleaned_data
                for field in ['produce_name', 'category', 'quantity', 'unit', 'price_per_unit', 'farm_state', 'farm_lga', 'description']:
                    setattr(listing, field, d[field])
                listing.save()
                messages.success(request, 'Listing updated successfully.')
                return redirect('listings:detail', ref_code=ref_code)
            return render(request, 'listings/edit_listing.html', {'form': form, 'ref_code': ref_code, 'step': 'edit', 'listing': listing})
        else:
            form = GuestAccessForm(request.POST)
            if form.is_valid():
                listing = verify_listing_access(form.cleaned_data['reference_code'], form.cleaned_data['contact_phone'])
                if listing:
                    edit_form = ListingForm(initial={
                        'produce_name': listing.produce_name, 'category': listing.category,
                        'quantity': listing.quantity, 'unit': listing.unit,
                        'price_per_unit': listing.price_per_unit, 'farm_state': listing.farm_state,
                        'farm_lga': listing.farm_lga, 'contact_phone': listing.contact_phone,
                        'description': listing.description,
                    })
                    return render(request, 'listings/edit_listing.html', {'form': edit_form, 'ref_code': ref_code, 'step': 'edit', 'listing': listing})
                messages.error(request, 'Invalid reference code or phone number.')
            return render(request, 'listings/edit_listing.html', {'form': form, 'ref_code': ref_code, 'step': 'verify'})


class DeleteListingView(View):
    def post(self, request, ref_code):
        form = GuestAccessForm(request.POST)
        if form.is_valid():
            listing = verify_listing_access(form.cleaned_data['reference_code'], form.cleaned_data['contact_phone'])
            if listing:
                deactivate_listing(listing)
                messages.success(request, 'Listing removed successfully.')
                return redirect('/')
            messages.error(request, 'Invalid reference code or phone number.')
        return redirect('listings:detail', ref_code=ref_code)


class SearchView(View):
    def get(self, request):
        query = request.GET.get('q', '').strip()
        results = []
        if query:
            results = search_listings(query)
        return render(request, 'listings/search_results.html', {'results': results, 'query': query, 'categories': CATEGORY_CHOICES})


def handler_404(request, exception=None):
    return render(request, 'errors/404.html', status=404)


def handler_500(request):
    return render(request, 'errors/500.html', status=500)
