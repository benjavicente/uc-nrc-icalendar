"""NRC a ics"""

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

print("Ingresar los NRC separados por espacios")

while True:
    acc = input("\nNRC -> ")

    if not acc:
        break

    nfc_list = acc.split()

    if all(map(valid_nrc, nfc_list)):
        RESULTS = Schedule.get(nfc_list)
        print("Cursos importados:", *RESULTS.courses, sep="\n", end="\n" * 2)

        print("Cargar el siguiente calendario?")
        print(RESULTS.display())

        opt = input("Y/N -> ").strip().lower()

        if opt == "y":
            makedirs(OUT_DIRECORY, exist_ok=True)
            with open(path.join(OUT_DIRECORY, OUT_FILE), "w", encoding="utf-8") as file:
                file.write(RESULTS.to_ics())
            print("Calendario gurdado en", path.join(OUT_DIRECORY, OUT_FILE))
            print(path.join(getcwd(), OUT_DIRECORY, OUT_FILE))
