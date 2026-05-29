import os
from mutagen import File as ArchivoMut

FORMATOS = {'.mp3', '.flac', '.wav', '.ogg', '.m4a', '.aac', '.wma', '.opus'}


def es_audio(ruta):
    ext = os.path.splitext(ruta)[1].lower()
    return ext in FORMATOS


def leer_meta(ruta):
    nombre = os.path.splitext(os.path.basename(ruta))[0]
    datos = {
        'title': nombre,
        'artist': 'Artista Desconocido',
        'album': 'Album Desconocido',
        'duration': 0,
        'cover_art': None,
        'filepath': ruta,
        'format': os.path.splitext(ruta)[1].upper().replace('.', ''),
        'size': os.path.getsize(ruta) if os.path.exists(ruta) else 0,
    }
    try:
        audio = ArchivoMut(ruta)
        if audio is None:
            return datos
        if hasattr(audio.info, 'length'):
            datos['duration'] = int(audio.info.length)
        ext = os.path.splitext(ruta)[1].lower()
        if ext == '.mp3':
            _leer_id3(audio, datos)
        elif ext == '.flac':
            _leer_flac(audio, datos)
        elif ext in ('.ogg', '.opus'):
            _leer_vorbis(audio, datos)
        elif ext in ('.m4a', '.aac'):
            _leer_mp4(audio, datos)
        elif ext == '.wav':
            _leer_id3(audio, datos)
    except:
        pass
    return datos


def _leer_id3(audio, datos):
    if not hasattr(audio, 'tags') or audio.tags is None:
        return
    t = audio.tags
    if 'TIT2' in t:
        datos['title'] = str(t['TIT2'])
    if 'TPE1' in t:
        datos['artist'] = str(t['TPE1'])
    if 'TALB' in t:
        datos['album'] = str(t['TALB'])
    for k in t:
        if k.startswith('APIC'):
            datos['cover_art'] = t[k].data
            break


def _leer_flac(audio, datos):
    if 'title' in audio:
        datos['title'] = audio['title'][0]
    if 'artist' in audio:
        datos['artist'] = audio['artist'][0]
    if 'album' in audio:
        datos['album'] = audio['album'][0]
    if audio.pictures:
        datos['cover_art'] = audio.pictures[0].data


def _leer_vorbis(audio, datos):
    if 'title' in audio:
        datos['title'] = audio['title'][0]
    if 'artist' in audio:
        datos['artist'] = audio['artist'][0]
    if 'album' in audio:
        datos['album'] = audio['album'][0]


def _leer_mp4(audio, datos):
    if '\xa9nam' in audio:
        datos['title'] = audio['\xa9nam'][0]
    if '\xa9ART' in audio:
        datos['artist'] = audio['\xa9ART'][0]
    if '\xa9alb' in audio:
        datos['album'] = audio['\xa9alb'][0]
    if 'covr' in audio:
        datos['cover_art'] = bytes(audio['covr'][0])


def escanear(carpeta):
    pistas = []
    for raiz, dirs, archs in os.walk(carpeta):
        for f in sorted(archs):
            ruta = os.path.join(raiz, f)
            if es_audio(ruta):
                pistas.append(leer_meta(ruta))
    return pistas


def fmt_dur(segs):
    if segs <= 0:
        return "0:00"
    m = segs // 60
    s = segs % 60
    return f"{m}:{s:02d}"


def fmt_tam(b):
    if b < 1024:
        return f"{b} B"
    elif b < 1024 * 1024:
        return f"{b / 1024:.1f} KB"
    else:
        return f"{b / (1024 * 1024):.1f} MB"
