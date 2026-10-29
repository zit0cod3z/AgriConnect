from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from django.views import View
from .models import Order
from .services import (
    confirm_order, cancel_order, mark_in_transit,
    mark_delivered, submit_freshness_score
)


def get_order_for_user(pk, user):
    """Return order if user is buyer OR farmer."""
    return get_object_or_404(
        Order,
        Q(pk=pk) & (Q(customer=user) | Q(farmer_phone=user.phone))
    )


# ─────────────────────────────────────────────────────────── Buyer views ──

class OrderListView(LoginRequiredMixin, View):
    def get(self, request):
        buyer_orders = Order.objects.filter(
            customer=request.user
        ).select_related('deal__offer__listing').order_by('-created_at')
        farmer_orders = Order.objects.filter(
            farmer_phone=request.user.phone
        ).exclude(customer=request.user).select_related(
            'deal__offer__listing'
        ).order_by('-created_at') if request.user.phone else Order.objects.none()
        pending_count = farmer_orders.filter(status='pending_confirmation').count()
        return render(request, 'orders/order_list.html', {
            'orders': buyer_orders,
            'farmer_orders': farmer_orders,
            'pending_count': pending_count,
        })


class OrderDetailView(LoginRequiredMixin, View):
    def get(self, request, pk):
        order = get_order_for_user(pk, request.user)
        is_farmer = (
            order.farmer_phone == request.user.phone
            and order.customer != request.user
        )
        return render(request, 'orders/order_detail.html', {
            'order': order,
            'is_farmer': is_farmer,
        })


class ConfirmOrderView(LoginRequiredMixin, View):
    """Legacy — buyer confirms payment method (used internally)."""
    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk, customer=request.user)
        payment_method = request.POST.get('payment_method', 'pod')
        try:
            if payment_method == 'paystack':
                order.delivery_method = 'paystack'
                order.save(update_fields=['delivery_method'])
                return redirect('payments:initiate', order_id=pk)
            else:
                order.delivery_method = payment_method  # pod or pickup
                order.save(update_fields=['delivery_method'])
                confirm_order(order)
                messages.success(request, 'Order confirmed!')
                return redirect('orders:detail', pk=pk)
        except Exception as e:
            messages.error(request, str(e))
        return redirect('orders:detail', pk=pk)


class PaymentChoiceView(LoginRequiredMixin, View):
    """
    Step shown to buyer AFTER farmer accepts the order.
    Buyer chooses: POD / Paystack / Pickup.
    """
    def get(self, request, pk):
        order = get_object_or_404(Order, pk=pk, customer=request.user)
        if order.status != 'accepted':
            return redirect('orders:detail', pk=pk)
        return render(request, 'orders/payment_choice.html', {'order': order})

    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk, customer=request.user)
        method = request.POST.get('delivery_method', 'pod')
        order.delivery_method = method
        order.save(update_fields=['delivery_method'])

        if method == 'paystack':
            # Go straight to Paystack — no address needed
            order.status = 'pending_payment'
            order.save(update_fields=['status'])
            return redirect('payments:initiate', order_id=pk)

        elif method == 'pod':
            # Need buyer's delivery address
            order.status = 'awaiting_address'
            order.save(update_fields=['status'])
            return redirect('orders:provide_address', pk=pk)

        elif method == 'pickup':
            # Show farmer's pickup/store address to buyer, then confirm
            order.status = 'awaiting_address'
            order.save(update_fields=['status'])
            return redirect('orders:provide_address', pk=pk)

        return redirect('orders:detail', pk=pk)


