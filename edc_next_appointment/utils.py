from __future__ import annotations

from dateutil.relativedelta import relativedelta
from django.conf import settings


def get_max_rdelta_to_next_appointment():
    max_months = settings.INTECOMM_MAX_MONTHS_TO_NEXT_APPT
    return relativedelta(months=max_months)


# def visit_code_choices() -> tuple[tuple[str, str]]:
#     visit_codes = list[str]
#     for visit_schedule in site_visit_schedules.visit_schedules.values():
#         for schedule in visit_schedule.schedules:
#             visit_codes.extend([v.code for v in schedule.visits])
#     # codes = ["1000"]
#     # for i in range(1, 13):
#     #     codes.append(get_visit_code(i))
#     # return tuple([(code, code) for code in codes])
#     return tuple([(code, code) for code in visit_codes])
