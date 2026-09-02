"""Motor de templates: aplica un template JSON sobre un conjunto de clips.

El sistema es modular: cada template es un archivo JSON independiente en
``templates/``. Agregar un nuevo template para futuros formatos de reel
no requiere tocar código Python, solo crear un nuevo archivo JSON que siga
la misma estructura (ver ``templates/README.md``).
"""

from __future__ import annotations

import json
import tempfile
from dataclasses import dataclass
from pathlib import Path

from . import config, ffmpeg_utils


@dataclass
class Template:
    """Representa un template de reel cargado desde JSON."""

    nombre: str
    descripcion: str
    plataforma_recomendada: str
    escenas: list[dict]
    ruta: Path

    @classmethod
    def desde_archivo(cls, ruta_template: str | Path) -> "Template":
        ruta_template = Path(ruta_template)
        with open(ruta_template, "r", encoding="utf-8") as f:
            datos = json.load(f)

        escenas = datos.get("escenas", [])
        if not escenas:
            raise ValueError(
                f"El template '{ruta_template}' no define ninguna escena ('escenas')."
            )

        return cls(
            nombre=datos.get("nombre", ruta_template.stem),
            descripcion=datos.get("descripcion", ""),
            plataforma_recomendada=datos.get(
                "plataforma_recomendada", config.PLATAFORMA_POR_DEFECTO
            ),
            escenas=escenas,
            ruta=ruta_template,
        )


def listar_templates(directorio_templates: str | Path) -> list[Template]:
    """Devuelve todos los templates (.json) válidos de un directorio."""

    directorio = Path(directorio_templates)
    templates = []
    for ruta in sorted(directorio.glob("*.json")):
        try:
            templates.append(Template.desde_archivo(ruta))
        except (ValueError, json.JSONDecodeError):
            continue
    return templates


def generar_reel(
    template: Template,
    clips: list[str | Path],
    salida: str | Path,
    plataforma: str | None = None,
    ruta_fuente: str | None = None,
    musica: str | Path | None = None,
) -> Path:
    """Genera un reel aplicando ``template`` sobre ``clips``.

    Cada escena del template hace referencia a un clip de entrada mediante
    ``clip_index`` (posición dentro de la lista ``clips``). El resultado
    final se codifica según la especificación de ``plataforma``.
    """

    ffmpeg_utils.verificar_ffmpeg_disponible()

    plataforma = plataforma or template.plataforma_recomendada
    if plataforma not in config.PLATFORM_FORMATS:
        disponibles = ", ".join(config.PLATFORM_FORMATS)
        raise ValueError(
            f"Plataforma '{plataforma}' no reconocida. Usa una de: {disponibles}"
        )
    spec = config.PLATFORM_FORMATS[plataforma]

    fuente = config.obtener_fuente_disponible(ruta_fuente)

    salida = Path(salida)
    salida.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="reel_generator_") as tmp:
        tmp_dir = Path(tmp)
        rutas_escenas: list[Path] = []

        for indice, escena in enumerate(template.escenas):
            clip_index = escena.get("clip_index", 0)
            if clip_index >= len(clips):
                raise ValueError(
                    f"La escena {indice} referencia clip_index={clip_index}, "
                    f"pero solo se proporcionaron {len(clips)} clip(s)."
                )

            clip_origen = clips[clip_index]
            salida_escena = tmp_dir / f"escena_{indice:03d}.mp4"

            ffmpeg_utils.recortar_y_ajustar_escena(
                clip_origen=clip_origen,
                salida=salida_escena,
                ancho=spec.ancho,
                alto=spec.alto,
                fps=spec.fps,
                inicio=float(escena.get("inicio", 0)),
                duracion=escena.get("duracion"),
                texto=escena.get("texto"),
                ruta_fuente=fuente,
            )
            rutas_escenas.append(salida_escena)

        concatenado = tmp_dir / "concatenado.mp4"
        ffmpeg_utils.concatenar_escenas(rutas_escenas, concatenado)

        ffmpeg_utils.exportar_para_plataforma(
            entrada=concatenado,
            salida=salida,
            ancho=spec.ancho,
            alto=spec.alto,
            fps=spec.fps,
            video_bitrate=spec.video_bitrate,
            audio_bitrate=spec.audio_bitrate,
            audio_origen=musica,
        )

    return salida
