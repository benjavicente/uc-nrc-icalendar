# Proceso de empaquetado

Primero, hay que entrar en el entorno virtual

En windows

```cmd
env\Scripts\activate
```

En macOS y Linux

```bash
env/bin/activate
```

Para empaquetar el ejecutable con el _spec_ se usa

```bash
python -m PyInstaller --clean "build/uc-nrc-icalendar.spec"
```
