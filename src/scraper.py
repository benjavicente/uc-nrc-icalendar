"Scraper de buscacursos"

from html import unescape as html_unescape
from collections import defaultdict
from itertools import product
from multiprocessing.dummy import Pool

import urllib.request as rq
import datetime as dt
import re

from bs4 import BeautifulSoup


_COURSES_COLUMNS_NAMES = (
    "NCR",
    "Sigla",
    "",
    "",
    "Seccion",
    "",
    "",
    "",
    "",
    "Nombre",
    "Profesor",
    "Campus",
    "",
    "",
    "",
    "",
    "Modulos",
    "",
)

_MATCH_RESULT_ROW = {"class": re.compile("resultados")}

_TODAY = dt.date.today()
_CURRENT_YEAR = _TODAY.year
_CURRENT_SEMESTER = _TODAY.month // 6 + 1


def _get_soup(url: str) -> BeautifulSoup:
    with rq.urlopen(url) as response:
        html = html_unescape(response.read().decode("utf-8"))
    return BeautifulSoup(html, "lxml")  # Hay que instalar lxml!


def _get_courses_address(**parameters) -> str:
    return (
        "http://buscacursos.uc.cl/"
        "?cxml_semestre={p[year]}-{p[semester]}"
        "&cxml_sigla={p[cod]}"
        "&cxml_nrc={p[nrc]}"
        "&cxml_nombre={p[name]}"
        "&cxml_categoria={p[category]}"
        "&cxml_area_fg={p[area]}"
        "&cxml_formato_cur={p[format]}"
        "&cxml_profesor={p[prof]}"
        "&cxml_campus={p[campus]}"
        "&cxml_unidad_academica={p[academic_unit]}"
        "&cxml_horario_tipo_busqueda={p[special_1]}"
        "&cxml_horario_tipo_busqueda_actividad={p[special_2]}".format(
            p=defaultdict(str, parameters)
        )
    )


def _clean_courses_row(row) -> dict:
    row_data = dict()
    for name, data in zip(_COURSES_COLUMNS_NAMES, row.find_all("td", recursive=False)):
        # Ve si se omite la columna si no tiene nombre
        if not name:
            continue
        # Ve se hay una tabla (horario)
        table = data.find("table")
        if table:
            modules = defaultdict(list)
            for mod_row in data.find_all("tr"):
                mod, mod_type, _ = map(lambda r: r.text.strip(), mod_row.find_all("td"))
                days, hours = mod.split(":")
                days = days.split("-")
                hours = hours.split(",")
                modules[mod_type].extend(product(days, hours))
            row_data[name] = modules
            continue
        # Ve los profesores y los separa
        if name == "Profesor":
            row_data[name] = tuple(data.text.strip().split(", "))
            continue
        # La información es un str
        text = data.text.strip()
        # Se ve si el resultado es numérico y no NCR
        if name != "NCR" and text.isnumeric():
            text = int(text)
        # En cualquier otro caso guarda el resultado tal cual
        row_data[name] = text
    return row_data


def get_courses(semester=_CURRENT_SEMESTER, year=_CURRENT_YEAR, **parameters) -> list:
    "Obtiene los cursos de BuscaCursos, dado los parámetros"
    url = _get_courses_address(semester=semester, year=year, **parameters)
    soup = _get_soup(url)
    results = soup.find_all("tr", _MATCH_RESULT_ROW)
    return tuple(map(_clean_courses_row, results))  # Puede ser lista o set también


def get_multiple_courses(nrc_codes=()):
    "Obtiene multiples cursos a partir de su NFC"
    # https://stackoverflow.com/questions/2846653/how-can-i-use-threading-in-python
    with Pool() as pool:
        # Si no hay resultados (r vacío) no se considera
        return [r[0] for r in pool.map(lambda nrc: get_courses(nrc=nrc), nrc_codes) if r]
