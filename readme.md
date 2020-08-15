# NRC a iCalendar

Aplicación que toma los horarios de BuscaCursos UC a partir de una
lista de NRCs y crea un calendario en formato iCalendar que puede
ser [importado a Google Calendar.][gg-import]

No crea eventos en los feriados (incluyendo la semana de receso).
Inician desde el 10 de Agosto hasta el 4 de Diciembre (inclusive).

Incluye las fechas de las evaluaciones si es que estas están
disponibles en BuscaCursos.

## Descargar aplicación

### [Windows] (45MB) - [MacOS] (36MB)

> :warning: La aplicación puede ser bloqueada al ejecutarla
> por primera vez ya que esta no tiene una firma digital.
> NO SE GARANTIZA QUE ESTA FUNCIONE.

## Descargar con git

### Obtener el repositorio

```cmd
git clone https://github.com/benjavicente/uc-nrc-icalendar.git
cd uc-nrc-icalendar
```

### Crear un entorno virtual (opcional, recomendado)

[Guía de entornos virtuales][venv-guide]

En Windows:

```cmd
py -m venv .env
.env\Scripts\activate
```

En macOS y Linux:

```shell
python3 -m venv .env
source .env/bin/activate  # en bash/zsh
. .env/bin/activate.fish  # en fish
```

### Descarga de módulos

```shell
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -r optional-requirements.txt
```

### Uso

```shell
cd src
console.py  # para ejecutar en la consola
gui.py      # para ejecutar en el gui
```

### Empaquetamiento

```shell
cd src
python -m PyInstaller --clean "build/uc-nrc-icalendar.spec"
```


[windows]: https://github.com/benjavicente/uc-nrc-icalendar/releases/latest/download/windows.zip
[macOS]: https://github.com/benjavicente/uc-nrc-icalendar/releases/latest/download/macos.zip
[gg-import]: https://calendar.google.com/calendar/r/settings/export
[venv-guide]: https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/#creating-a-virtual-environment
