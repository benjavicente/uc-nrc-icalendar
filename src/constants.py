"""Constants"""

from string import Template
from collections import OrderedDict

import arrow


# iCalendar

FIRST_DAY = arrow.get(2021, 3, 15)

LAST_DAY = arrow.get(2021, 7, 9).shift(days=1)

MODULE_LENGTH = {"hours": 1, "minutes": 20}

MODULE_START_TIME = {
    1: {"hour": 8, "minute": 30},
    2: {"hour": 10, "minute": 00},
    3: {"hour": 11, "minute": 30},
    4: {"hour": 14, "minute": 00},
    5: {"hour": 15, "minute": 30},
    6: {"hour": 17, "minute": 00},
    7: {"hour": 18, "minute": 30},
    8: {"hour": 20, "minute": 00},
}

HOLIDAYS = (
    arrow.get(2021, 4, 2),    # Viernes santo
    arrow.get(2021, 4, 3),    # Sábado Santo
    arrow.get(2021, 5, 1),    # Día del trabajo
    arrow.get(2021, 5, 10),   # Semana de receso
    arrow.get(2021, 5, 11),   # Semana de receso
    arrow.get(2021, 5, 12),   # Semana de receso
    arrow.get(2021, 5, 13),   # Semana de receso
    arrow.get(2021, 5, 14),   # Semana de receso
    arrow.get(2021, 5, 15),   # Semana de receso
    arrow.get(2021, 5, 21),   # Día de las Glorias Navales
    arrow.get(2021, 6, 28),   # San Pedro y San Pablo
    arrow.get(2021, 7, 16),   # Virgen del Carmen
    arrow.get(2021, 8, 15),   # La Asunción de la Virgen
    arrow.get(2021, 9, 18),   # 1ra Junta Nacional de Gobierno
    arrow.get(2021, 9, 19),   # Día de las Glorias del Ejército
    arrow.get(2021, 10, 4),   # Semana de receso
    arrow.get(2021, 10, 5),   # Semana de receso
    arrow.get(2021, 10, 6),   # Semana de receso
    arrow.get(2021, 10, 7),   # Semana de receso
    arrow.get(2021, 10, 8),   # Semana de receso
    arrow.get(2021, 10, 9),   # Semana de receso
    arrow.get(2021, 10, 11),  # Encuentro de Dos Mundos
    arrow.get(2021, 10, 31),  # Día Nacional de las Iglesias Evangélicas y Protestantes
    arrow.get(2021, 11, 1),   # Día de Todos los Santos

)

ICS_ARROW_DATETIME_FORMAT = "YYYYMMDDTHHmmss"
ICS_ARROW_TIME_FORMAT = "HHmmss"
ICS_ARROW_DATE_FORMAT = "YYYYMMDD"

BC_TO_ICS_DAY_NAMES = OrderedDict(
    L="MO", M="TU", W="WE", J="TH", V="FR", S="SA", D="SU"
)

CALENDAR_TEMPLETE = Template(
    "\n".join(
        (
            "BEGIN:VCALENDAR",
            "PRODID:-//benjavicente//uc-nrc-a-ics//CL",
            "VERSION:2.0",
            "CALSCALE:GREGORIAN",
            "X-WR-TIMEZONE:America/Santiago",
            "BEGIN:VTIMEZONE",
            "TZID:America/Santiago",
            "X-LIC-LOCATION:America/Santiago",
            "BEGIN:STANDARD",
            "TZOFFSETFROM:-0300",
            "TZOFFSETTO:-0400",
            "TZNAME:-04",
            "DTSTART:19700405T000000",
            "RRULE:FREQ=YEARLY;BYMONTH=4;BYDAY=1SU",
            "END:STANDARD",
            "BEGIN:DAYLIGHT",
            "TZOFFSETFROM:-0400",
            "TZOFFSETTO:-0300",
            "TZNAME:-03",
            "DTSTART:19700906T000000",
            "RRULE:FREQ=YEARLY;BYMONTH=9;BYDAY=1SU",
            "END:DAYLIGHT",
            "END:VTIMEZONE",
            "${events}",
            "END:VCALENDAR",
        )
    )
)

EVENT_TEMPLETE = Template(
    "\n".join(
        (
            "BEGIN:VEVENT",
            "DTSTART;TZID=America/Santiago:${start}",
            "DTEND;TZID=America/Santiago:${end}",
            "RRULE:FREQ=WEEKLY;UNTIL=${last};BYDAY=${days}",
            "${ex_dates}",
            "DTSTAMP:${now}",
            "UID:${uid}",
            "DESCRIPTION:${description}",
            "SUMMARY:${summary}",
            "END:VEVENT",
        )
    )
)

DAY_EVENT_TEMPLATE = Template(
    "\n".join(
        (
            "BEGIN:VEVENT",
            "DTSTART;TZID=America/Santiago:${day}",
            "DTEND;TZID=America/Santiago:${next_day}",
            "DTSTAMP:${now}",
            "UID:${uid}",
            "SUMMARY:${summary}",
            "END:VEVENT",
        )
    )
)

EX_DATE_TEMPLATE = Template("EXDATE;TZID=America/Santiago:${date}T${start}")
