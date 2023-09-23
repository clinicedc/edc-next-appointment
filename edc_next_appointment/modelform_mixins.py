from __future__ import annotations

from datetime import date, datetime
from zoneinfo import ZoneInfo

from django import forms
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from edc_appointment.constants import NEW_APPT, SKIPPED_APPT
from edc_appointment.utils import get_appointment_by_datetime
from edc_utils import convert_php_dateformat
from edc_utils.date import to_local
from edc_visit_schedule.schedule.window import ScheduledVisitWindowError


class NextAppointmentModelFormMixin:
    def clean(self):
        cleaned_data = super().clean()
        self.validate_suggested_date_with_future_appointments()
        self.validate_suggested_visit_code()
        return cleaned_data

    @property
    def suggested_date(self) -> date | None:
        return self.cleaned_data.get("appt_date")

    @property
    def suggested_visit_code(self) -> str | None:
        return getattr(
            self.cleaned_data.get("visitschedule"),
            "visit_code",
            self.cleaned_data.get("visitschedule"),
        )

    def validate_suggested_date_with_future_appointments(self):
        if self.suggested_date and self.related_visit.appointment.next.appt_status not in [
            NEW_APPT,
            SKIPPED_APPT,
        ]:
            if (
                self.suggested_date
                != to_local(self.related_visit.appointment.next.appt_datetime).date()
            ):
                next_appt = self.related_visit.appointment.next
                date_format = convert_php_dateformat(settings.SHORT_DATE_FORMAT)
                next_appt_date = to_local(next_appt.appt_datetime).date().strftime(date_format)
                raise forms.ValidationError(
                    {
                        "appt_date": _(
                            "Invalid. Next visit report already submitted. Expected "
                            "`%(dt)s`. See `%(visit_code)s`."
                        )
                        % {
                            "dt": next_appt_date,
                            "visit_code": next_appt.visit_code,
                        }
                    }
                )

        if (
            self.suggested_date
            and self.related_visit.appointment.next.appt_status not in [NEW_APPT, SKIPPED_APPT]
            and self.suggested_date
            > to_local(self.related_visit.appointment.next.appt_datetime).date()
        ):
            next_appt = self.related_visit.appointment.next
            date_format = convert_php_dateformat(settings.SHORT_DATE_FORMAT)
            raise forms.ValidationError(
                {
                    "appt_date": _(
                        "Invalid. Expected a date before appointment "
                        "`%(visit_code)s` on "
                        "%(dt_str)s."
                    )
                    % {
                        "visit_code": next_appt.visit_code,
                        "dt_str": to_local(next_appt.appt_datetime)
                        .date()
                        .strftime(date_format),
                    }
                }
            )

    def validate_suggested_visit_code(self):
        if suggested_date := self.suggested_date:
            subject_visit = self.cleaned_data.get("subject_visit")
            try:
                appointment = get_appointment_by_datetime(
                    self.as_datetime(suggested_date),
                    subject_identifier=subject_visit.subject_identifier,
                    visit_schedule_name=subject_visit.visit_schedule.name,
                    schedule_name=subject_visit.schedule.name,
                    raise_if_in_gap=False,
                )
            except ScheduledVisitWindowError as e:
                raise forms.ValidationError({"appt_date": str(e)})
            if not appointment:
                raise forms.ValidationError(
                    {"appt_date": _("Invalid. Must be within the followup period.")}
                )
            elif appointment == subject_visit.appointment:
                raise forms.ValidationError(
                    {
                        "appt_date": (
                            _(
                                "Invalid. Cannot be within window period "
                                "of current appointment."
                            )
                        )
                    }
                )

            if (
                self.suggested_visit_code
                and self.suggested_visit_code != appointment.visit_code
            ):
                date_format = convert_php_dateformat(settings.SHORT_DATE_FORMAT)
                raise forms.ValidationError(
                    {
                        "visitschedule": _(
                            "Expected %(visit_code)s using %(dt_str)s from above."
                        )
                        % {
                            "visit_code": appointment.visit_code,
                            "dt_str": suggested_date.strftime(date_format),
                        }
                    }
                )

    @staticmethod
    def as_datetime(dt: date) -> datetime:
        return datetime(dt.year, dt.month, dt.day, 23, 59, 59, tzinfo=ZoneInfo("UTC"))
