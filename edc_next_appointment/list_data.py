from edc_constants.constants import (
    ESTIMATED,
    HOSPITAL_NOTES,
    OTHER,
    OUTPATIENT_CARDS,
    PATIENT,
    PATIENT_REPRESENTATIVE,
)

list_data = {
    "edc_next_appointment.infosources": [
        (PATIENT, "Patient"),
        (
            PATIENT_REPRESENTATIVE,
            "Patient representative (e.g., next of kin, relative, guardian)",
        ),
        (HOSPITAL_NOTES, "Hospital notes"),
        (OUTPATIENT_CARDS, "Outpatient cards"),
        (ESTIMATED, "Estimated by research staff"),
        (OTHER, "Other"),
    ],
}
