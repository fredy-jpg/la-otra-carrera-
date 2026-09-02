"""Configuración de formatos de exportación y valores por defecto.

Este módulo centraliza las especificaciones técnicas de cada plataforma
(Instagram Reels, TikTok, YouTube Shorts) para que el resto del sistema
no tenga que conocer esos detalles.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PlatformSpec:
    """Especificación técnica de exportación para una plataforma."""

    nombre: str
    ancho: int
    alto: int
    fps: int
    duracion_maxima: float  # segundos
    video_bitrate: str
    audio_bitrate: str


# Todas las plataformas objetivo usan formato vertical 9:16 (1080x1920),
# pero se manejan como specs independientes por si en el futuro cambian
# límites de duración o bitrate recomendado.
PLATFORM_FORMATS: dict[str, PlatformSpec] = {
    "instagram_reel": PlatformSpec(
        nombre="Instagram Reel",
        ancho=1080,
        alto=1920,
        fps=30,
        duracion_maxima=90,
        video_bitrate="4M",
        audio_bitrate="128k",
    ),
    "tiktok": PlatformSpec(
        nombre="TikTok",
        ancho=1080,
        alto=1920,
        fps=30,
        duracion_maxima=180,
        video_bitrate="4M",
        audio_bitrate="128k",
    ),
    "youtube_shorts": PlatformSpec(
        nombre="YouTube Shorts",
        ancho=1080,
        alto=1920,
        fps=30,
        duracion_maxima=60,
        video_bitrate="6M",
        audio_bitrate="192k",
    ),
}

# Plataforma que se usa cuando no se especifica ninguna.
PLATAFORMA_POR_DEFECTO = "instagram_reel"

# Paleta de colores sugerida para "La Otra Carrera" (usada en los textos
# generados por los templates). Se puede sobreescribir en cada template.
COLOR_TEXTO_DEFECTO = "white"
COLOR_BORDE_DEFECTO = "black"

# Posibles rutas donde suele encontrarse una fuente utilizable por FFmpeg
# (drawtext requiere una ruta a un archivo .ttf/.otf). Se usa la primera
# que exista en el sistema, salvo que el usuario indique una propia.
RUTAS_FUENTE_CANDIDATAS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "C:/Windows/Fonts/arialbd.ttf",
]


def obtener_fuente_disponible(fuente_personalizada: str | None = None) -> str | None:
    """Devuelve la ruta a una fuente utilizable por FFmpeg (drawtext).

    Si ``fuente_personalizada`` se indica y existe, se usa esa. En caso
    contrario se busca entre las rutas candidatas conocidas. Si no se
    encuentra ninguna, se devuelve ``None`` (FFmpeg usará su fuente por
    defecto, lo cual puede fallar según la instalación).
    """

    import os

    if fuente_personalizada and os.path.isfile(fuente_personalizada):
        return fuente_personalizada

    for ruta in RUTAS_FUENTE_CANDIDATAS:
        if os.path.isfile(ruta):
            return ruta

    return None
