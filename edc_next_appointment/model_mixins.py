from __future__ import annotations

from django.db import models
from django.db.models import PROTECT
from edc_facility.utils import get_health_facility_model
from edc_visit_schedule.models import VisitSchedule

from .models import InfoSources


class NextAppointmentCrfModelMixin(models.Model):
    health_facility = models.ForeignKey(
        get_health_facility_model(),
        on_delete=PROTECT,
        null=True,
        blank=True,
    )

    appt_date = models.DateField(
        verbose_name="Next scheduled routine/facility appointment",
        null=True,
        blank=False,
        help_text="Should fall on an Integrated clinic day",
    )

    info_source = models.ForeignKey(
        InfoSources,
        verbose_name="What is the source of this appointment date",
        max_length=15,
        on_delete=PROTECT,
        null=True,
        blank=False,
    )

    best_visit_code = models.CharField(
        verbose_name="Which study visit code is closest to this appointment date",
        max_length=15,
        null=True,
        blank=False,
        help_text=(
            "Click SAVE to let the EDC suggest. Once selected, interim appointments will "
            "be flagged as not required/missed."
        ),
    )

    visitschedule = models.ForeignKey(
        VisitSchedule,
        on_delete=PROTECT,
        verbose_name="Which study visit code is closest to this appointment date",
        max_length=15,
        null=True,
        blank=False,
        help_text=(
            "Click SAVE to let the EDC suggest. Once selected, interim appointments will "
            "be flagged as not required/missed."
        ),
    )

    class Meta:
        abstract = True
        verbose_name = "Next Appointment"
        verbose_name_plural = "Next Appointments"
