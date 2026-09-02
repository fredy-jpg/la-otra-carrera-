"""Ejemplo de uso programático del generador de reels.

Este script muestra cómo usar el módulo ``core`` directamente desde
Python (sin pasar por la CLI), útil si quieres integrar la generación de
reels dentro de otro proyecto o automatización.

Antes de ejecutarlo, coloca tus propios videos en ``examples/clips/`` o
ajusta las rutas de ``CLIPS`` más abajo.
"""

from __future__ import annotations

import sys
from pathlib import Path

DIRECTORIO_BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(DIRECTORIO_BASE))

from core import template_engine  # noqa: E402

# Clips de origen, en el orden que espera el template
# "educativo_basico.json" (3 escenas -> 3 clips).
CLIPS = [
    DIRECTORIO_BASE / "examples" / "clips" / "clip_1.mp4",
    DIRECTORIO_BASE / "examples" / "clips" / "clip_2.mp4",
    DIRECTORIO_BASE / "examples" / "clips" / "clip_3.mp4",
]

TEMPLATE = DIRECTORIO_BASE / "templates" / "educativo_basico.json"
SALIDA = DIRECTORIO_BASE / "output" / "ejemplo_educativo.mp4"


def main() -> None:
    faltantes = [str(c) for c in CLIPS if not c.is_file()]
    if faltantes:
        print("⚠️  Coloca los siguientes clips de ejemplo antes de continuar:")
        for f in faltantes:
            print(f"   - {f}")
        print(
            "\nPuedes usar tus propios videos cortos (mp4) con esos nombres, "
            "o editar CLIPS en este script para apuntar a tus archivos."
        )
        return

    template = template_engine.Template.desde_archivo(TEMPLATE)
    resultado = template_engine.generar_reel(
        template=template,
        clips=CLIPS,
        salida=SALIDA,
        plataforma="instagram_reel",
    )
    print(f"✅ Reel de ejemplo generado en: {resultado}")


if __name__ == "__main__":
    main()
