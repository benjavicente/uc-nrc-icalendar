# NRC a iCalendar

Script que toma los horarios de BuscaCursos UC a partir de una lista
de NRCs y crea un calendario en formato iCalendar que puede ser [importado a Google Calendar.][gg-import]

No crea eventos en los feriados (incluyendo la semana de receso).
Inician desde el 10 de Agosto hasta el 4 de Diciembre (inclusive).

Incluye las fechas de las evaluaciones si es que estas están
disponibles en BuscaCursos.

## Descargar aplicación

### [Windows] (46MB)

La aplicación puede ser bloqueada por SmartScreen al ejecutarla por
primera vez. Al solicitar más información se mostrará la opción para
ejecutarlo de todas formas.

## Descarga y uso por git

### Obtener el repositorio

```cmd
git clone https://github.com/benjavicente/uc-nrc-icalendar.git
cd uc-nrc-icalendar
```

### Crear un entorno virtual (opcional)

[Guía de entornos virtuales][venv-guide]

En Windows:
```cmd
py -m venv env
env\Scripts\activate
```

En macOS y Linux>

```shell
python3 -m venv env
source env/bin/activate # en bash/zsh
. env/bin/activate.fish # en fish
```

### Descarga de módulos

```shell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Uso

Para mostrar el interfaz de la consola: `src/main.py`.

Para mostrar el GUI ejecuta `src/gui.py`.



[windows]: https://github.com/benjavicente/uc-nrc-icalendar/releases/latest/download/uc-nrc-icalendar.exe
[gg-import]: https://calendar.google.com/calendar/r/settings/export
[venv-guide]: https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/#creating-a-virtual-environment
