from dateutil.relativedelta import relativedelta
from django.contrib.auth.models import User
from django.test import TestCase
from edc_appointment.models import Appointment
from edc_facility import import_holidays
from edc_reference import site_reference_configs
from edc_utils import get_utcnow
from edc_visit_schedule import site_visit_schedules
from edc_visit_schedule.apps import populate_visit_schedule
from edc_visit_tracking.utils import get_related_visit_model_cls

from next_appointment_app.models import SubjectConsent
from next_appointment_app.visit_schedules import visit_schedule


class TestNextAppointment(TestCase):
    def setUp(self):
        import_holidays()
        self.user = User.objects.create_superuser("user_login", "u@example.com", "pass")

        site_visit_schedules._registry = {}
        site_visit_schedules.loaded = False
        site_visit_schedules.register(visit_schedule)

        populate_visit_schedule()

        site_reference_configs.register_from_visit_schedule(
            visit_models={"edc_appointment.appointment": "next_appointment_app.subjectvisit"}
        )
        self.subject_identifier = "101-40990029-4"
        identity = "123456789"
        subject_consent = SubjectConsent.objects.create(
            subject_identifier=self.subject_identifier,
            consent_datetime=get_utcnow() - relativedelta(days=10),
            identity=identity,
            confirm_identity=identity,
            dob=get_utcnow() - relativedelta(years=25),
        )

        # put subject on schedule
        _, schedule = site_visit_schedules.get_by_onschedule_model(
            "next_appointment_app.onschedule"
        )
        schedule.put_on_schedule(
            subject_identifier=subject_consent.subject_identifier,
            onschedule_datetime=subject_consent.consent_datetime,
        )

    def test_ok(self):
        self.assertEqual(5, Appointment.objects.all().count())
        get_related_visit_model_cls()
