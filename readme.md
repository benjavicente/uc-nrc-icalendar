# NRC a iCalendar

Script que toma los horarios de BuscaCursos UC a partir de una lista
de NRCs y crea un calendario en formato iCalendar.

## Uso

Utilizando Python 3.7 o superior

```cmd
pip install -r requirements.txt
cd src
main.py
```

Hay que entregar una lista de NRC válidos.
Con estos, el programa obtendrá el horario en BuscaCursos,
el cual mostrará en la consola.
Luego se elige si se guarda o no el horario.
El archivo se creará en el directorio `src/output`.


## TODO

- Configuración más accesible
- :bug: iniciar bien los eventos, evitando el evento adicional que se
crea el primer día
