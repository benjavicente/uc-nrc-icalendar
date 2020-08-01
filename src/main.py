"""NRC a ics"""

from os import path, makedirs, getcwd
from schedule import Schedule

out_direcory = "output"
out_file = "calendario.ics"



def valid_nrc(nrc: str) -> bool:
    """Retorna si el nrc es válido"""
    return len(nrc) == 5 and nrc.isdecimal()


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
        RESULTS = Schedule.get_courses(nfc_list)
        print("Cursos importados:", *RESULTS.courses, sep="\n", end="\n" * 2)

        print("Cargar el siguiente calendario?")
        # print(calendar)

        opt = input("Y/N -> ").strip().lower()

        if opt == "y":
            makedirs(out_direcory, exist_ok=True)
            with open(path.join(out_direcory, out_file), "w", encoding="utf-8") as file:
                file.write(RESULTS.to_ics())
            print("Calendario gurdado en", path.join(out_direcory, out_file))
            print(path.join(getcwd(), out_direcory, out_file))
