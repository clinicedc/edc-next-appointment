from edc_crf.crf_form_validator import CrfFormValidator
from edc_dx_review.utils import raise_if_clinical_review_does_not_exist
from edc_form_validators import INVALID_ERROR


class NextAppointmentFormValidatorMixin(CrfFormValidator):
    def __init__(self, **kwargs):
        self._clinic_days = None
        super().__init__(**kwargs)

    def clean(self):
        raise_if_clinical_review_does_not_exist(self.cleaned_data.get("subject_visit"))
        super().clean()

    @property
    def clinic_days(self) -> list[int]:
        if not self._clinic_days:
            if self.cleaned_data.get("health_facility"):
                self._clinic_days = self.cleaned_data.get("health_facility").clinic_days
        return self._clinic_days

    def validate_date_is_on_clinic_day(self):
        if appt_date := self.cleaned_data.get("appt_date"):
            if appt_date.isoweekday() > 5:
                day = "Sat" if appt_date.isoweekday() == 6 else "Sun"
                raise self.raise_validation_error(
                    {"appt_date": f"Expected Mon-Fri. Got {day}"},
                    INVALID_ERROR,
                )
        if appt_date and self.cleaned_data.get("subject_visit").site:
            if (
                self.integrated_clinic_days
                and appt_date.isoweekday() not in self.integrated_clinic_days
            ):
                dct = dict(zip([1, 2, 3, 4, 5, 6, 7], ["M", "T", "W", "Th", "F", "Sa", "Su"]))
                expected_days = [v for k, v in dct.items() if k in self.clinic_days]
                raise self.raise_validation_error(
                    {
                        "appt_date": (
                            "Invalid clinic day. "
                            f"Expected {''.join(expected_days)}. "
                            f"Got {appt_date.strftime('%A')}"
                        )
                    },
                    INVALID_ERROR,
                )
