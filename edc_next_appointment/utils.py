from __future__ import annotations

from dateutil.relativedelta import relativedelta
from django.conf import settings


def get_max_months_to_next_appointment():
    return getattr(settings, "EDC_NEXT_APPOINTMENT_MAX_MONTHS_TO_NEXT_APPT", 6)


def get_max_months_to_next_appointment_as_rdelta():
    max_months = get_max_months_to_next_appointment()
    return relativedelta(months=max_months)


def allow_clinic_on_weekend():
    return getattr(settings, "EDC_NEXT_APPOINTMENT_ALLOW_CLINIC_ON_WEEKENDS", False)
