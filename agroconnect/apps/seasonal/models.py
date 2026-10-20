from django.db import models

AGRO_ZONES = [
    ('north_west', 'North-West'), ('north_east', 'North-East'),
    ('north_central', 'North-Central'), ('south_west', 'South-West'),
    ('south_east', 'South-East'), ('south_south', 'South-South'),
]


class HarvestSeasonSignal(models.Model):
    produce_category = models.CharField(max_length=100)
    agro_zone = models.CharField(max_length=20, choices=AGRO_ZONES)
    peak_months = models.CharField(max_length=50, help_text='Comma-separated month numbers e.g. 1,2,3,10')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'seasonal_harvest_signal'
        unique_together = [('produce_category', 'agro_zone')]

    def __str__(self):
        return f"{self.produce_category} - {self.agro_zone}"


class AvailabilityCalendar(models.Model):
    produce_category = models.CharField(max_length=100)
    geo_zone = models.CharField(max_length=20, choices=AGRO_ZONES)
    available_months = models.CharField(max_length=50)
    price_trend_notes = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'seasonal_availability_calendar'
        unique_together = [('produce_category', 'geo_zone')]

    def __str__(self):
        return f"{self.produce_category} - {self.geo_zone}"
