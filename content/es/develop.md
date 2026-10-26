```sh
python -m unittest discover -s tests -v
python -m readme_builder build readme.json --output . --check
python -m readme_builder check .
```

Las pruebas usan archivos temporales y procesos CLI reales: salida determinista,
protección de cambios, límites de rutas, escape, temas, migración idempotente,
ejemplos de código, Unicode, BOM/CRLF y códigos de error. CI ejecuta las mismas
comprobaciones en Windows, Linux y macOS. Consulta [qué se ejecutó](docs/STATUS.md).

Lee [CONTRIBUTING.md](CONTRIBUTING.md) antes de añadir un componente. Cada componente
debe ser portable, accesible y útil fuera de un solo repositorio.

[MIT](LICENSE) · Iconos y componentes SVG originales de Roberto Gallardo.
