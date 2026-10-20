from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views import View
from .models import Order
from .services import confirm_order, cancel_order, mark_delivered, submit_freshness_score


class OrderListView(LoginRequiredMixin, View):
    def get(self, request):
        orders = Order.objects.filter(customer=request.user).select_related(
            'deal__offer__listing'
        )
        return render(request, 'orders/order_list.html', {'orders': orders})


class OrderDetailView(LoginRequiredMixin, View):
    def get(self, request, pk):
        order = get_object_or_404(Order, pk=pk, customer=request.user)
        return render(request, 'orders/order_detail.html', {'order': order})


class ConfirmOrderView(LoginRequiredMixin, View):
    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk, customer=request.user)
        payment_method = request.POST.get('payment_method', 'pod')
        try:
            if payment_method == 'paystack':
                order.delivery_method = 'paystack'
                order.save(update_fields=['delivery_method'])
                return redirect('payments:initiate', order_id=pk)
            else:
                order.delivery_method = 'pod'
                order.save(update_fields=['delivery_method'])
                confirm_order(order)
                messages.success(request, 'Order confirmed! The farmer will be in touch.')
                return redirect('orders:detail', pk=pk)
        except Exception as e:
            messages.error(request, str(e))
        return redirect('orders:detail', pk=pk)


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
            messages.success(request, 'Order marked as delivered.')
        except Exception as e:
            messages.error(request, str(e))
        return redirect('orders:detail', pk=pk)


class RateOrderView(LoginRequiredMixin, View):
    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk, customer=request.user)
        try:
            stars = int(request.POST.get('stars', 3))
            review_text = request.POST.get('review_text', '')
            submit_freshness_score(order, request.user, stars, review_text)
            messages.success(request, 'Thank you for your review!')
        except Exception as e:
            messages.error(request, str(e))
        return redirect('orders:detail', pk=pk)
