"""Funciones de bajo nivel para invocar FFmpeg de forma segura.

Todas las llamadas usan listas de argumentos (nunca ``shell=True``) para
evitar problemas de seguridad al construir comandos con rutas o textos
proporcionados por el usuario.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path


class FFmpegError(RuntimeError):
    """Se lanza cuando un comando de FFmpeg/FFprobe falla."""


def _ejecutar(comando: list[str]) -> subprocess.CompletedProcess:
    resultado = subprocess.run(
        comando,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if resultado.returncode != 0:
        raise FFmpegError(
            f"El comando falló ({' '.join(comando)}):\n{resultado.stderr[-4000:]}"
        )
    return resultado


def verificar_ffmpeg_disponible() -> None:
    """Lanza un error claro si FFmpeg/FFprobe no están instalados."""

    for binario in ("ffmpeg", "ffprobe"):
        try:
            subprocess.run(
                [binario, "-version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
            )
        except (FileNotFoundError, subprocess.CalledProcessError) as exc:
            raise FFmpegError(
                f"No se encontró '{binario}' en el sistema. "
                "Instala FFmpeg (https://ffmpeg.org/download.html) antes de continuar."
            ) from exc


def obtener_duracion(video_path: str | Path) -> float:
    """Devuelve la duración (en segundos) de un archivo de video/audio."""

    comando = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "json",
        str(video_path),
    ]
    resultado = _ejecutar(comando)
    datos = json.loads(resultado.stdout)
    return float(datos["format"]["duration"])


def envolver_texto(texto: str, ancho_px: int, tamano_fuente: int) -> str:
    """Inserta saltos de línea para que ``texto`` no se salga del cuadro.

    ``drawtext`` no ajusta el texto automáticamente: una línea más ancha
    que el video se corta en los bordes. Se estima el ancho de cada
    palabra con un factor fijo (fuentes bold sans rondan ~0.58 * tamaño de
    fuente por carácter) y se arma cada línea greedy, respetando ese límite.
    """

    ancho_util = ancho_px * 0.86
    max_caracteres = max(int(ancho_util / (tamano_fuente * 0.58)), 1)

    lineas: list[str] = []
    linea_actual = ""
    for palabra in texto.split():
        candidata = f"{linea_actual} {palabra}".strip()
        if len(candidata) <= max_caracteres or not linea_actual:
            linea_actual = candidata
        else:
            lineas.append(linea_actual)
            linea_actual = palabra
    if linea_actual:
        lineas.append(linea_actual)

    return "\n".join(lineas)


def escapar_texto_drawtext(texto: str) -> str:
    """Escapa caracteres especiales para el filtro ``drawtext`` de FFmpeg."""

    reemplazos = {
        "\\": "\\\\",
        ":": "\\:",
        "'": "\u2019",  # se sustituye por una comilla tipográfica
        "%": "\\%",
    }
    texto_escapado = texto
    for original, nuevo in reemplazos.items():
        texto_escapado = texto_escapado.replace(original, nuevo)
    return texto_escapado


def recortar_y_ajustar_escena(
    clip_origen: str | Path,
    salida: str | Path,
    ancho: int,
    alto: int,
    fps: int,
    inicio: float = 0.0,
    duracion: float | None = None,
    texto: dict | None = None,
    ruta_fuente: str | None = None,
) -> None:
    """Genera un clip de escena listo para concatenar.

    Recorta el clip de origen (``inicio``/``duracion``), lo escala y
    recorta ("cover") al tamaño objetivo, aplica una transición de
    entrada/salida (fade) y, opcionalmente, agrega un texto superpuesto.
    """

    filtros = [
        f"scale={ancho}:{alto}:force_original_aspect_ratio=increase",
        f"crop={ancho}:{alto}",
        f"fps={fps}",
        "fade=t=in:st=0:d=0.4",
    ]

    if duracion is not None:
        filtros.append(f"fade=t=out:st={max(duracion - 0.4, 0):.2f}:d=0.4")

    if texto:
        posicion = texto.get("posicion", "bottom")
        tamano_fuente = texto.get("tamano_fuente", 56)
        contenido_envuelto = envolver_texto(
            texto.get("contenido", ""), ancho, tamano_fuente
        )
        contenido = escapar_texto_drawtext(contenido_envuelto)
        color = texto.get("color", "white")
        color_borde = texto.get("color_borde", "black")
        aparece_en = float(texto.get("aparece_en", 0))
        duracion_texto = texto.get("duracion_texto")

        posiciones = {
            "top": "x=(w-text_w)/2:y=h*0.12",
            "center": "x=(w-text_w)/2:y=(h-text_h)/2",
            "bottom": "x=(w-text_w)/2:y=h*0.78",
        }
        coordenadas = posiciones.get(posicion, posiciones["bottom"])

        fin_texto = (
            aparece_en + float(duracion_texto)
            if duracion_texto is not None
            else (duracion if duracion is not None else 1e9)
        )

        drawtext = (
            "drawtext=text='" + contenido + "'"
            f":{coordenadas}"
            f":fontsize={tamano_fuente}"
            f":fontcolor={color}"
            f":borderw=3:bordercolor={color_borde}"
            ":box=1:boxcolor=black@0.35:boxborderw=20"
            f":enable='between(t,{aparece_en},{fin_texto})'"
        )
        if ruta_fuente:
            drawtext += f":fontfile='{ruta_fuente}'"

        filtros.append(drawtext)

    comando = [
        "ffmpeg",
        "-y",
        "-ss",
        str(inicio),
    ]
    if duracion is not None:
        comando += ["-t", str(duracion)]
    comando += [
        "-i",
        str(clip_origen),
        "-vf",
        ",".join(filtros),
        "-c:v",
        "libx264",
        "-preset",
        "veryfast",
        "-an",
        str(salida),
    ]
    _ejecutar(comando)


def concatenar_escenas(escenas: list[str | Path], salida: str | Path) -> None:
    """Concatena una lista de clips de video (sin audio) en un solo archivo."""

    if not escenas:
        raise ValueError("No hay escenas para concatenar.")

    directorio = Path(salida).parent
    lista_path = directorio / "_lista_concat.txt"
    with open(lista_path, "w", encoding="utf-8") as f:
        for escena in escenas:
            ruta_absoluta = Path(escena).resolve()
            f.write(f"file '{ruta_absoluta.as_posix()}'\n")

    comando = [
        "ffmpeg",
        "-y",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(lista_path),
        "-c",
        "copy",
        str(salida),
    ]
    _ejecutar(comando)
    lista_path.unlink(missing_ok=True)


def exportar_para_plataforma(
    entrada: str | Path,
    salida: str | Path,
    ancho: int,
    alto: int,
    fps: int,
    video_bitrate: str,
    audio_bitrate: str,
    audio_origen: str | Path | None = None,
) -> None:
    """Genera el archivo final codificado según la especificación de la plataforma.

    Si se indica ``audio_origen`` (por ejemplo música de fondo), se mezcla
    con el video final. Si no, el resultado se exporta sin pista de audio.
    """

    comando = ["ffmpeg", "-y", "-i", str(entrada)]
    if audio_origen:
        comando += ["-i", str(audio_origen)]

    comando += [
        "-vf",
        f"scale={ancho}:{alto}:force_original_aspect_ratio=increase,crop={ancho}:{alto},fps={fps}",
        "-c:v",
        "libx264",
        "-preset",
        "medium",
        "-b:v",
        video_bitrate,
        "-pix_fmt",
        "yuv420p",
    ]

    if audio_origen:
        comando += [
            "-c:a",
            "aac",
            "-b:a",
            audio_bitrate,
            "-shortest",
        ]
    else:
        comando += ["-an"]

    comando.append(str(salida))
    _ejecutar(comando)
