from __future__ import annotations

from datetime import date, datetime
from zoneinfo import ZoneInfo

from django import forms
from django.conf import settings
from edc_appointment.constants import MISSED_APPT, NEW_APPT
from edc_appointment.utils import get_appointment_by_datetime
from edc_utils import convert_php_dateformat
from edc_utils.date import to_local
from edc_visit_schedule.schedule.window import ScheduledVisitWindowError


class NextAppointmentModelFormMixin:
    def clean(self):
        cleaned_data = super().clean()
        self.validate_appt_date_with_next()
        self.validate_best_visit_code()
        return cleaned_data

    def validate_appt_date_with_next(self):
        if (
            self.related_visit.appointment.next.appt_status != NEW_APPT
            and self.related_visit.appointment.next.appt_timing != MISSED_APPT
        ):
            if (
                self.cleaned_data.get("appt_date")
                != to_local(self.related_visit.appointment.next.appt_datetime).date()
            ):
                next_appt = self.related_visit.appointment.next
                date_format = convert_php_dateformat(settings.SHORT_DATE_FORMAT)
                next_appt_date = to_local(next_appt.appt_datetime).date().strftime(date_format)
                raise forms.ValidationError(
                    {
                        "appt_date": (
                            f"Invalid. Next visit report already submitted. Expected "
                            f"`{next_appt_date}`. See {next_appt.visit_code}."
                        )
                    }
                )

        if (
            self.cleaned_data.get("appt_date")
            and self.related_visit.appointment.next.appt_status != NEW_APPT
            and self.related_visit.appointment.next.appt_timing != MISSED_APPT
            and self.cleaned_data.get("appt_date")
            > to_local(self.related_visit.appointment.next.appt_datetime).date()
        ):
            next_appt = self.related_visit.appointment.next
            date_format = convert_php_dateformat(settings.SHORT_DATE_FORMAT)
            raise forms.ValidationError(
                {
                    "appt_date": (
                        f"Invalid. Expected a date before next appointment "
                        f"{next_appt.visit_code} on "
                        f"{to_local(next_appt.appt_datetime).date().strftime(date_format)}."
                    )
                }
            )

    def validate_best_visit_code(self):
        if appt_date := self.cleaned_data.get("appt_date"):
            subject_visit = self.cleaned_data.get("subject_visit")
            try:
                appointment = get_appointment_by_datetime(
                    self.as_appt_datetime(appt_date),
                    subject_identifier=subject_visit.subject_identifier,
                    visit_schedule_name=subject_visit.visit_schedule.name,
                    schedule_name=subject_visit.schedule.name,
                    raise_if_in_gap=False,
                )
            except ScheduledVisitWindowError as e:
                raise forms.ValidationError({"appt_date": str(e)})
            if not appointment:
                raise forms.ValidationError(
                    {"appt_date": "Invalid. Must be within the followup period."}
                )
            elif appointment == subject_visit.appointment:
                raise forms.ValidationError(
                    {
                        "appt_date": (
                            "Invalid. Cannot be within window period of current appointment."
                        )
                    }
                )

            if (
                self.cleaned_data.get("visitschedule")
                and self.cleaned_data.get("visitschedule").visit_code != appointment.visit_code
            ):
                date_format = convert_php_dateformat(settings.SHORT_DATE_FORMAT)
                raise forms.ValidationError(
                    {
                        "visitschedule": (
                            f"Expected {appointment.visit_code} "
                            f"using {appt_date.strftime(date_format)} from above."
                        )
                    }
                )

    @staticmethod
    def as_appt_datetime(appt_date: date) -> datetime:
        return datetime(
            appt_date.year,
            appt_date.month,
            appt_date.day,
            23,
            59,
            59,
            tzinfo=ZoneInfo("UTC"),
        )
