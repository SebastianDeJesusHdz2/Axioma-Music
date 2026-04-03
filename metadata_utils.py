import os
from mutagen import File as ArchivoMutagen

FORMATOS_SOPORTADOS = {'.mp3', '.flac', '.wav', '.ogg', '.m4a', '.aac', '.wma', '.opus'}

def es_archivo_audio(ruta_archivo):
    ext = os.path.splitext(ruta_archivo)[1].lower()
    return ext in FORMATOS_SOPORTADOS

def obtener_metadatos(ruta_archivo):
    nombre_base = os.path.splitext(os.path.basename(ruta_archivo))[0]
    metadatos = {
        'title': nombre_base,
        'artist': 'Artista Desconocido',
        'album': 'Álbum Desconocido',
        'duration': 0,
        'cover_art': None,
        'filepath': ruta_archivo,
        'format': os.path.splitext(ruta_archivo)[1].upper().replace('.', ''),
        'size': os.path.getsize(ruta_archivo) if os.path.exists(ruta_archivo) else 0,
    }

    try:
        audio = ArchivoMutagen(ruta_archivo)
        if audio is None:
            return metadatos

        if hasattr(audio.info, 'length'):
            metadatos['duration'] = int(audio.info.length)

        ext = os.path.splitext(ruta_archivo)[1].lower()

        if ext == '.mp3':
            _extraer_id3(audio, metadatos)
        elif ext == '.flac':
            _extraer_flac(audio, metadatos)
        elif ext in ('.ogg', '.opus'):
            _extraer_vorbis(audio, metadatos)
        elif ext in ('.m4a', '.aac'):
            _extraer_mp4(audio, metadatos)
        elif ext == '.wav':
            _extraer_id3(audio, metadatos)

    except Exception as e:
        print(f"[metadata_utils] Error leyendo {ruta_archivo}: {e}")

    return metadatos

def _extraer_id3(audio, metadatos):
    if not hasattr(audio, 'tags') or audio.tags is None:
        return
    tags = audio.tags
    if 'TIT2' in tags:
        metadatos['title'] = str(tags['TIT2'])
    if 'TPE1' in tags:
        metadatos['artist'] = str(tags['TPE1'])
    if 'TALB' in tags:
        metadatos['album'] = str(tags['TALB'])
    for clave in tags:
        if clave.startswith('APIC'):
            metadatos['cover_art'] = tags[clave].data
            break

def _extraer_flac(audio, metadatos):
    if 'title' in audio:
        metadatos['title'] = audio['title'][0]
    if 'artist' in audio:
        metadatos['artist'] = audio['artist'][0]
    if 'album' in audio:
        metadatos['album'] = audio['album'][0]
    if audio.pictures:
        metadatos['cover_art'] = audio.pictures[0].data

def _extraer_vorbis(audio, metadatos):
    if 'title' in audio:
        metadatos['title'] = audio['title'][0]
    if 'artist' in audio:
        metadatos['artist'] = audio['artist'][0]
    if 'album' in audio:
        metadatos['album'] = audio['album'][0]

def _extraer_mp4(audio, metadatos):
    if '\xa9nam' in audio:
        metadatos['title'] = audio['\xa9nam'][0]
    if '\xa9ART' in audio:
        metadatos['artist'] = audio['\xa9ART'][0]
    if '\xa9alb' in audio:
        metadatos['album'] = audio['\xa9alb'][0]
    if 'covr' in audio:
        metadatos['cover_art'] = bytes(audio['covr'][0])

def escanear_directorio(directorio):
    canciones = []
    for raiz, directorios, archivos in os.walk(directorio):
        for f in sorted(archivos):
            ruta_archivo = os.path.join(raiz, f)
            if es_archivo_audio(ruta_archivo):
                canciones.append(obtener_metadatos(ruta_archivo))
    return canciones

def formatear_duracion(segundos):
    if segundos <= 0:
        return "0:00"
    minutos = segundos // 60
    segs = segundos % 60
    return f"{minutos}:{segs:02d}"

def formatear_tamano(tamano_bytes):
    if tamano_bytes < 1024:
        return f"{tamano_bytes} B"
    elif tamano_bytes < 1024 * 1024:
        return f"{tamano_bytes / 1024:.1f} KB"
    else:
        return f"{tamano_bytes / (1024 * 1024):.1f} MB"
