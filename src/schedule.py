"""Schedule of Buscacursos UC"""

from __future__ import annotations

from operator import attrgetter, itemgetter
from typing import Iterable
from uuid import uuid4
from collections import namedtuple

import arrow

from constants import (
    CALENDAR_TEMPLETE,
    BC_TO_ICS_DAY_NAMES,
    EVENT_TEMPLETE,
    DAY_EVENT_TEMPLATE,
    FIRST_DAY,
    ICS_ARROW_DATETIME_FORMAT,
    ICS_ARROW_TIME_FORMAT,
    ICS_ARROW_DATE_FORMAT,
    LAST_DAY,
    HOLIDAYS,
    EX_DATE_TEMPLATE,
    MODULE_START_TIME,
    MODULE_LENGTH,
)

from scraper import get_specific_courses, get_exams

def scape_str(string: str) -> str:
    """Escapes a string"""
    return repr(string).strip("'")


def get_ex_dates(start: arrow.Arrow) -> str:
    """Get a string with ExDates of the iCalendar"""
    # TODO: retornar solo los feriados que estén en el mismo día de la semana
    return "\n".join(
        map(
            lambda h, s=start: EX_DATE_TEMPLATE.substitute(
                {
                    "date": h.format(ICS_ARROW_DATE_FORMAT),
                    "start": s.format(ICS_ARROW_TIME_FORMAT),
                }
            ),
            HOLIDAYS,
        )
    )


def valid_nrc(nrc: str) -> bool:
    """Checks if aa string is a valid NRC"""
    return len(nrc) == 5 and nrc.isdecimal()


Exam = namedtuple("Exam", ("name", "date"))
Event = namedtuple("Event", ("days", "mods", "type_", "classroom"))
Module = namedtuple("Module", ("code", "type_"))


class Course:
    """Course"""

    def __init__(self, data: dict):
        self.data = data
        self.exams = list()

    def __hash__(self):
        return hash(self.data["ncr"])

    def __repr__(self):
        return f"{type(self).__name__}({self.code_section})"

    @property
    def code_section(self):
        """Code and section"""
        return "-".join((self.data["code"], self.data["section"]))

    @property
    def description(self):
        """Description of a course"""
        return "\n".join(
            (self.data["code"], ", ".join(self.data["teachers"]), self.data["campus"])
        )

    def to_ics(self):
        """Transforms the Course to the iCalendar format"""
        # TODO: esto se puede mejorar considerablemente
        # TODO: ordenar variables
        ics = list()

        # Primero se crean los eventos de las clases

        # Extensión vertical
        week_events = list()
        for day in "LMWJVS":
            last_event = None
            events_in_the_day = list()
            for mod in map(str, range(1, 9)):
                mathed_modules = [
                    m for m in self.data["modules"] if m["module"] == (day, mod)
                ]
                for module in mathed_modules:
                    if last_event:
                        tp_l = attrgetter("type_", "classroom")(last_event)
                        tp_m = itemgetter("type_", "classroom")(module)
                        if tp_l == tp_m:
                            last_event.mods.append(mod)
                            continue
                    last_event = Event(
                        [day], [mod], module["type_"], module["classroom"]
                    )
                    events_in_the_day.append(last_event)
            week_events.append(events_in_the_day)

        # Extensión horizontal
        events = list()
        for day1, list1 in enumerate(week_events):
            for day2 in range(day1 + 1, len(week_events)):
                for event1 in list1:
                    for event2 in week_events[day2]:
                        compare = attrgetter("type_", "classroom")
                        if compare(event1) == compare(event2):
                            event1.days.extend(event2.days)
                            week_events[day2].remove(event2)
                            break
            events.extend(list1)

        # Se crean los eventos ics de los módulos
        for event in events:
            first_module = min(map(int, event.mods))
            last_module = max(map(int, event.mods))

            day_number = list(BC_TO_ICS_DAY_NAMES).index(event.days[0])
            base_day = FIRST_DAY.shift(weekday=day_number)
            start = base_day.replace(**MODULE_START_TIME[first_module])
            end = base_day.replace(**MODULE_START_TIME[last_module]).shift(
                **MODULE_LENGTH
            )

            days = ",".join((BC_TO_ICS_DAY_NAMES[d] for d in event.days))
            name_prefix = "" if event.type_ == "CLAS" else f"{event.type_} "

            mapping = {
                "start": start.format(ICS_ARROW_DATETIME_FORMAT),
                "end": end.format(ICS_ARROW_DATETIME_FORMAT),
                "last": LAST_DAY.format(ICS_ARROW_DATETIME_FORMAT),
                "days": days,
                "ex_dates": get_ex_dates(start),
                "now": arrow.get().format(ICS_ARROW_DATETIME_FORMAT),
                "uid": uuid4(),
                "description": scape_str(self.description),
                "summary": scape_str(name_prefix + self.data["name"]),
            }

            ics.append(EVENT_TEMPLETE.substitute(mapping))

        # Se crean los eventos de las evaluaciones

        for exam in self.exams:
            date = arrow.get(*exam.date)
            name = " ".join((exam.name, self.data["name"]))
            mapping = {
                "day": date.format(ICS_ARROW_DATETIME_FORMAT),
                "next_day": date.shift(days=1).format(ICS_ARROW_DATETIME_FORMAT),
                "days": days,
                "now": arrow.get().format(ICS_ARROW_DATETIME_FORMAT),
                "uid": uuid4(),
                "summary": name,
            }
            ics.append(DAY_EVENT_TEMPLATE.substitute(mapping))

        return "\n".join(ics)


