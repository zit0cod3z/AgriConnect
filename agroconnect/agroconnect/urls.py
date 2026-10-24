from django.urls import path, include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    path('', include('apps.listings.urls', namespace='listings')),
    path('about/', TemplateView.as_view(template_name='about.html'), name='about'),
    path('accounts/', include('apps.accounts.urls', namespace='accounts')),
    path('negotiations/', include('apps.negotiations.urls', namespace='negotiations')),
    path('orders/', include('apps.orders.urls', namespace='orders')),
    path('payments/', include('apps.payments.urls', namespace='payments')),
    path('broadcasts/', include('apps.broadcasts.urls', namespace='broadcasts')),
    path('groupbuy/', include('apps.groupbuy.urls', namespace='groupbuy')),
    path('seasonal/', include('apps.seasonal.urls', namespace='seasonal')),
    path('stories/', include('apps.stories.urls', namespace='stories')),
    path('notifications/', include('apps.notifications.urls', namespace='notifications')),
    path('admin-panel/', include('apps.admin_panel.urls', namespace='admin_panel')),
    path('admin/', admin.site.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'apps.listings.views.handler_404'
handler500 = 'apps.listings.views.handler_500'
