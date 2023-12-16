from django.utils import timezone

def day_has_changed(day: timezone) -> bool:
    current_day = timezone.now().day
    if current_day != day:
        day = current_day
        return True

    return False
