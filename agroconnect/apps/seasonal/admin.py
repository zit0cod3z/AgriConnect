from django.contrib import admin
from .models import HarvestSeasonSignal, AvailabilityCalendar


@admin.register(HarvestSeasonSignal)
class HarvestSeasonSignalAdmin(admin.ModelAdmin):
    list_display = ('produce_category', 'agro_zone', 'peak_months', 'updated_at')


@admin.register(AvailabilityCalendar)
class AvailabilityCalendarAdmin(admin.ModelAdmin):
    list_display = ('produce_category', 'geo_zone', 'available_months', 'updated_at')
