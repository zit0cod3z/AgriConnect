import json
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views import View
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from apps.orders.models import Order
from .models import DeliveryTracking


class DeliverySetupView(LoginRequiredMixin, View):
    """Buyer sets up delivery type and their location."""
    def get(self, request, order_id):
        order = get_object_or_404(Order, pk=order_id, customer=request.user)
        tracking = DeliveryTracking.objects.filter(order=order).first()
        return render(request, 'delivery/setup.html', {
            'order': order,
            'tracking': tracking,
        })

    def post(self, request, order_id):
        order = get_object_or_404(Order, pk=order_id, customer=request.user)
        delivery_type  = request.POST.get('delivery_type', 'delivery')
        buyer_lat      = request.POST.get('buyer_lat', '')
        buyer_lng      = request.POST.get('buyer_lng', '')
        buyer_address  = request.POST.get('buyer_address', '')
        farmer_address = request.POST.get('farmer_address', '')

        tracking, created = DeliveryTracking.objects.get_or_create(order=order)
        tracking.delivery_type  = delivery_type
        tracking.buyer_address  = buyer_address
        tracking.farmer_address = farmer_address
        if buyer_lat and buyer_lng:
            tracking.buyer_lat = float(buyer_lat)
            tracking.buyer_lng = float(buyer_lng)
        tracking.status = 'active'
        tracking.save()

        messages.success(request, 'Delivery tracking started!')
        return redirect('delivery:track', order_id=order_id)


class DeliveryTrackView(LoginRequiredMixin, View):
    """Live map tracking page — visible to buyer, farmer and admin."""
    def get(self, request, order_id):
        order = get_object_or_404(Order, pk=order_id)
        # Allow: buyer, farmer (via phone match), or staff
        is_buyer  = order.customer == request.user
        is_farmer = (order.farmer_phone == getattr(request.user, 'phone', None))
        is_staff  = request.user.is_staff
        if not (is_buyer or is_farmer or is_staff):
            messages.error(request, 'You do not have access to this delivery.')
            return redirect('orders:list')

        tracking = get_object_or_404(DeliveryTracking, order=order)
        return render(request, 'delivery/track.html', {
            'order': order,
            'tracking': tracking,
            'is_farmer': is_farmer or is_staff,
            'is_buyer': is_buyer,
        })


class DeliveryLocationUpdateView(LoginRequiredMixin, View):
    """Farmer/driver POSTs their current GPS location via AJAX."""
    def post(self, request, order_id):
        order = get_object_or_404(Order, pk=order_id)
        tracking = get_object_or_404(DeliveryTracking, order=order)

        try:
            data = json.loads(request.body)
            tracking.current_lat = float(data['lat'])
            tracking.current_lng = float(data['lng'])
            tracking.estimated_arrival = data.get('eta', '')
            tracking.save(update_fields=['current_lat', 'current_lng', 'estimated_arrival', 'last_updated'])
            return JsonResponse({'status': 'ok', 'last_updated': tracking.last_updated.isoformat()})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


class DeliveryLocationPollView(LoginRequiredMixin, View):
    """Buyer polls this every 10s to get farmer's current position."""
    def get(self, request, order_id):
        order = get_object_or_404(Order, pk=order_id)
        tracking = get_object_or_404(DeliveryTracking, order=order)
        return JsonResponse({
            'status':           tracking.status,
            'delivery_type':    tracking.delivery_type,
            'current_lat':      tracking.current_lat,
            'current_lng':      tracking.current_lng,
            'farmer_lat':       tracking.farmer_lat,
            'farmer_lng':       tracking.farmer_lng,
            'buyer_lat':        tracking.buyer_lat,
            'buyer_lng':        tracking.buyer_lng,
            'farmer_address':   tracking.farmer_address,
            'buyer_address':    tracking.buyer_address,
            'estimated_arrival':tracking.estimated_arrival,
            'last_updated':     tracking.last_updated.isoformat() if tracking.last_updated else None,
        })


class DeliveryCompleteView(LoginRequiredMixin, View):
    """Mark delivery as arrived/completed."""
    def post(self, request, order_id):
        order = get_object_or_404(Order, pk=order_id)
        tracking = get_object_or_404(DeliveryTracking, order=order)
        action = request.POST.get('action', 'arrived')
        if action == 'complete':
            tracking.status = 'completed'
        else:
            tracking.status = 'arrived'
        tracking.save(update_fields=['status'])
        return JsonResponse({'status': tracking.status})
