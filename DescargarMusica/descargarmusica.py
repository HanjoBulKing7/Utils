"""
descargar_musica.py
-------------------
Descarga canciones de YouTube por género usando yt-dlp.
Filtra compilaciones, mixes y videos largos.
Lleva registro de lo descargado para nunca repetir.

Requisitos:
    pip install yt-dlp
    ffmpeg instalado y en PATH (winget install ffmpeg)

Uso básico:
    python descargarmusica.py                        # 1 ronda, 3 por género
    python descargarmusica.py --rondas 10            # 10 rondas, 3 por género
    python descargarmusica.py --rondas 5 --por-ronda 2   # 5 rondas, 2 por género
"""

import subprocess
import sys
import json
import os
import re
import argparse
import time

# ─── CONFIGURACIÓN ────────────────────────────────────────────────────────────

CARPETA_SALIDA = "D:\\"             # ← letra de tu USB
ARCHIVO_REGISTRO = "registro_descargados.json"  # se guarda junto al script
DURACION_MAX_SEGUNDOS = 420          # 7 min — filtra mixes/compilaciones
DURACION_MIN_SEGUNDOS = 90           # 1.5 min — filtra intros raras

PALABRAS_PROHIBIDAS = [
    "mix", "hora", "hours", "playlist", "completo", "top 10", "top 5",
    "top10", "top5", "compilation", "compilacion", "compilación",
    "lo mejor", "grandes exitos", "grandes éxitos", "best of",
    "nonstop", "non stop", "radio", "en vivo", "live", "karaoke",
    "cover", "instrumental", "lyrics only", "visualizer only",
    "full album", "álbum completo", "album completo",
]

GENEROS = {
    "Banda":     ["banda sinaloense cancion", "banda el recodo sencillo", "banda ms cancion", 
                  "la arrolladora cancion", "banda sinaloense popular", "el yaki cancion",
                  "edwin luna cancion", "banda la trakalosa", "los recoditos cancion"],

    "Metal":     ["metallica cancion", "rammstein song", "iron maiden cancion", 
                  "system of a down song", "ozzy osbourne song", "black sabbath song",
                  "judas priest song", "megadeth song", "slayer song"],

    "Corridos":  ["corridos tumbados sencillo", "natanael cano cancion", "peso pluma sencillo", 
                  "junior h cancion", "tito doble p song", "eslabon armado cancion",
                  "luis r conriquez cancion", "gabito ballesteros cancion", "oscar maydon cancion"],

    "Reggaeton": ["bad bunny cancion", "j balvin sencillo", "ozuna cancion", 
                  "daddy yankee cancion", "don omar cancion", "wisin yandel cancion",
                  "anuel aa cancion", "rauw alejandro cancion", "myke towers cancion"],

    "Rock":      ["mana cancion", "cafe tacvba sencillo", "caifanes cancion", 
                  "los enanitos verdes cancion", "soda stereo cancion", "fobia cancion",
                  "molotov cancion", "el tri cancion", "division minuscula cancion"],

    "Cumbia":    ["cumbia sonidera cancion", "los angeles azules cancion", "sonora dinamita cancion",
                  "tropicalisimo apache cancion", "chicos del barrio cancion", "cumbia colombiana popular",
                  "grupo kual cancion", "la sonora santanera cancion", "carlos vives cancion"],

    "Norteño":   ["los tigres del norte cancion", "vicente fernandez cancion", "chalino sanchez cancion",
                  "los tucanes de tijuana cancion", "banda el recodo norteno", "lupillo rivera cancion",
                  "el chapo de sinaloa cancion", "los huracanes del norte cancion", "ramon ayala cancion"],

    "Gruperas":  ["los bukis cancion", "bronco cancion", "los yonics cancion", 
                  "los acosta cancion", "grupo libra cancion", "los mier cancion",
                  "los rehenes cancion", "limite cancion", "grupo bryndis cancion"],

    "Balada":    ["juan gabriel balada", "luis miguel cancion", "alejandro fernandez cancion",
                  "jose jose cancion", "marco antonio solis cancion", "pedro infante cancion",
                  "javier solis cancion", "rocio durcal cancion", "raphael cancion"],

    "Pop":       ["shakira cancion", "maluma sencillo", "enrique iglesias cancion",
                  "ricky martin cancion", "marc anthony cancion", "jennifer lopez cancion",
                  "thalía cancion", "paulina rubio cancion", "alejandra guzman cancion"],

    "RockEng":   ["acdc song", "queen song", "guns n roses song", 
                  "nirvana song", "aerosmith song", "the doors song",
                  "led zeppelin song", "pink floyd song", "rolling stones song"],

    "Electronica": ["daft punk song", "calvin harris song", "david guetta cancion",
                    "avicii song", "tiesto song", "martin garrix song",
                    "deadmau5 song", "marshmello song", "alan walker song"],
}

# ─── REGISTRO ─────────────────────────────────────────────────────────────────

def cargar_registro() -> set:
    if os.path.exists(ARCHIVO_REGISTRO):
        with open(ARCHIVO_REGISTRO, "r", encoding="utf-8") as f:
            return set(json.load(f))
    return set()


def guardar_registro(ids: set):
    with open(ARCHIVO_REGISTRO, "w", encoding="utf-8") as f:
        json.dump(list(ids), f, ensure_ascii=False, indent=2)

# ─── UTILIDADES ───────────────────────────────────────────────────────────────

