from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views import View
from django.utils import timezone
from datetime import timedelta
from .models import PriceBroadcast
from .services import create_broadcast, get_active_broadcasts, record_interest
from .forms import BroadcastForm


class BroadcastFeedView(View):
    def get(self, request):
        broadcasts = get_active_broadcasts()
        return render(request, 'broadcasts/feed.html', {'broadcasts': broadcasts})


class CreateBroadcastView(View):
    def get(self, request):
        return render(request, 'broadcasts/create_broadcast.html', {'form': BroadcastForm()})

    def post(self, request):
        form = BroadcastForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            data['expires_at'] = timezone.now() + timedelta(days=7)
            if request.user.is_authenticated:
                data['broadcaster_customer'] = request.user
            try:
                create_broadcast(data)
                messages.success(request, 'Price broadcast posted! Farmers will respond soon.')
                return redirect('broadcasts:feed')
            except Exception as e:
                messages.error(request, str(e))
        return render(request, 'broadcasts/create_broadcast.html', {'form': form})


class BroadcastInterestView(LoginRequiredMixin, View):
    def post(self, request, pk):
        broadcast = get_object_or_404(PriceBroadcast, pk=pk, is_expired=False)
        try:
            record_interest(
                broadcast=broadcast,
                responder_name=request.user.get_full_name() or request.user.username,
                responder_phone=request.user.phone,
                message=request.POST.get('message', ''),
                customer=request.user,
            )
            messages.success(request, 'Interest recorded! The buyer has been notified.')
        except Exception as e:
            messages.error(request, str(e))
        return redirect('broadcasts:feed')
