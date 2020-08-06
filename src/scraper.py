"Scraper of BuscaCursos UC"

import datetime as dt
import re
import html

from collections import defaultdict
from itertools import product
from multiprocessing.dummy import Pool as ThreadPool
from typing import Iterable, Tuple

import requests as rq
from bs4 import BeautifulSoup


COURSES_COLUMNS_NAMES = (
    "ncr",
    "code",
    "",
    "",
    "section",
    "",
    "",
    "",
    "",
    "name",
    "teachers",
    "campus",
    "",
    "",
    "",
    "",
    "modules",
    "",
)

MODULE_COLUMNS_NAMES = (
    "type_",
    "module",
    "classroom",
)

NCR_INDEX = 0
TEACHER_INDEX = 10

MATCH_RESULT_ROW = {"class": re.compile("resultados")}

TODAY = dt.date.today()
CURRENT_YEAR = TODAY.year
CURRENT_SEMESTER = TODAY.month // 6 + 1


def _get_soup(url: str, **kwargs) -> BeautifulSoup:
    """Gets a BeautifulSoup from the `url`.
    `kwards` from the Requests API.
    """
    with rq.get(url, **kwargs) as response:
        html_string = html.unescape(response.content.decode("utf-8"))
    return BeautifulSoup(html_string, "lxml")  # Hay que instalar lxml!


def _get_courses_address(**parameters) -> str:
    return (
        "http://buscacursos.uc.cl/"
        "?cxml_semestre={year}-{semester}"
        "&cxml_sigla={code}"
        "&cxml_nrc={nrc}"
        "&cxml_nombre={name}"
        "&cxml_categoria={category}"
        "&cxml_area_fg={area}"
        "&cxml_formato_cur={format}"
        "&cxml_profesor={teacher}"
        "&cxml_campus={campus}"
        "&cxml_unidad_academica={academic_unit}"
    ).format_map(defaultdict(str, parameters))


def _clean_courses_row(row) -> dict:
    row_data = dict()
    for name, data in zip(COURSES_COLUMNS_NAMES, row.find_all("td", recursive=False)):
        # Ve si se omite la columna si no tiene nombre
        if not name:
            continue
        # Ve se hay una tabla (horario)
        table = data.find("table")
        if table:
            modules = list()
            for mod_row in data.find_all("tr"):
                mod, type_, classroom = map(lambda r: r.text.strip(), mod_row.find_all("td"))
                days, hours = mod.split(":")
                if not days or not hours:
                    continue
                if classroom == "(Por Asignar)":
                    classroom = None
                days = days.split("-")
                hours = hours.split(",")
                modules += [
                    dict(zip(MODULE_COLUMNS_NAMES, [type_, m, classroom]))
                    for m in product(days, hours)
                ]
            row_data[name] = modules
            continue
        # Ve los profesores y los separa
        if name == COURSES_COLUMNS_NAMES[TEACHER_INDEX]:
            row_data[name] = tuple(data.text.strip().split(", "))
            continue
        # En cualquier otro caso guarda el resultado tal cual
        row_data[name] = data.text.strip()
    return row_data


def get_courses(semester=CURRENT_SEMESTER, year=CURRENT_YEAR, **parameters) -> list:
    """Get courses a list of courses that matches the given parameters.
    A maximum of 50 courses can be scraped in the same request.

    Parameters:
       year, semester, nrc, code, name, category, area,
       format, teacher, campus, academic_unit
    """
    url = _get_courses_address(semester=semester, year=year, **parameters)
    soup = _get_soup(url)
    results = soup.find_all("tr", MATCH_RESULT_ROW)
    return list(map(_clean_courses_row, results))


def get_specific_courses(nrc_codes: Iterable) -> list:
    "Get multiple courses from BuscaCursos UC with their respective NCR"
    with ThreadPool() as pool:
        return pool.map(lambda nrc: get_courses(nrc=nrc), nrc_codes)


# EXPERIMENTAL

MONTH_NUMBERS = {
    "Enero": 1,
    "Febrero": 2,
    "Marzo": 3,
    "Abril": 4,
    "Mayo": 5,
    "Junio": 6,
    "Julio": 7,
    "Agosto": 8,
    "Septiembre": 9,
    "Octubre": 10,
    "Noviembre": 11,
    "Diciembre": 12,
}


def get_exams(courses: Iterable["code-section"], semester=CURRENT_SEMESTER, year=CURRENT_YEAR):
    """Get the tests from multiple courses"""
    # TODO: cleanup
    cookies = {f"cursosuc-{year}-{semester}": "%2C".join(courses)}
    soup = _get_soup("http://buscacursos.uc.cl/calendarioPruebas.ajax.php", cookies=cookies)

    test_list = list()

    for month_table in soup.find_all("table"):
        month_name, year = month_table.find("th").text.strip().split()
        for month_row in month_table.find_all("tr"):
            for day_cell in month_row.find_all("td"):

                cell_content = day_cell.find_all("div")

                if not cell_content:
                    continue

                day = cell_content[0].text.strip()
                tests = cell_content[1:]

                if not tests:
                    continue

                month = MONTH_NUMBERS[month_name]

                for test in tests:
                    name, course = test.text.split(" \xa0")
                    test_list.append({
                        "name": name,
                        "course_code": course,
                        "date": (int(year), int(month), int(day))
                    })
    return test_list

# Example
if __name__ == "__main__":
    RESULT = get_courses(nrc="16312"), get_courses(nrc="20803")
    from pprint import pprint
    pprint(RESULT)
