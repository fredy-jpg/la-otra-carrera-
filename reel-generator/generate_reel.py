#!/usr/bin/env python3
"""Generador automático de reels educativos para La Otra Carrera.

Uso básico:

    python generate_reel.py --template templates/educativo_basico.json \
        --clips clip1.mp4 clip2.mp4 clip3.mp4 \
        --output output/mi_reel.mp4 \
        --plataforma instagram_reel

Para ver los templates disponibles:

    python generate_reel.py --list-templates

Para ver las plataformas de exportación soportadas:

    python generate_reel.py --list-plataformas
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

DIRECTORIO_BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(DIRECTORIO_BASE))

from core import config, template_engine  # noqa: E402
from core.ffmpeg_utils import FFmpegError  # noqa: E402

DIRECTORIO_TEMPLATES = DIRECTORIO_BASE / "templates"


def listar_templates() -> None:
    templates = template_engine.listar_templates(DIRECTORIO_TEMPLATES)
    if not templates:
        print("No se encontraron templates en", DIRECTORIO_TEMPLATES)
        return

    print("Templates disponibles:\n")
    for t in templates:
        print(f"  - {t.ruta.name}")
        print(f"      Nombre: {t.nombre}")
        print(f"      Descripción: {t.descripcion}")
        print(f"      Plataforma recomendada: {t.plataforma_recomendada}")
        print(f"      Escenas: {len(t.escenas)}\n")


def listar_plataformas() -> None:
    print("Plataformas de exportación disponibles:\n")
    for clave, spec in config.PLATFORM_FORMATS.items():
        print(
            f"  - {clave}: {spec.nombre} "
            f"({spec.ancho}x{spec.alto} @ {spec.fps}fps, "
            f"máx. {spec.duracion_maxima:.0f}s)"
        )


def construir_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Genera reels educativos automáticamente a partir de videos brutos, "
            "usando templates predefinidos para La Otra Carrera."
        )
    )
    parser.add_argument(
        "--template",
        help="Ruta al archivo de template JSON a usar.",
    )
    parser.add_argument(
        "--clips",
        nargs="+",
        help="Rutas a los videos de origen, en el orden que espera el template.",
    )
    parser.add_argument(
        "--output",
        default=str(DIRECTORIO_BASE / "output" / "reel.mp4"),
        help="Ruta del archivo de salida (por defecto: output/reel.mp4).",
    )
    parser.add_argument(
        "--plataforma",
        choices=sorted(config.PLATFORM_FORMATS),
        help=(
            "Plataforma de exportación (instagram_reel, tiktok, youtube_shorts). "
            "Si se omite, se usa la recomendada por el template."
        ),
    )
    parser.add_argument(
        "--musica",
        help="Ruta a un archivo de audio opcional para usar como música de fondo.",
    )
    parser.add_argument(
        "--fuente",
        help="Ruta a un archivo de fuente (.ttf) para los textos. Opcional.",
    )
    parser.add_argument(
        "--list-templates",
        action="store_true",
        help="Muestra los templates disponibles y termina.",
    )
    parser.add_argument(
        "--list-plataformas",
        action="store_true",
        help="Muestra las plataformas de exportación disponibles y termina.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = construir_parser()
    args = parser.parse_args(argv)

    if args.list_templates:
        listar_templates()
        return 0

    if args.list_plataformas:
        listar_plataformas()
        return 0

    if not args.template or not args.clips:
        parser.error("--template y --clips son obligatorios (o usa --list-templates).")

    template_path = Path(args.template)
    if not template_path.is_file():
        # Permite pasar solo el nombre del archivo si está en templates/
        alternativa = DIRECTORIO_TEMPLATES / args.template
        if alternativa.is_file():
            template_path = alternativa
        else:
            print(f"❌ No se encontró el template: {args.template}", file=sys.stderr)
            return 1

    for clip in args.clips:
        if not Path(clip).is_file():
            print(f"❌ No se encontró el clip: {clip}", file=sys.stderr)
            return 1

    try:
        template = template_engine.Template.desde_archivo(template_path)
        salida = template_engine.generar_reel(
            template=template,
            clips=args.clips,
            salida=args.output,
            plataforma=args.plataforma,
            ruta_fuente=args.fuente,
            musica=args.musica,
        )
    except FFmpegError as exc:
        print(f"❌ Error de FFmpeg: {exc}", file=sys.stderr)
        return 1
    except ValueError as exc:
        print(f"❌ Error: {exc}", file=sys.stderr)
        return 1

    print(f"✅ Reel generado correctamente en: {salida}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
