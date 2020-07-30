# NRC a iCalendar

Script que toma los horarios de Buscacursos UC a partir de una lista
de NRCs y crea un calendario en formato iCalendar.

## Uso

```cmd
pip install -r requirements.txt
cd src
main.py
```

Hay que entregar una lista de NRC válidos.
Con estos, el programa obtendrá el horario en Buscacursos,
el cual mostrará en la consola.
Luego se elige si se guarda o no el horario.
El archivo se creará en el directorio `src/output`.

## Limitaciones

- El programa usa caracteres especiales de color y de `utf-8`, puede
que no se muestren correctamente en la consola.
- En el horario de la consola no se muestran topes de horario.
- Módulos juntos no se agrupan.
- No hay configuración. (Solo se puede configurar editando el código).
