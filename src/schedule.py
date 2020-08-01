"""Schedule of Buscacursos UC"""

from __future__ import annotations

from dataclasses import dataclass
from operator import attrgetter, itemgetter
from typing import Iterable, Set
from uuid import uuid4

import arrow

from constants import (
    CALENDAR_TEMPLETE,
    BC_TO_ICS_DAY_NAMES,
    EVENT_TEMPLETE,
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
from scraper import get_specific_courses


def scape_str(string: str) -> str:
    """Scapes a string"""
    return repr(string).strip("'")


def get_ex_dates(start: arrow.Arrow) -> str:
    """Get a str with EXDATES of the iCalendar"""
    return "\n".join(
        map(
            lambda h, s=start: EX_DATE_TEMPLATE.substitute(
                {"date": h.format(ICS_ARROW_DATE_FORMAT), "start": s.format(ICS_ARROW_TIME_FORMAT),}
            ),
            HOLIDAYS,
        )
    )


@dataclass(frozen=True)
class Module:
    """Module of a course"""

    day: str
    mod: str
    type_: str
    classroom: str
    _metadata: dict

    @property
    def code(self):
        """Code of the course"""
        return "-".join(itemgetter("code", "section")(self._metadata))

    @property
    def name(self):
        """Name of the module"""
        if self.type_ == "CLAS":
            return self._metadata["name"]
        return " ".join((self.type_, self._metadata["name"]))

    @property
    def description(self):
        """Description of the module"""
        return "\n".join(
            (self.code, ", ".join(self._metadata["teachers"]), self._metadata["campus"])
        )

    def __hash__(self):
        return hash((self.day, self.mod, self.type_, self.classroom))

    def __repr__(self):
        return f"<{type(self).__name__}({self.day}{self.mod}:{self.code})>"


class Event:
    """Group of modules that makes one VEvent.
    Modules must have the same type and code.
    """

    def __init__(self, main_module: Module, modules: Set[Module]):
        """
        main_module: module where the VEvent will get the metadata.
        modules: a set of modules that makes the VEvent.
        """
        self._modules = modules
        self.__main_module = main_module
        self.days = {main_module.day}
        self.mods = {main_module.mod}

    # TODO: mejor manera de acceder a code, type_, name & description
    @property
    def code(self):
        return self.__main_module.code

    @property
    def type_(self):
        return self.__main_module.type_

    @property
    def name(self):
        return self.__main_module.name

    @property
    def description(self):
        return self.__main_module.description

    @classmethod
    def new(cls, module: Module) -> Event:
        """Makes a new event form one module"""
        return cls(module, {module})

    def __repr__(self):
        join = "".join
        return f"<{type(self).__name__}({join(self.days)}{join(self.mods)}:{self.code})>"

    def __iadd__(self, other_event: Event):
        self._modules |= other_event._modules
        self.days |= other_event.days
        self.mods |= other_event.mods

    def is_expandable_to(self, other_event: Event) -> bool:
        """Checks if a event can be expanded"""
        # Example:
        # A C ~ D
        # B ~ ~ E
        # ~ F ~ ~
        # - A can expand vertically to B if they are the same code and type
        # - AB can expand horizontally to DE if hey are the same code and type
        # - AC can expand horizontally to D if hey are the same code and type
        # - AB can't expand to C because columns must have the same size
        # - C cant expand to F because there is a gap in the column

        if self.code != other_event.code or self.type_ != other_event.type_:
            return False

        # TODO: testing
        vert = list(map(int, self.mods | other_event.mods))
        return (
            all((n in vert for n in range(min(vert), max(vert) + 1)))
            if self.days == other_event.days
            else self.mods == other_event.mods
        )

    def to_ics(self) -> str:
        """Returns the representation of the object in the iCalendar format"""
        first_module = str(min(map(int, self.mods)))
        last_module = str(max(map(int, self.mods)))

        # TODO: funciona para todo el calendario excepto a la primera semana
        # TODO: debido a que todos los eventos parten en el primer día de clases
        # TODO: esto se puede solucionar creando un día base en el primer día
        # TODO: que realmente hay clases en ese evento, remplazando `FIRST DAY`

        # base_day = FIRST_DAY.shift(weekday=BC_TO_ICS_DAY_NAMES.keys().index())

        start = FIRST_DAY.replace(**MODULE_START_TIME[first_module])
        end = FIRST_DAY.replace(**MODULE_START_TIME[last_module]).shift(**MODULE_LENGTH)

        last = LAST_DAY
        days = ",".join((BC_TO_ICS_DAY_NAMES[d] for d in self.days if d in BC_TO_ICS_DAY_NAMES))

        mapping = {
            "start": start.format(ICS_ARROW_DATETIME_FORMAT),
            "end": end.format(ICS_ARROW_DATETIME_FORMAT),
            "last": last.format(ICS_ARROW_DATETIME_FORMAT),
            "days": days,
            "ex_dates": get_ex_dates(start),
            "now": arrow.get().format(ICS_ARROW_DATETIME_FORMAT),
            "uid": uuid4(),
            "description": scape_str(self.description),
            "summary": scape_str(self.name),
        }
        return EVENT_TEMPLETE.substitute(mapping)


class Schedule:
    """Container of courses with their modules"""

    def __init__(self):
        self.modules = set()
        self.courses = set()
        self._events = None

    @classmethod
    def get_courses(cls, ncr_list: Iterable) -> Schedule:

        new_schedule = cls()
        results = get_specific_courses(ncr_list)
        for result in (r[0] for r in results if r):
            # Agrega el nombre del curso al set de nombre
            new_schedule.courses.add(result["name"])
            for module in result["modules"]:
                # Agrega el módulo al set de módulos
                (day, mod), type_, classroom = itemgetter("mod", "type_", "classroom")(module)
                new_schedule.modules.add(Module(day, mod, type_, classroom, result))
        return new_schedule

    def display(self, show_color: bool = False) -> str:
        """Shows the module in a string table-like format"""
        # TODO
        pass

    def _modules_to_events(self):
        """Takes the set of modules and creates a list of events"""
        self._events = list()
        day_events = list()
        # Primero se crean los eventos de cada día, expandiendolos si es posible
        for d in "LMWJV":
            events_in_the_day = list()

            for m in map(str, range(1, 9)):
                # Obtiene los módulos en el día y mod correspondiente
                modules = filter(lambda x: attrgetter("day", "mod")(x) == (d, m), self.modules)
                for new_event in map(Event.new, modules):
                    # Revisa si se puede expandir con los otros eventos del día
                    can_be_expanded = False

                    for other_event in events_in_the_day:
                        if other_event.is_expandable_to(new_event):
                            can_be_expanded = True
                            # Se modifica el evento en el lugar
                            other_event += new_event
                            break

                    if not can_be_expanded:
                        events_in_the_day.append(new_event)

            day_events.append(events_in_the_day)

        # Luego se ve si algún evento de un día puede expandirse a otro
        # TODO: ver si se está iterando correctamente y cambiar los nombres (testing)
        for day1, list1 in enumerate(day_events):
            for day2 in range(len(day_events) - 1 - day1):
                for event1 in list1:
                    for event2 in day_events[day2]:
                        if event1.is_expandable_to(event2):
                            event1 += event2
                            day_events[day2].remove(event2)
                            break
            # Una vez terminado el día se agregan los eventos a la lista principal
            self._events.extend(list1)

    def to_ics(self) -> str:
        """Returns the representation of the object in the iCalendar format"""
        self._modules_to_events()
        mapping = {"events": "\n".join(map(Event.to_ics, self._events))}
        return CALENDAR_TEMPLETE.substitute(mapping)


if __name__ == "__main__":
    from pprint import pprint
    RESULT = Schedule.get_courses(["11349", "20803", "16183", "12481"])
    pprint(RESULT.courses)
    print(RESULT.to_ics())