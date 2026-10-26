```sh
# Genera los README del builder en inglés y español.
python -m readme_builder build readme.json --output .

# Detecta archivos desactualizados sin escribir.
python -m readme_builder build readme.json --output . --check

# Revisa enlaces locales, anclas y presentación.
python -m readme_builder check .

# Crea una hoja local de componentes en ambos modos de color.
python -m readme_builder preview . --output preview.html
```

Edita `readme.json` y `content/`, y vuelve a generar. Un manifiesto SHA-256 protege
los archivos generados frente a cambios manuales accidentales. Detecta cambios y
pertenencia; no es una firma ni sustituye a Git. El generador no elimina recursos antiguos.

`audit RUTA --json` entrega un informe estructurado. `audit` informa sin fallar;
`check` devuelve 1 si encuentra problemas. Las entradas inválidas devuelven 2.
