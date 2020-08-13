"""NRC a ics"""

from os import path, makedirs, getcwd
from schedule import Schedule, valid_nrc

OUT_DIRECORY = "output"
OUT_FILE = "calendario.ics"


print(
    """
█   █ ███  ████            █
██  █ █  █ █       ▄▄▄    ▄▄  ▄▄▄ ▄▄▄▄
█ █ █ ███  █         █    ▀█  █▀▀ █▀▀▀
█  ██ █  █ █       █▀█     █  █   ▀▀▀█
█   █ █  █ ████    █▄█    ███ ███ ████
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
        # TODO: display the names of the imported courses
        # print("Cursos importados:", *results.courses, sep="\n", end="\n" * 2)

        print("¿Cargar el siguiente calendario?")
        print(results.display(True))

        opt = input("S/N -> ").strip().lower()

        if opt in ["s", "y"]:
            makedirs(OUT_DIRECORY, exist_ok=True)
            with open(path.join(OUT_DIRECORY, OUT_FILE), "w", encoding="utf-8") as file:
                file.write(results.to_ics())
            print("Calendario guardado en", path.join(OUT_DIRECORY, OUT_FILE))
            print(path.join(getcwd(), OUT_DIRECORY, OUT_FILE))