class ProvideAddressView(LoginRequiredMixin, View):
    """
    POD  → buyer provides delivery address → order confirmed → map starts
    Pickup → farmer's address is shown → buyer confirms → map starts
    """
    def get(self, request, pk):
        order = get_object_or_404(Order, pk=pk, customer=request.user)
        if order.status not in ('awaiting_address', 'accepted'):
            return redirect('orders:detail', pk=pk)
        # Pre-fill buyer's saved address if available
        default_address = request.user.address or ''
        return render(request, 'orders/provide_address.html', {
            'order': order,
            'default_address': default_address,
        })

    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk, customer=request.user)
        if order.delivery_method == 'pod':
            address = request.POST.get('delivery_address', '').strip()
            lat = request.POST.get('lat', '')
            lng = request.POST.get('lng', '')
            if not address:
                messages.error(request, 'Please provide your delivery address.')
                return redirect('orders:provide_address', pk=pk)
            order.delivery_address = address
            if lat and lng:
                try:
                    order.delivery_lat = float(lat)
                    order.delivery_lng = float(lng)
                except ValueError:
                    pass
            # Save buyer address to profile if requested
            if request.POST.get('save_address'):
                request.user.address = address
                request.user.save(update_fields=['address'])

        elif order.delivery_method == 'pickup':
            # Use farmer's store address
            farmer = order.deal.offer.listing.farmer
            if farmer and farmer.store_address:
                order.pickup_address = farmer.store_address
                order.pickup_lat = farmer.store_lat
                order.pickup_lng = farmer.store_lng

        order.status = 'confirmed'
        order.save()
        # Notify farmer
        try:
            from apps.notifications.services import notify
            from apps.accounts.models import Customer
            farmer_users = Customer.objects.filter(phone=order.farmer_phone)
            for f in farmer_users:
                notify(f, 'order_status_change', {
                    'order_id': order.pk,
                    'status': 'confirmed',
                    'message': f'Buyer confirmed — {order.get_delivery_method_display()}',
                })
        except Exception:
            pass
        messages.success(request, 'Order confirmed! Setting up delivery tracking...')
        # Auto-redirect to delivery setup
        return redirect('delivery:setup', order_id=pk)


class CancelOrderView(LoginRequiredMixin, View):
    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk, customer=request.user)
        try:
            cancel_order(order)
            if order.status == 'cancelled':
                messages.success(request, 'Order cancelled.')
            else:
                messages.info(request, 'Cancellation request sent to farmer.')
        except Exception as e:
            messages.error(request, str(e))
        return redirect('orders:detail', pk=pk)


class MarkDeliveredView(LoginRequiredMixin, View):
    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk, customer=request.user)
        try:
            mark_delivered(order)
            messages.success(request, 'Order marked as delivered. Please rate the produce!')
        except Exception as e:
            messages.error(request, str(e))
        return redirect('orders:detail', pk=pk)


class RateOrderView(LoginRequiredMixin, View):
    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk, customer=request.user)
        if order.status not in ('delivered', 'closed'):
            messages.error(request, 'You can only rate a delivered order.')
            return redirect('orders:detail', pk=pk)
        try:
            stars = max(1, min(5, int(request.POST.get('stars', 5))))
            review_text = request.POST.get('review_text', '').strip()
            submit_freshness_score(order, request.user, stars, review_text)
            messages.success(request, f'Thank you! You gave {stars}★ — your feedback helps the community.')
        except Exception as e:
            messages.error(request, str(e))
        return redirect('orders:detail', pk=pk)


# ─────────────────────────────────────────────────────────── Farmer views ──

class FarmerInboxView(LoginRequiredMixin, View):
    def get(self, request):
        if not request.user.phone:
            messages.warning(request, 'Add your phone number in your profile to receive orders.')
            return redirect('accounts:dashboard')
        orders = Order.objects.filter(
            farmer_phone=request.user.phone
        ).select_related('deal__offer__listing', 'customer').order_by('-created_at')
        pending   = orders.filter(status='pending_confirmation')
        accepted  = orders.filter(status__in=['accepted', 'awaiting_address'])
        confirmed = orders.filter(status__in=['confirmed', 'ready'])
        transit   = orders.filter(status='in_transit')
        completed = orders.filter(status__in=['delivered', 'closed', 'cancelled'])
        return render(request, 'orders/farmer_inbox.html', {
            'pending':      pending,
            'accepted':     accepted,
            'confirmed':    confirmed,
            'transit':      transit,
            'completed':    completed,
            'total_pending': pending.count(),
        })


class FarmerAcceptOrderView(LoginRequiredMixin, View):
    """Farmer accepts order → buyer gets notified to choose payment method."""
    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk, farmer_phone=request.user.phone)
        if order.status != 'pending_confirmation':
            messages.error(request, 'This order cannot be accepted now.')
            return redirect('orders:detail', pk=pk)
        order.status = 'accepted'
        order.save(update_fields=['status', 'updated_at'])
        # Notify buyer
        try:
            from apps.notifications.services import notify
            notify(order.customer, 'order_status_change', {
                'order_id': order.pk,
                'status': 'accepted',
                'message': 'Your order was accepted! Please choose your payment method.',
            })
        except Exception:
            pass
        messages.success(request, f'Order #{pk} accepted! Buyer has been asked to choose payment method.')
        return redirect('orders:farmer_inbox')


