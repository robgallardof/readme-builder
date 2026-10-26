**Python 3.11+ y Git. Nada más para ejecutar el generador.**

```sh
git clone https://github.com/robgallardof/readme-builder.git
cd readme-builder
python -m readme_builder build examples/project.json --output demo
```

Abre `demo/README.md` y edita una copia de [la configuración de ejemplo](examples/project.json).
Define nombre, descripción, tema, idioma y secciones. El contenido puede escribirse
directamente en JSON o leerse desde archivos Markdown locales. Consulta el
[contrato de autoría](docs/CONFIGURATION.md).

La carpeta de salida contiene Markdown y SVG portables. Copia los archivos generados
a tu proyecto o genera allí después de revisar las rutas. El generador rechaza
sobrescribir archivos que no le pertenecen; `--force` es una excepción explícita.
