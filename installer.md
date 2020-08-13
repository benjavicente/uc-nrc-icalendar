# Proceso de empaquetado

Primero, hay que entrar en el entorno virtual.

En Windows:

```cmd
env/Scripts/activate
```

En macOS y Linux:

```bash
source env/bin/activate # en bash/zsh
. env/bin/activate.fish # en fish
```

Para empaquetar el ejecutable con el _spec_ se usa:

```bash
pyinstaller --clean "build/pyinstaller.spec"
```