class Schedule:
    """Schedule of courses"""

    def __init__(self, courses: set):
        self.courses = courses

    def __repr__(self):
        str_courses = ",".join(map(repr, self.courses))
        return f"{type(self).__name__}({str_courses})"

    @classmethod
    def get(cls, ncr_list: Iterable) -> Schedule:
        """Get a new instance of Schedule with the given courses"""
        results = get_specific_courses(ncr_list)
        courses = {Course(r[0]) for r in results if r}
        exams = get_exams(map(attrgetter("code_section"), courses))

        # Se añaden las evaluaciones a los cursos
        for exam in exams:
            for course in courses:
                if exam["course_code"] == course.data["code"]:
                    course.exams.append(Exam(exam["name"], exam["date"]))

        return Schedule(courses)

    def get_table(self) -> list:
        """Gets the table representing the modules in the schedule"""
        table = [[[None for i in range(6)]] for j in range(8)]
        day_index = "LMWJVS".index

        for course in self.courses:
            for module in course.data["modules"]:
                day, mod = module["module"]
                i_day = day_index(day)
                i_mod = int(mod) - 1

                # Ve si hay un espacio en las filas existentes
                has_space = False
                for row in table[i_mod]:
                    if not row[i_day]:
                        # Se agrega el evento en el espacio
                        row[i_day] = Module(course.code_section, module["type_"])
                        has_space = True
                        break

                # Si no existe se agrega una fila
                if not has_space:
                    table[i_mod].append([None for i in range(6)])
                    table[i_mod][-1][i_mod] = Module(
                        course.code_section, module["type_"]
                    )

        return table

    def display(self, show_color: bool = False) -> str:
        """Shows the module in a string table-like format"""
        # TODO: color (colorama)
        table = self.get_table()
        # Se hace el string de la tabla
        output = "  ║" + "│".join(map(lambda r: r.center(11), "LMWJVS")) + "\n"
        for mod_number, mod_group in enumerate(table):
            for i, row in enumerate(mod_group):
                str_row = map(lambda r: r.code if r else str(), row)
                output += "  ║" if i else f"{mod_number + 1} ║"
                output += "│".join(map(lambda r: r.center(11), str_row))
                output += "\n" if mod_number != len(table) - 1 else ""
        return output

    def to_ics(self) -> str:
        """Returns the representation of the object in the iCalendar format"""
        mapping = {"events": "\n".join([c.to_ics() for c in self.courses])}
        return CALENDAR_TEMPLETE.substitute(mapping)


if __name__ == "__main__":
    x = Schedule.get(["20803"])
    # print(x.to_ics())
    print(x.display(), sep="\n")
