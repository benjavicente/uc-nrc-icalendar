"""Horarios"""

from collections import defaultdict
from datetime import date
from uuid import uuid4

import arrow

from scraper import get_multiple_courses


def str_scape(string: str) -> str:
    """Escapa los caracteres especiales de un string"""
    return repr(string).strip("'")


class Module:
    """Módulo"""

    # https://stackoverflow.com/questions/287871/how-to-print-colored-text-in-python
    display_color = True
    color_type = defaultdict(
        lambda: "\033[41m{:^9}\033[0m",
        {
            "CLAS": "\033[41m{:^9}\033[0m",
            "LAB": "\033[44m{:^9}\033[0m",
            "AYU": "\033[42m{:^9}\033[0m",
            "TAL": "\033[45m{:^9}\033[0m",
        },
    )

    def __init__(self, type_: str, course_json):
        self._type = type_
        self._data = course_json

    def __repr__(self):
        return "{Sigla}-{Seccion}".format_map(self._data)

    def __str__(self):
        if self.display_color:
            return self.color_type[self._type].format(repr(self))
        return repr(self)

    @property
    def name(self):
        """Nombre del módulo"""
        if self._type == "CLAS":
            return self._data["Nombre"]
        return self._type + " " + self._data["Nombre"]

    @property
    def description(self):
        """Descripción del módulo"""
        return "\n".join([repr(self), ", ".join(self._data["Profesor"]), self._data["Campus"]])


class Calendar:
    """Calendario compuesto por módulos"""

    def __init__(self):
        self.schedule = defaultdict(list)
        self.courses_names = set()

    def import_courses(self, nrc: set):
        """Importa el horario de los cusos a partir de su NRC"""
        self.schedule.clear()
        self.courses_names.clear()

        courses_list = get_multiple_courses(nrc)

        for course in courses_list:
            self.courses_names.add(course["Nombre"])
            for module_type, modules in course["Modulos"].items():
                for day, mod in modules:
                    self.schedule[day + mod].append(Module(module_type, course))

    def __str__(self):
        # Se crea una tabla
        rep = "  | " + "".join(map(lambda d: format(d, "^11"), "LMWJVS")) + "\n"
        for mod in map(str, range(1, 9)):
            rep += f"{mod} | "
            for day in "LMWJVS":
                courses = self.schedule[day + mod]
                if courses:
                    rep += format(str(courses[0]), "^20")
                else:
                    rep += " " * 11
            rep += "\n"
        return rep

    def to_ics(self) -> str:
        """Retorna un str con el calendario en formato ics"""
        # TODO: Limpiar

        ics_time_format = "YYYYMMDDTHHmmss"
        first_day = arrow.get(date(2020, 8, 10), "Chile/Continental")
        final_day = arrow.get(date(2020, 12, 4), "Chile/Continental")

        first_monday = first_day.shift(weekday=0)
        mod_length = {"hours": 1, "minutes": 20}

        start_time = {
            "1": {"hour": 8, "minute": 30},
            "2": {"hour": 10, "minute": 00},
            "3": {"hour": 11, "minute": 30},
            "4": {"hour": 14, "minute": 00},
            "5": {"hour": 15, "minute": 30},
            "6": {"hour": 17, "minute": 00},
            "7": {"hour": 18, "minute": 30},
            "8": {"hour": 20, "minute": 00},
        }

        holidays = {
            date(2020, 8, 15),  # La Asunción de la Virgen
            date(2020, 9, 18),  # 1ra Junta Nacional de Gobierno
            date(2020, 9, 19),  # Día de las Glorias del Ejército
            date(2020, 9, 21),  # Semana de receso
            date(2020, 9, 22),  # Semana de receso
            date(2020, 9, 23),  # Semana de receso
            date(2020, 9, 24),  # Semana de receso
            date(2020, 9, 25),  # Semana de receso
            date(2020, 9, 26),  # Semana de receso
            date(2020, 10, 12),  # Encuentro de Dos Mundos
            date(2020, 10, 31),  # Día Nacional de las Iglesias Evangélicas y Protestantes
        }

        def remove_holidays(start_arw: arrow.Arrow) -> list:
            """Retorna una lista con los feriados a remover"""
            start = start_arw.format("HHmmss")
            return list(
                map(
                    lambda d: f"EXDATE;TZID=America/Santiago:{d.strftime(r'%Y%m%d')}T{start}",
                    holidays,
                )
            )

        day_index = "LMWJVS".index

        ics = [
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
        ]

        for (day, mod), modules in self.schedule.items():
            for module_info in modules:
                start = first_monday.shift(weekday=day_index(day)).replace(**start_time[mod])
                end = start.shift(**mod_length)
                ics.extend(
                    [
                        "BEGIN:VEVENT",
                        f"DTSTART;TZID=America/Santiago:{start.format(ics_time_format)}",
                        f"DTEND;TZID=America/Santiago:{end.format(ics_time_format)}",
                        (
                            "RRULE:FREQ=WEEKLY;"
                            f"WKST=MO;UNTIL={final_day.to('utc').format(ics_time_format)}Z;"
                            f"BYDAY={start.format('ddd').upper()[:2]}"
                        ),
                        *remove_holidays(start),
                        f"DTSTAMP:{arrow.get().format(ics_time_format)}",
                        f"UID:{str(uuid4())}",
                        f"DESCRIPTION:{str_scape(module_info.description)}",
                        f"SUMMARY:{str_scape(module_info.name)}",
                        "END:VEVENT",
                    ]
                )
        ics.append("END:VCALENDAR")
        return "\n".join(ics)
