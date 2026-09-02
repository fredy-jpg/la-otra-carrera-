# 🎬 Reel Generator — La Otra Carrera

Herramienta de automatización de video para generar **reels educativos**
listos para publicar en **Instagram, TikTok y YouTube Shorts**, pensada
para que cualquier persona del equipo de *La Otra Carrera* pueda crear
contenido de impacto **sin experiencia en edición de video**.

## ¿Qué hace?

1. Toma uno o más videos "brutos" (sin editar) como entrada.
2. Aplica un **template** que define escenas, recortes, transiciones y
   textos educativos ya diseñados para la comunicación de La Otra Carrera.
3. Automatiza la edición básica: recorte de clips, transiciones (fade),
   textos superpuestos y armado del reel completo.
4. Exporta el resultado final optimizado para la plataforma elegida
   (Instagram Reel, TikTok o YouTube Shorts — todas en formato vertical
   1080x1920).

## Requisitos

- **Python 3.9+**
- **FFmpeg** y **FFprobe** instalados y disponibles en el `PATH`.

### Instalar FFmpeg

- **Ubuntu/Debian**: `sudo apt-get install ffmpeg`
- **macOS (Homebrew)**: `brew install ffmpeg`
- **Windows**: descarga los binarios desde [ffmpeg.org](https://ffmpeg.org/download.html) y agrégalos al `PATH`.

Verifica la instalación con:

```bash
ffmpeg -version
```

No se necesita instalar ninguna librería de Python adicional: el proyecto
usa solo la librería estándar (ver `requirements.txt`).

## Uso rápido

Desde la carpeta `reel-generator/`:

```bash
# Ver los templates disponibles
python generate_reel.py --list-templates

# Ver las plataformas de exportación soportadas
python generate_reel.py --list-plataformas

# Generar un reel usando el template "educativo_basico" con 3 clips
python generate_reel.py \
  --template templates/educativo_basico.json \
  --clips ruta/a/clip1.mp4 ruta/a/clip2.mp4 ruta/a/clip3.mp4 \
  --output output/mi_reel.mp4 \
  --plataforma instagram_reel
```

Si no indicas `--plataforma`, se usa la plataforma recomendada por el
template. Si no indicas `--output`, el resultado se guarda en
`output/reel.mp4`.

### Opciones principales

| Opción | Descripción |
| --- | --- |
| `--template` | Ruta al archivo JSON del template (o solo el nombre si está en `templates/`). |
| `--clips` | Uno o más videos de origen, en el orden que espera el template. |
| `--output` | Ruta del archivo `.mp4` final. |
| `--plataforma` | `instagram_reel`, `tiktok` o `youtube_shorts`. |
| `--musica` | (Opcional) Ruta a una pista de audio para usar como música de fondo. |
| `--fuente` | (Opcional) Ruta a un archivo `.ttf` para los textos, si la fuente por defecto no está disponible en tu sistema. |

## Estructura del proyecto

```
reel-generator/
├── generate_reel.py       # CLI principal
├── requirements.txt
├── core/                  # Lógica reutilizable
│   ├── config.py          # Especificaciones de plataformas y fuentes
│   ├── ffmpeg_utils.py    # Wrappers seguros sobre comandos de FFmpeg
│   └── template_engine.py # Carga y aplica templates JSON
├── templates/             # Templates de reels (JSON) — ver templates/README.md
│   ├── educativo_basico.json
│   ├── testimonio_impacto.json
│   └── promocion_programa.json
├── examples/
│   └── ejemplo_uso.py     # Ejemplo de uso programático (sin CLI)
└── output/                # Reels generados (ignorado por git)
```

## Sistema modular de templates

Cada template es un archivo JSON independiente que describe una secuencia
de escenas (qué clip usar, cuánto dura, qué texto mostrar y cuándo). Para
crear un nuevo template **no se necesita escribir código**: basta con
agregar un nuevo archivo `.json` en `templates/` siguiendo la misma
estructura. Consulta [`templates/README.md`](templates/README.md) para
el detalle completo de los campos disponibles.

Templates incluidos:

- **`educativo_basico.json`** — gancho + explicación + llamado a la acción.
- **`testimonio_impacto.json`** — historia real de impacto de una persona beneficiada.
- **`promocion_programa.json`** — anuncio corto de una convocatoria o programa.

## Uso programático

Si prefieres integrar la generación de reels dentro de otro script o
automatización, puedes usar el módulo `core` directamente:

```python
from core import template_engine

template = template_engine.Template.desde_archivo("templates/educativo_basico.json")
template_engine.generar_reel(
    template=template,
    clips=["clip1.mp4", "clip2.mp4", "clip3.mp4"],
    salida="output/mi_reel.mp4",
    plataforma="instagram_reel",
)
```

Ver `examples/ejemplo_uso.py` para un ejemplo completo y ejecutable.

## Formatos de exportación soportados

| Plataforma | Resolución | FPS | Duración máx. recomendada |
| --- | --- | --- | --- |
| Instagram Reel (`instagram_reel`) | 1080x1920 | 30 | 90s |
| TikTok (`tiktok`) | 1080x1920 | 30 | 180s |
| YouTube Shorts (`youtube_shorts`) | 1080x1920 | 30 | 60s |

## Solución de problemas

- **`No se encontró 'ffmpeg' en el sistema`**: instala FFmpeg siguiendo las
  instrucciones de arriba y asegúrate de que esté en el `PATH`.
- **Los textos no se ven o FFmpeg falla en `drawtext`**: indica una fuente
  válida con `--fuente /ruta/a/tu-fuente.ttf`.
- **Quiero cambiar los textos de un template**: no necesitas tocar código,
  edita directamente el archivo `.json` correspondiente en `templates/`.
