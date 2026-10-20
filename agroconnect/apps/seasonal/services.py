from datetime import date
from .constants import STATE_TO_AGRO_ZONE


def evaluate_season_signal(produce_category, listing_state):
    zone = STATE_TO_AGRO_ZONE.get(str(listing_state).lower())
    if not zone:
        return 'off_season'
    try:
        from .models import HarvestSeasonSignal
        signal = HarvestSeasonSignal.objects.get(
            produce_category__iexact=produce_category, agro_zone=zone
        )
        current_month = date.today().month
        peak_months = [int(m.strip()) for m in signal.peak_months.split(',') if m.strip()]
        return 'in_season' if current_month in peak_months else 'off_season'
    except Exception:
        return 'off_season'
