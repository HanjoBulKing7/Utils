# 🎵 descargar-musica-usb

Script de Python para llenar una memoria USB con música descargada de YouTube, organizada por géneros, sin repetir canciones y filtrando automáticamente compilaciones y mixes.

---

## ¿Qué hace?

- Busca canciones en YouTube por género (Banda, Corridos, Rock, Reggaeton, etc.)
- Filtra videos largos (+7 min), mixes, compilaciones, lives y karaokes automáticamente
- Descarga el audio directamente como **MP3**
- Lleva un **registro local** para nunca repetir una canción entre sesiones
- Alterna entre géneros en cada ronda para que la USB quede variada

---

## Requisitos

**Python 3.10+**
```bash
python --version
```

**yt-dlp**
```bash
pip install yt-dlp
```

**ffmpeg** (necesario para convertir a MP3)

- Windows:
  ```powershell
  winget install ffmpeg
  ```
- macOS:
  ```bash
  brew install ffmpeg
  ```
- Linux:
  ```bash
  sudo apt install ffmpeg
  ```

> Después de instalar ffmpeg, cierra y vuelve a abrir la terminal para que tome efecto.

---

## Uso

```bash
# 1 ronda, 3 canciones por género (36 canciones aprox.)
python descargarmusica.py

# 10 rondas, 3 por género (360 canciones aprox. ~3 GB)
python descargarmusica.py --rondas 10

# 25 rondas, 2 por género (600 canciones aprox. ~5 GB)
python descargarmusica.py --rondas 25 --por-ronda 2
```

### Referencia rápida de espacio

| Rondas | Por género | Canciones aprox. | Espacio aprox. |
|--------|-----------|-----------------|---------------|
| 10     | 3         | 360             | ~3 GB         |
| 20     | 3         | 720             | ~6 GB         |
| 25     | 2         | 600             | ~5 GB         |
| 30     | 3         | 1,080           | ~9 GB         |

> Un MP3 de buena calidad pesa entre 7–10 MB en promedio.

---

## Configuración

Al inicio del script hay variables que puedes editar:

```python
CARPETA_SALIDA = "./musica_usb"   # carpeta destino (o ruta de tu USB, ej: "D:\\")
DURACION_MAX_SEGUNDOS = 420       # máximo 7 min por video
DURACION_MIN_SEGUNDOS = 90        # mínimo 1.5 min por video
```

### Cambiar destino a una USB

```python
CARPETA_SALIDA = "D:\\"   # Windows
CARPETA_SALIDA = "/Volumes/MI_USB"  # macOS
CARPETA_SALIDA = "/media/usuario/MI_USB"  # Linux
```

### Agregar o quitar géneros

Edita el diccionario `GENEROS` en el script. Cada entrada es una lista de queries de búsqueda:

```python
"MiGenero": ["artista1 cancion", "artista2 song", "genero popular cancion"],
```

---

## Géneros incluidos por defecto

| Género     | Artistas de referencia                              |
|------------|-----------------------------------------------------|
| Banda      | Banda MS, El Recodo, La Arrolladora                 |
| Metal      | Metallica, Iron Maiden, System of a Down            |
| Corridos   | Peso Pluma, Natanael Cano, Eslabon Armado           |
| Reggaeton  | Bad Bunny, Daddy Yankee, J Balvin                   |
| Rock       | Maná, Caifanes, Soda Stereo                         |
| Cumbia     | Los Ángeles Azules, Sonora Dinamita, Carlos Vives   |
| Norteño    | Los Tigres del Norte, Vicente Fernández, Ramón Ayala|
| Gruperas   | Los Bukis, Bronco, Grupo Bryndis                    |
| Balada     | Juan Gabriel, Luis Miguel, José José                |
| Pop        | Shakira, Enrique Iglesias, Thalía                   |
| Rock Inglés| AC/DC, Queen, Led Zeppelin, Nirvana                 |
| Electrónica| Daft Punk, Avicii, Calvin Harris                    |

---

## Archivos generados

| Archivo                      | Descripción                                      |
|------------------------------|--------------------------------------------------|
| `registro_descargados.json`  | Historial de IDs descargados (no subir al repo)  |
| `musica_usb/`                | Carpeta con los MP3 (si usas la ruta por defecto)|

---

## .gitignore recomendado

```
registro_descargados.json
musica_usb/
__pycache__/
*.pyc
```

---

## Notas

- Si una descarga falla (video eliminado, restringido, etc.) el script lo omite y continúa con el siguiente automáticamente.
- El registro persiste entre sesiones — puedes correr el script varias veces sin repetir canciones.
- Para reiniciar el historial y volver a descargar desde cero, borra el archivo `registro_descargados.json`.
