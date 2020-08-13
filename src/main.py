"""NRC a ics"""

# Copyright 2020 © Benjamín Vicente
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


from os import path, makedirs, getcwd
from schedule import Schedule, valid_nrc

OUT_DIRECORY = "output"
OUT_FILE = "calendario.ics"


print(
    """
█▙  █ ███▖ ▟██▙             ▐▌
██▙ █ █  █ █▘      ▗▄▄▖    ▄▄▖  ▗▄▄▖ ▗▄▄▖
█▝█▙█ ███▛ █       ▘  █    ▀▜▌  █▛▀▀ █▀▀▀
█ ▝██ █ ▝▙ █▖      ▟▀▜█     ▐▌  █▖   ▝▀▀█
█  ▝█ █  █ ▜██▛    ▜▃▞█    ████ ▜██▛ ▜██▛
"""
)

print("Ingresa los NRC separados por espacios.")

while True:
    acc = input("\nNRCs -> ")

    if not acc:
        break

    nfc_list = acc.split()

    if all(map(valid_nrc, nfc_list)):
        results = Schedule.get(nfc_list)
        print("Cursos importados:", *results.courses, sep="\n", end="\n" * 2)

        print("¿Cargar el siguiente calendario?")
        print(results.display())

        opt = input("S/N -> ").strip().lower()

        if opt in ["S", "s", "Y", "y"]:
            makedirs(OUT_DIRECORY, exist_ok=True)
            with open(path.join(OUT_DIRECORY, OUT_FILE), "w", encoding="utf-8") as file:
                file.write(results.to_ics())
            print("Calendario guardado en", path.join(OUT_DIRECORY, OUT_FILE))
            print(path.join(getcwd(), OUT_DIRECORY, OUT_FILE))
