from __future__ import annotations

from typing import TYPE_CHECKING

from edc_crf.crf_form_validator import CrfFormValidator
from edc_dx_review.utils import raise_if_clinical_review_does_not_exist
from edc_form_validators import INVALID_ERROR

if TYPE_CHECKING:
    from edc_facility.models import HealthFacility


class NextAppointmentFormValidatorMixin(CrfFormValidator):
    def __init__(self, **kwargs):
        self._clinic_days = None
        self._clinic_days_str = None
        self._health_facility = None
        super().__init__(**kwargs)

    def clean(self):
        raise_if_clinical_review_does_not_exist(self.cleaned_data.get("subject_visit"))
        super().clean()

    @property
    def health_facility(self) -> HealthFacility | None:
        if not self._health_facility:
            if self.cleaned_data.get("health_facility"):
                self._health_facility = self.cleaned_data.get("health_facility")
            else:
                raise self.raise_validation_error(
                    {"health_facility": "This field is required."}
                )
        return self._health_facility

    def validate_date_is_on_clinic_day(self):
        if appt_date := self.cleaned_data.get("appt_date"):
            if not self.health_facility.clinic_days:
                if appt_date.isoweekday() > 5:
                    day = "Sat" if appt_date.isoweekday() == 6 else "Sun"
                    raise self.raise_validation_error(
                        {"appt_date": f"Expected Mon-Fri. Got {day}"},
                        INVALID_ERROR,
                    )
            else:
                if appt_date.isoweekday() not in self.health_facility.clinic_days:
                    raise self.raise_validation_error(
                        {
                            "appt_date": (
                                "Invalid clinic day for facility. "
                                f"Expected {self.health_facility.clinic_days_str}. "
                                f"Got {appt_date.strftime('%A')}"
                            )
                        },
                        INVALID_ERROR,
                    )
