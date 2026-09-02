# Templates de reels

Cada archivo `.json` en esta carpeta define un template reutilizable. El
sistema es **modular**: para agregar un template nuevo solo hace falta
crear un archivo JSON con esta estructura, no se necesita tocar código.

## Estructura de un template

```json
{
  "nombre": "Nombre del template",
  "descripcion": "Para qué sirve este template",
  "plataforma_recomendada": "instagram_reel",
  "escenas": [
    {
      "clip_index": 0,
      "inicio": 0,
      "duracion": 4,
      "texto": {
        "contenido": "Texto que aparece en pantalla",
        "posicion": "top",
        "aparece_en": 0.3,
        "duracion_texto": 3.5,
        "tamano_fuente": 58,
        "color": "white",
        "color_borde": "black"
      }
    }
  ]
}
```

### Campos de cada escena

| Campo | Obligatorio | Descripción |
| --- | --- | --- |
| `clip_index` | Sí | Índice (empezando en 0) del clip de entrada que se usará para esta escena, según el orden en que se pasan los clips al generador. |
| `inicio` | No (por defecto `0`) | Segundo del clip de origen donde empieza a recortarse la escena. |
| `duracion` | No | Duración en segundos de la escena. Si se omite, se usa el clip completo desde `inicio`. |
| `texto` | No | Objeto con el texto superpuesto (ver abajo). Si se omite, la escena no lleva texto. |

### Campos del objeto `texto`

| Campo | Obligatorio | Descripción |
| --- | --- | --- |
| `contenido` | Sí | El texto a mostrar. |
| `posicion` | No (`bottom` por defecto) | `top`, `center` o `bottom`. |
| `aparece_en` | No (`0` por defecto) | Segundos desde el inicio de la escena en que aparece el texto. |
| `duracion_texto` | No | Cuánto tiempo permanece visible el texto. Si se omite, se muestra hasta el final de la escena. |
| `tamano_fuente` | No (`56` por defecto) | Tamaño de fuente en píxeles. |
| `color` | No (`white` por defecto) | Color del texto (nombre válido para FFmpeg, ej. `white`, `yellow`, `#FFAA00`). |
| `color_borde` | No (`black` por defecto) | Color del borde del texto para mejorar la legibilidad. |

## Templates incluidos

- **`educativo_basico.json`**: gancho + explicación + llamado a la acción. Ideal para explicar un concepto.
- **`testimonio_impacto.json`**: presentación + testimonio + cierre inspirador. Ideal para historias reales.
- **`promocion_programa.json`**: anuncio corto para promocionar una convocatoria o programa.

## Crear un nuevo template

1. Copia uno de los archivos existentes como punto de partida.
2. Ajusta el número de escenas, los textos y sus tiempos.
3. Guarda el archivo con un nombre descriptivo dentro de esta carpeta.
4. Ejecútalo con:

   ```bash
   python generate_reel.py --template templates/mi_nuevo_template.json --clips clip1.mp4 clip2.mp4 clip3.mp4 --output output/mi_reel.mp4
   ```

No hace falta registrar el template en ningún otro lugar: `generate_reel.py --list-templates` los detecta automáticamente.
