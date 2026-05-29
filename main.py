import sys
import os
import json
import base64
import ctypes

if os.name == 'nt':
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("vibe.pulse.music.1.0")
    except:
        pass


def ruta_rec(rel):
    try:
        base = sys._MEIPASS
    except AttributeError:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, rel)


DIR_CFG = os.path.join(os.path.expanduser('~'), '.axioma_music')
ARCH_CFG = os.path.join(DIR_CFG, 'config.json')


def cargar_cfg():
    if os.path.exists(ARCH_CFG):
        try:
            with open(ARCH_CFG, 'r', encoding='utf-8') as f:
                cfg = json.load(f)
            pls = cfg.get('playlists', {})
            for nom, val in list(pls.items()):
                if isinstance(val, list):
                    pls[nom] = {'songs': val, 'banner': None}
            if 'folders' not in cfg:
                cfg['folders'] = []
            return cfg
        except:
            pass
    return {"folders": [], "playlists": {"Favoritos": {"songs": [], "banner": None}}}


def guardar_cfg(cfg):
    os.makedirs(DIR_CFG, exist_ok=True)
    try:
        with open(ARCH_CFG, 'w', encoding='utf-8') as f:
            json.dump(cfg, f, indent=2, ensure_ascii=False)
    except:
        pass


class Api:
    def __init__(self):
        from audio_engine import Motor
        self.motor = Motor()
        self.cfg = cargar_cfg()
        self.listas = self.cfg.get('playlists', {"Favoritos": {"songs": [], "banner": None}})
        self.carpetas = self.cfg.get('folders', [])
        self.pistas = []
        self._cache_art = {}
        self._cache_meta = {}
        self._vent = None
        if not self.carpetas:
            mus = os.path.join(os.path.expanduser('~'), 'Music')
            if not os.path.isdir(mus):
                mus = os.path.join(os.path.expanduser('~'), 'Música')
            if os.path.isdir(mus):
                self.carpetas.append(mus)
                self._guardar()
        if 'Favoritos' not in self.listas:
            self.listas['Favoritos'] = {'songs': [], 'banner': None}
        self._recargar()

    def set_window(self, v):
        self._vent = v

    def _recargar(self):
        from metadata_utils import escanear
        self.pistas = []
        visto = set()
        for carp in self.carpetas:
            if os.path.isdir(carp):
                res = escanear(carp)
                for p in res:
                    fp = p['filepath']
                    if fp not in visto:
                        visto.add(fp)
                        p.pop('cover_art', None)
                        self.pistas.append(p)

    def _limpiar_str(self, s):
        if not s:
            return ''
        return s.replace('\ufeff', '').replace('\x00', '').strip()

    def get_library(self):
        return [{
            'filepath': p['filepath'],
            'title': self._limpiar_str(p.get('title', '')),
            'artist': self._limpiar_str(p.get('artist', '')),
            'album': self._limpiar_str(p.get('album', '')),
            'duration': p.get('duration', 0),
            'size': p.get('size', 0),
            'format': p.get('format', ''),
        } for p in self.pistas]

    def get_stats(self):
        albs = 0
        for nom in self.listas:
            if nom != 'Favoritos':
                albs += 1
        tam = 0
        for p in self.pistas:
            tam += p.get('size', 0)
        return {
            'total_tracks': len(self.pistas),
            'total_albums': albs,
            'total_size': tam,
            'carpetas': self.carpetas,
        }

    def get_cover_b64(self, ruta):
        if ruta in self._cache_art:
            return self._cache_art[ruta]
        from metadata_utils import leer_meta
        try:
            m = leer_meta(ruta)
            if m.get('cover_art'):
                b = base64.b64encode(m['cover_art']).decode('utf-8')
                self._cache_art[ruta] = b
                return b
        except:
            pass
        self._cache_art[ruta] = None
        return None

    def get_song_meta(self, ruta):
        if ruta in self._cache_meta:
            return self._cache_meta[ruta]
        from metadata_utils import leer_meta
        if not ruta or not os.path.exists(ruta):
            return None
        try:
            m = leer_meta(ruta)
            res = {
                'title': self._limpiar_str(m.get('title', '')),
                'artist': self._limpiar_str(m.get('artist', '')),
                'album': self._limpiar_str(m.get('album', '')),
                'duration': m.get('duration', 0),
            }
            self._cache_meta[ruta] = res
            return res
        except:
            return None

    def play_queue(self, rutas, inicio=0, mezclar=False):
        from metadata_utils import leer_meta
        self.motor.poner_cola(rutas, inicio, mezclar)
        self.motor.tocar()
        if 0 <= self.motor.idx < len(self.motor.cola):
            fp = self.motor.cola[self.motor.idx]
            m = leer_meta(fp)
            self.motor.fijar_dur(m.get('duration', 0) * 1000)
        return True

    def toggle_playback(self):
        self.motor.alternar()
        return True

    def next_track(self):
        from metadata_utils import leer_meta
        self.motor.sig()
        if self.motor.archivo:
            m = leer_meta(self.motor.archivo)
            self.motor.fijar_dur(m.get('duration', 0) * 1000)
        return True

    def prev_track(self):
        from metadata_utils import leer_meta
        self.motor.ant()
        if self.motor.archivo:
            m = leer_meta(self.motor.archivo)
            self.motor.fijar_dur(m.get('duration', 0) * 1000)
        return True

    def seek(self, ms):
        self.motor.saltar(ms / 1000.0)
        return True

    def set_volume(self, v):
        self.motor.fijar_vol(v / 100.0)
        return True

    def set_shuffle(self, val):
        import random
        self.motor.mezcla = val
        if val and len(self.motor.cola) > 1 and self.motor.archivo:
            actual = self.motor.archivo
            resto = [f for f in self.motor.cola if f != actual]
            random.shuffle(resto)
            self.motor.cola = [actual] + resto
            self.motor.idx = 0
        return True

    def set_repeat(self, modo):
        self.motor.repite = modo
        return True

    def get_state(self):
        from metadata_utils import leer_meta
        s = self.motor.estado()
        if s.get('cambio_pista') and s['archivo']:
            m = leer_meta(s['archivo'])
            dur = m.get('duration', 0) * 1000
            self.motor.fijar_dur(dur)
            s['dur_ms'] = dur
        elif s['archivo'] and s['dur_ms'] == 0:
            m = leer_meta(s['archivo'])
            dur = m.get('duration', 0) * 1000
            self.motor.fijar_dur(dur)
            s['dur_ms'] = dur
        return s

    def get_next_song_title(self):
        if self.motor.idx < len(self.motor.cola) - 1:
            fp = self.motor.cola[self.motor.idx + 1]
            m = self.get_song_meta(fp)
            if m:
                return m['title']
        return None

    def get_playlists(self):
        return self.listas

    def create_playlist(self, nom):
        if nom and nom not in self.listas:
            self.listas[nom] = {'songs': [], 'banner': None}
            self._guardar()
            return True
        return False

    def delete_playlist(self, nom):
        if nom in self.listas and nom != 'Favoritos':
            del self.listas[nom]
            self._guardar()
            return True
        return False

    def clear_playlist(self, nom):
        if nom in self.listas:
            self.listas[nom]['songs'] = []
            self._guardar()
            return True
        return False

    def add_to_playlist(self, nom, ruta):
        if nom in self.listas:
            if ruta not in self.listas[nom]['songs']:
                self.listas[nom]['songs'].append(ruta)
                self._guardar()
                return True
        return False

    def remove_from_playlist(self, nom, ruta):
        if nom in self.listas and ruta in self.listas[nom]['songs']:
            self.listas[nom]['songs'].remove(ruta)
            self._guardar()
            return True
        return False

    def toggle_favorite(self, ruta):
        favs = self.listas.get('Favoritos', {'songs': [], 'banner': None})
        if ruta in favs['songs']:
            favs['songs'].remove(ruta)
            self._guardar()
            return False
        else:
            favs['songs'].append(ruta)
            self._guardar()
            return True

    def is_favorite(self, ruta):
        return ruta in self.listas.get('Favoritos', {}).get('songs', [])

    def set_playlist_banner(self, nom):
        import webview
        tipos = ('Image Files (*.jpg;*.jpeg;*.png;*.bmp;*.webp)',)
        try:
            res = self._vent.create_file_dialog(webview.FileDialog.OPEN, file_types=tipos)
        except:
            return None
        if res and len(res) > 0:
            ruta = res[0]
            if nom in self.listas:
                self.listas[nom]['banner'] = ruta
                self._guardar()
                return ruta
        return None

    def get_file_b64(self, ruta):
        if not ruta or not os.path.exists(ruta):
            return None
        try:
            with open(ruta, 'rb') as f:
                datos = f.read()
            ext = os.path.splitext(ruta)[1].lower().lstrip('.')
            tipos_m = {'jpg': 'image/jpeg', 'jpeg': 'image/jpeg', 'png': 'image/png',
                     'bmp': 'image/bmp', 'gif': 'image/gif', 'webp': 'image/webp'}
            tipo_m = tipos_m.get(ext, 'image/jpeg')
            return "data:" + tipo_m + ";base64," + base64.b64encode(datos).decode()
        except:
            return None

    def delete_file(self, ruta):
        try:
            if os.path.exists(ruta):
                os.remove(ruta)
            self._recargar()
            for pl in self.listas.values():
                if ruta in pl['songs']:
                    pl['songs'].remove(ruta)
            self._guardar()
            return True
        except:
            return False

    def add_folder(self):
        import webview
        try:
            res = self._vent.create_file_dialog(webview.FileDialog.FOLDER)
        except:
            return None
        if res and len(res) > 0:
            carp = res[0]
            if carp not in self.carpetas:
                self.carpetas.append(carp)
                self._guardar()
                self._recargar()
                return carp
        return None

    def remove_folder(self, carp):
        if carp in self.carpetas:
            self.carpetas.remove(carp)
            self._guardar()
            self._recargar()
            return True
        return False

    def get_folders(self):
        return self.carpetas

    def _guardar(self):
        guardar_cfg({
            'folders': self.carpetas,
            'playlists': self.listas,
        })


def main():
    import webview

    api = Api()
    html = ruta_rec(os.path.join('web', 'index.html'))

    if not os.path.exists(html):
        sys.exit(1)

    vent = webview.create_window(
        'VIBE PULSE',
        url=html,
        js_api=api,
        width=1200,
        height=800,
        min_size=(900, 600),
        background_color='#0a0b10',
        text_select=False,
    )

    api.set_window(vent)
    webview.start(debug=False)
    api.motor.limpiar()


if __name__ == '__main__':
    main()