def verificar_ytdlp():
    try:
        subprocess.run(["yt-dlp", "--version"], capture_output=True, check=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        print("❌  yt-dlp no encontrado. Instalando...")
        subprocess.run([sys.executable, "-m", "pip", "install", "yt-dlp"], check=True)
        print("✅  yt-dlp instalado.\n")


def titulo_es_compilacion(titulo: str) -> bool:
    titulo_lower = titulo.lower()
    return any(p in titulo_lower for p in PALABRAS_PROHIBIDAS)


def nombre_seguro(texto: str) -> str:
    return re.sub(r'[<>:"/\\|?*]', "", texto).strip()


def buscar_videos(query: str, max_resultados: int = 20) -> list:
    cmd = [
        "yt-dlp",
        f"ytsearch{max_resultados}:{query}",
        "--dump-json",
        "--flat-playlist",
        "--no-warnings",
        "--quiet",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    videos = []
    for line in result.stdout.strip().splitlines():
        try:
            videos.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return videos


def filtrar_videos(videos: list, ids_descargados: set) -> list:
    filtrados = []
    for v in videos:
        titulo = v.get("title", "")
        duracion = v.get("duration") or 0
        vid_id = v.get("id", "")

        if vid_id in ids_descargados:
            continue
        if titulo_es_compilacion(titulo):
            continue
        if duracion > DURACION_MAX_SEGUNDOS:
            continue
        if duracion < DURACION_MIN_SEGUNDOS:
            continue

        filtrados.append(v)
    return filtrados


def descargar_audio(video_id: str, nombre_archivo: str) -> bool:
    url = f"https://www.youtube.com/watch?v={video_id}"
    archivo_salida = os.path.join(CARPETA_SALIDA, f"{nombre_seguro(nombre_archivo)}.%(ext)s")

    cmd = [
        "yt-dlp",
        url,
        "--extract-audio",
        "--audio-format", "mp3",
        "--audio-quality", "0",
        "--output", archivo_salida,
        "--no-playlist",
        "--quiet",
        "--no-warnings",
    ]

    try:
        subprocess.run(cmd, check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError:
        return False

# ─── RONDA ────────────────────────────────────────────────────────────────────

def ejecutar_ronda(numero_ronda: int, canciones_por_genero: int, ids_descargados: set) -> int:
    print(f"\n{'═'*45}")
    print(f"  RONDA {numero_ronda}")
    print(f"{'═'*45}")

    descargadas_ronda = 0
    conteo = {g: 0 for g in GENEROS}
    query_idx = {g: 0 for g in GENEROS}

    while any(conteo[g] < canciones_por_genero for g in GENEROS):
        hubo_avance = False

        for genero, queries in GENEROS.items():
            if conteo[genero] >= canciones_por_genero:
                continue
            if query_idx[genero] >= len(queries):
                continue

            query = queries[query_idx[genero]]
            query_idx[genero] += 1

            videos = buscar_videos(query, max_resultados=25)
            videos = filtrar_videos(videos, ids_descargados)

            for video in videos:
                vid_id = video.get("id", "")
                titulo = video.get("title", "sin_titulo")
                duracion = int(video.get("duration") or 0)
                mins = duracion // 60
                segs = duracion % 60

                print(f"\n🎵  {genero}")
                print(f"  ⬇  {titulo[:52]:<52} [{mins}:{segs:02d}]")

                ok = descargar_audio(vid_id, f"{genero} - {titulo}")
                if ok:
                    ids_descargados.add(vid_id)
                    guardar_registro(ids_descargados)
                    conteo[genero] += 1
                    descargadas_ronda += 1
                    hubo_avance = True
                    print(f"     ✅  {genero} ({conteo[genero]}/{canciones_por_genero})")
                    break
                else:
                    print(f"     ⚠️   Falló, siguiente...")

            time.sleep(0.5)

        if not hubo_avance:
            break

    return descargadas_ronda

# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Descarga música por géneros desde YouTube.")
    parser.add_argument("--rondas",    type=int, default=1, help="Cuántas rondas ejecutar (default: 1)")
    parser.add_argument("--por-ronda", type=int, default=3, help="Canciones por género por ronda (default: 3)")
    args = parser.parse_args()

    verificar_ytdlp()
    os.makedirs(CARPETA_SALIDA, exist_ok=True)

    ids_descargados = cargar_registro()
    print(f"📋  Registro cargado: {len(ids_descargados)} canciones ya descargadas anteriormente.")
    print(f"🎯  Plan: {args.rondas} ronda(s) × {args.por_ronda} canciones × {len(GENEROS)} géneros")
    print(f"    = hasta {args.rondas * args.por_ronda * len(GENEROS)} canciones nuevas")
    print(f"📁  Destino: {os.path.abspath(CARPETA_SALIDA)}")

    total_descargadas = 0

    for ronda in range(1, args.rondas + 1):
        descargadas = ejecutar_ronda(ronda, args.por_ronda, ids_descargados)
        total_descargadas += descargadas

        if ronda < args.rondas:
            print(f"\n⏳  Pausa entre rondas...")
            time.sleep(2)

    print(f"\n{'═'*45}")
    print(f"✅  Listo. Total descargadas esta sesión: {total_descargadas}")
    print(f"📋  Historial acumulado: {len(ids_descargados)} canciones únicas")
    print(f"📁  {os.path.abspath(CARPETA_SALIDA)}")


if __name__ == "__main__":
    main()