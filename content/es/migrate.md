Si ya tienes un README que te gusta, empieza con una simulación:

```sh
python -m readme_builder migrate /ruta/al/proyecto/README.md
python -m readme_builder migrate /ruta/al/proyecto/README.md --write
python -m readme_builder check /ruta/al/proyecto
```

Los emojis decorativos y los shortcodes reconocidos se convierten en iconos SVG locales.
Los ejemplos dentro de bloques de código y el código en línea permanecen intactos.
Las etiquetas de Mermaid pasan a texto limpio porque no admiten estas imágenes de
forma portable. Se conservan alias de los encabezados, UTF-8 BOM y saltos CRLF/LF.

La auditoría detecta enlaces locales rotos, conflictos de merge y emojis decorativos
restantes. No visita enlaces remotos ni demuestra que las afirmaciones del proyecto
sean ciertas. Revisa el diff en Markdown complejo: es un escáner conservador, no un
parser completo. Conserva un commit antes de una migración grande.
