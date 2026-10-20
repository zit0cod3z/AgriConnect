from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import HttpResponse
from django.views import View
import json
from .services import initiate_paystack_payment, verify_paystack_payment, handle_paystack_webhook
from apps.orders.models import Order


class InitiatePaymentView(LoginRequiredMixin, View):
    def get(self, request, order_id):
        order = get_object_or_404(Order, pk=order_id, customer=request.user)
        return render(request, 'payments/initiate.html', {'order': order})

    def post(self, request, order_id):
        order = get_object_or_404(Order, pk=order_id, customer=request.user)
        try:
            auth_url = initiate_paystack_payment(order)
            return redirect(auth_url)
        except Exception as e:
            return render(request, 'payments/callback.html', {
                'success': False, 'message': str(e), 'order': order,
            })


class PaystackCallbackView(View):
    def get(self, request):
        reference = request.GET.get('reference', '')
        order = None
        success = False
        message = ''
        if reference:
            try:
                data = verify_paystack_payment(reference)
                from .models import PaystackTransaction
                txn = PaystackTransaction.objects.filter(reference=reference).first()
                if txn:
                    order = txn.order
                    if data.get('data', {}).get('status') == 'success':
                        txn.paystack_status = 'success'
                        txn.save(update_fields=['paystack_status'])
                        from apps.orders.services import confirm_order
                        try:
                            confirm_order(order)
                        except Exception:
                            pass
                        success = True
                    else:
                        message = 'Payment was not successful.'
            except Exception as e:
                message = str(e)
        return render(request, 'payments/callback.html', {
            'success': success, 'order': order, 'message': message,
        })


@method_decorator(csrf_exempt, name='dispatch')
class PaystackWebhookView(View):
    def post(self, request):
        signature = request.headers.get('X-Paystack-Signature', '')
        try:
            payload = json.loads(request.body)
            handle_paystack_webhook(payload, signature)
        except Exception:
            pass
        return HttpResponse(status=200)
