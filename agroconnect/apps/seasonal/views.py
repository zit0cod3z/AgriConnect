from django.shortcuts import render
from django.views import View
from .models import HarvestSeasonSignal, AvailabilityCalendar, AGRO_ZONES
from .services import evaluate_season_signal
import calendar as cal


class SeasonalGuideView(View):
    def get(self, request):
        signals = HarvestSeasonSignal.objects.all().order_by('produce_category')
        for s in signals:
            s.current_status = evaluate_season_signal(s.produce_category, s.agro_zone.replace('_', ' '))
        return render(request, 'seasonal/guide.html', {'signals': signals})


class AvailabilityCalendarView(View):
    def get(self, request):
        zone_filter = request.GET.get('zone', '')
        entries = AvailabilityCalendar.objects.all()
        if zone_filter:
            entries = entries.filter(geo_zone=zone_filter)
        months = [cal.month_name[i] for i in range(1, 13)]
        for e in entries:
            e.available_months_list = [int(m.strip()) for m in e.available_months.split(',') if m.strip()]
        return render(request, 'seasonal/calendar.html', {
            'entries': entries,
            'months': months,
            'month_numbers': range(1, 13),
            'zones': AGRO_ZONES,
            'zone_filter': zone_filter,
        })
