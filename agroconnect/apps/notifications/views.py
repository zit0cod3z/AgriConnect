from django.shortcuts import render, get_object_or_404
from django.views import View
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .models import Notification
from .services import mark_read, get_unread_count


@method_decorator(login_required, name='dispatch')
class NotificationListView(View):
    def get(self, request):
        notifications = Notification.objects.filter(customer=request.user)
        unread_count = get_unread_count(request.user)
        return render(request, 'notifications/notification_list.html', {
            'notifications': notifications,
            'unread_count': unread_count,
        })


@method_decorator(login_required, name='dispatch')
class MarkReadView(View):
    def post(self, request, pk):
        notif = get_object_or_404(Notification, pk=pk, customer=request.user)
        mark_read(notif)
        return JsonResponse({'count': get_unread_count(request.user)})


def unread_count_api(request):
    if request.user.is_authenticated:
        return JsonResponse({'count': get_unread_count(request.user)})
    return JsonResponse({'count': 0})
