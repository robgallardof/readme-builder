| Componente | Para qué sirve |
|---|---|
| **Hero** | Marca geométrica propia, identidad clara y una promesa breve. Variantes claras y oscuras. |
| **Sección** | Franjas numeradas con iconos de línea, encabezados reales y anclas estables. |
| **Separador** | Una línea con degradado que separa ideas sin recargar la página. |
| **Características** | Hasta seis tarjetas con beneficios escritos por ti e iconos propios. |
| **Terminal** | Un ejemplo mostrado como widget; nunca una ejecución inventada. |
| **Métricas** | Hasta cuatro datos declarados. Si son mediciones, conserva su evidencia. |
| **Flujo** | Una secuencia compacta de hasta seis pasos. |
| **Pie** | Una firma final que comparte el lenguaje visual. |

Tres paletas: **Aurora** (violeta/cian), **Ember** (naranja/rosa), **Ocean** (azul/verde).
Los componentes y los iconos originales tienen licencia MIT. Incluye **39 iconos Lucide** con sus avisos ISC / MIT ([atribución](THIRD_PARTY_NOTICES.md)). Sin fuentes remotas, scripts,
píxeles de seguimiento ni servidores externos de imágenes. Consulta los iconos:

```sh
python -m readme_builder icons
```

La [guía de componentes](docs/COMPONENTS.md) describe límites de texto y revisión visual.

### Movimiento y alineacion

Las filas de banners, widgets, separadores y pies se generan centradas. El modo
`"motion": "subtle"` es el predeterminado: dos recorridos decorativos que terminan
en cuatro segundos. El texto y los datos no se desplazan. `"ambient"` usa un efecto
continuo lento; `"off"` genera SVG estaticos. Se respeta `prefers-reduced-motion`.

```sh
python -m readme_builder animate assets/banner.svg                # vista previa
python -m readme_builder animate assets/banner.svg --write
python -m readme_builder animate assets/banner.svg --preset off --write
```

Usa nombres como `lucide-brain-circuit`, `lucide-shield-check`,
`lucide-clapperboard` o `lucide-layout-template`. Los iconos son locales:
sin CDN ni JavaScript. Las animaciones SVG/SMIL existentes se conservan.

La firma es optativa: indica tu logo y perfil en `branding`. La firma queda al final. Cuando se pida un diagrama, prioriza Archify e importa sus SVG claros y oscuros ya verificados.

Los titulos y las descripciones usan Markdown para adaptarse al ancho disponible. Solo el fondo de la portada tiene movimiento: los separadores, iconos, diagramas y la firma de cierre permanecen estaticos.