class FarmerRejectOrderView(LoginRequiredMixin, View):
    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk, farmer_phone=request.user.phone)
        try:
            cancel_order(order)
            messages.success(request, f'Order #{pk} rejected.')
        except Exception as e:
            messages.error(request, str(e))
        return redirect('orders:farmer_inbox')


class FarmerMarkReadyView(LoginRequiredMixin, View):
    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk, farmer_phone=request.user.phone)
        if order.status != 'confirmed':
            messages.error(request, 'Order must be confirmed before marking ready.')
            return redirect('orders:detail', pk=pk)
        order.status = 'ready'
        order.save(update_fields=['status', 'updated_at'])
        try:
            from apps.notifications.services import notify
            notify(order.customer, 'order_status_change', {
                'order_id': order.pk, 'status': 'ready',
                'message': 'Your order is packed and ready!',
            })
        except Exception:
            pass
        messages.success(request, 'Order marked as packed and ready!')
        return redirect('orders:detail', pk=pk)


class FarmerMarkInTransitView(LoginRequiredMixin, View):
    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk, farmer_phone=request.user.phone)
        try:
            mark_in_transit(order)
            messages.success(request, 'Order dispatched! Buyer can now track your location.')
        except Exception as e:
            messages.error(request, str(e))
        return redirect('orders:detail', pk=pk)


class FarmerSetPickupAddressView(LoginRequiredMixin, View):
    """Farmer sets their pickup/store address for this order."""
    def get(self, request, pk):
        order = get_object_or_404(Order, pk=pk, farmer_phone=request.user.phone)
        return render(request, 'orders/farmer_set_pickup.html', {
            'order': order,
            'default_address': request.user.store_address or '',
        })

    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk, farmer_phone=request.user.phone)
        address = request.POST.get('pickup_address', '').strip()
        lat = request.POST.get('lat', '')
        lng = request.POST.get('lng', '')
        if not address:
            messages.error(request, 'Please provide your pickup address.')
            return redirect('orders:farmer_set_pickup', pk=pk)
        order.pickup_address = address
        if lat and lng:
            try:
                order.pickup_lat = float(lat)
                order.pickup_lng = float(lng)
            except ValueError:
                pass
        order.save()
        # Save to farmer profile
        if request.POST.get('save_to_profile'):
            request.user.store_address = address
            if lat and lng:
                try:
                    request.user.store_lat = float(lat)
                    request.user.store_lng = float(lng)
                except ValueError:
                    pass
            request.user.save(update_fields=['store_address', 'store_lat', 'store_lng'])
        # Notify buyer
        try:
            from apps.notifications.services import notify
            notify(order.customer, 'order_status_change', {
                'order_id': order.pk,
                'message': f'Pickup address set: {address}',
            })
        except Exception:
            pass
        messages.success(request, 'Pickup address set. Buyer has been notified.')
        return redirect('orders:detail', pk=pk)


# ─────────────────────────────────────────────────── Reputation / Ratings ──

class FarmerReputationView(View):
    def get(self, request, farmer_phone):
        from apps.listings.models import FreshnessScore, Listing
        from apps.listings.services import get_farmer_freshness_score
        scores = FreshnessScore.objects.filter(
            farmer_phone=farmer_phone
        ).select_related('customer', 'order__deal__offer__listing').order_by('-created_at')
        summary  = get_farmer_freshness_score(farmer_phone)
        listings = Listing.objects.filter(contact_phone=farmer_phone, is_active=True)[:6]
        return render(request, 'orders/farmer_reputation.html', {
            'scores': scores, 'summary': summary,
            'farmer_phone': farmer_phone, 'listings': listings,
        })


class MyRatingsView(LoginRequiredMixin, View):
    def get(self, request):
        from apps.listings.models import FreshnessScore
        from apps.listings.services import get_farmer_freshness_score
        given    = FreshnessScore.objects.filter(customer=request.user).select_related(
            'order__deal__offer__listing').order_by('-created_at')
        received = FreshnessScore.objects.none()
        summary  = None
        if request.user.phone:
            received = FreshnessScore.objects.filter(
                farmer_phone=request.user.phone
            ).select_related('customer', 'order__deal__offer__listing').order_by('-created_at')
            summary = get_farmer_freshness_score(request.user.phone)
        return render(request, 'orders/my_ratings.html', {
            'given': given, 'received': received, 'summary': summary,
        })
