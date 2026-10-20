import os, sys, django
os.environ['DJANGO_SETTINGS_MODULE'] = 'agroconnect.settings'
sys.path.insert(0, r'c:\Users\KIZITO\AgriConnect\agroconnect')
django.setup()

from apps.orders.models import Order
from apps.negotiations.models import Deal, Offer, CounterOffer
from apps.notifications.models import Notification
from apps.listings.models import Listing, FreshnessScore
from apps.stories.models import FarmStory, FarmStoryLike
from apps.broadcasts.models import PriceBroadcast
from django.contrib.auth import get_user_model

Customer = get_user_model()
emails = ['buyer@test.ng', 'farmer@test.ng']
customers = Customer.objects.filter(email__in=emails)

FreshnessScore.objects.filter(customer__in=customers).delete()
FarmStoryLike.objects.filter(customer__in=customers).delete()
Notification.objects.filter(customer__in=customers).delete()
Order.objects.filter(customer__in=customers).delete()
Deal.objects.filter(offer__customer__in=customers).delete()
CounterOffer.objects.filter(offer__customer__in=customers).delete()
Offer.objects.filter(customer__in=customers).delete()
Listing.objects.filter(contact_phone__in=['08011110000', '08099990000']).delete()
FarmStory.objects.filter(farmer_name__in=['Test Buyer', 'Test Farmer']).delete()
PriceBroadcast.objects.filter(broadcaster_phone='08055550000').delete()
customers.delete()
print('Cleaned up test data OK')
