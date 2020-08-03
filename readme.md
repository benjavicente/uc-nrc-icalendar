# NRC a iCalendar

Script que toma los horarios de BuscaCursos UC a partir de una lista
de NRCs y crea un calendario en formato iCalendar.

No crea eventos en los feriados (incluyendo la semana de receso).
Inician desde el 10 de Agosto hasta el 4 de Diciembre (inclusive).

Los calendarios pueden ser importados a [Google Calendar][gg-import].

## Descargar aplicación

### [Windows] (46.1MB)

La aplicación puede ser bloqueada por SmartScreen al ejecutarla por
primera vez. Al solicitar más información se mostrará la opción para
ejecutarlo de todas formas.

## Descarga y uso por git

### Obtención del repositorio

```cmd
git clone https://github.com/benjavicente/uc-nrc-icalendar.git
cd uc-nrc-icalendar
```

### Creación de un entorno virtual (opcional)

[Guía de entornos virtuales][venv-guide]

En windows

```cmd
py -m venv env
env\Scripts\activate
```

En macOS y Linux

```bash
python3 -m venv env
env/bin/activate
```

### Descarga de módulos

```cmd
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Uso

```cmd
cd src
```

Para mostrar el interfaz de la consola: `main.py`

Para mostrar el GUI: `gui.py`



[windows]: https://github.com/benjavicente/uc-nrc-icalendar/releases/download/v0.3/uc-nrc-icalendar.exe
[gg-import]: https://calendar.google.com/calendar/r/settings/export
[venv-guide]: https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/#creating-a-virtual-environment
