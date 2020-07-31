"Scraper of BuscaCursos UC"

import datetime as dt
import re
import urllib.request as rq

from collections import defaultdict
from html import unescape as html_unescape
from itertools import product
from multiprocessing.dummy import Pool as ThreadPool
from typing import Iterable


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

NCR_INDEX = 0
TEACHER_INDEX = 10

MATCH_RESULT_ROW = {"class": re.compile("resultados")}

TODAY = dt.date.today()
CURRENT_YEAR = TODAY.year
CURRENT_SEMESTER = TODAY.month // 6 + 1


def _get_soup(url: str) -> BeautifulSoup:
    with rq.urlopen(url) as response:
        html = html_unescape(response.read().decode("utf-8"))
    return BeautifulSoup(html, "lxml")  # Hay que instalar lxml!


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
            modules = defaultdict(list)
            for mod_row in data.find_all("tr"):
                # TODO: Guardar la sala en el que se realizan las clases
                mod, type_, _ = map(lambda r: r.text.strip(), mod_row.find_all("td"))
                days, hours = mod.split(":")
                days = days.split("-")
                hours = hours.split(",")
                modules[type_].extend(product(days, hours))
            row_data[name] = modules
            continue
        # Ve los profesores y los separa
        if name == COURSES_COLUMNS_NAMES[TEACHER_INDEX]:
            row_data[name] = tuple(data.text.strip().split(", "))
            continue
        # La información es un str
        text = data.text.strip()
        # Se ve si el resultado es numérico y no NCR
        if name != COURSES_COLUMNS_NAMES[NCR_INDEX] and text.isnumeric():
            text = int(text)
        # En cualquier otro caso guarda el resultado tal cual
        row_data[name] = text
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


def get_specific_courses(nrc_codes: Iterable = ()) -> list:
    "Get multiple courses from BuscaCursos UC with their respective NCR"
    with ThreadPool() as pool:
        return pool.map(lambda nrc: get_courses(nrc=nrc), nrc_codes)
