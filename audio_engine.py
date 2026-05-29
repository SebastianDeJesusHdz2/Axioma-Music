import os
import random

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame


class Motor:
    def __init__(self):
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=2048)
        self.cola = []
        self.idx = -1
        self.archivo = None
        self.meta = {}
        self.dur_ms = 0
        self._offset_ms = 0
        self._activo = False
        self._pausado = False
        self.vol = 0.7
        self.mezcla = False
        self.repite = 0
        self._cambio_pista = False

    def poner_cola(self, rutas, inicio=0, mezclar=False):
        self.cola = list(rutas)
        if mezclar and len(self.cola) > 1:
            pri = self.cola[inicio]
            resto = [f for i, f in enumerate(self.cola) if i != inicio]
            random.shuffle(resto)
            self.cola = [pri] + resto
            self.idx = 0
        else:
            self.idx = inicio

    def tocar(self):
        if 0 <= self.idx < len(self.cola):
            self._cargar(self.cola[self.idx])

    def _cargar(self, ruta):
        if not ruta or not os.path.exists(ruta):
            return False
        try:
            pygame.mixer.music.load(ruta)
            pygame.mixer.music.play()
            pygame.mixer.music.set_volume(self.vol)
            self.archivo = ruta
            self._offset_ms = 0
            self.dur_ms = 0
            self._activo = True
            self._pausado = False
            self._cambio_pista = True
            return True
        except Exception:
            self._activo = False
            return False

    def fijar_dur(self, ms):
        self.dur_ms = ms

    def alternar(self):
        if self._pausado:
            pygame.mixer.music.unpause()
            self._pausado = False
        elif self._activo:
            pygame.mixer.music.pause()
            self._pausado = True
        elif self.cola and self.idx >= 0:
            self.tocar()

    def pausar(self):
        if self._activo and not self._pausado:
            pygame.mixer.music.pause()
            self._pausado = True

    def reanudar(self):
        if self._pausado:
            pygame.mixer.music.unpause()
            self._pausado = False

    def parar(self):
        pygame.mixer.music.stop()
        self._activo = False
        self._pausado = False

    def sig(self):
        if self.repite == 2:
            self.tocar()
        elif self.idx < len(self.cola) - 1:
            self.idx += 1
            self.tocar()
        elif self.repite == 1 and len(self.cola) > 0:
            self.idx = 0
            self.tocar()

    def ant(self):
        pos = self.pos_ms()
        if pos > 3000:
            self.saltar(0)
        elif self.idx > 0:
            self.idx -= 1
            self.tocar()
        else:
            self.saltar(0)

    def saltar(self, segs):
        if self._activo and self.archivo:
            try:
                pygame.mixer.music.stop()
                pygame.mixer.music.play(start=segs)
                pygame.mixer.music.set_volume(self.vol)
                self._offset_ms = int(segs * 1000)
                self._pausado = False
            except:
                pass

    def fijar_vol(self, v):
        self.vol = max(0.0, min(1.0, v))
        try:
            pygame.mixer.music.set_volume(self.vol)
        except:
            pass

    def pos_ms(self):
        if not self._activo or self._pausado:
            if self._pausado:
                bruto = pygame.mixer.music.get_pos()
                if bruto != -1:
                    return self._offset_ms + bruto
            return self._offset_ms
        bruto = pygame.mixer.music.get_pos()
        if bruto == -1:
            return 0
        return self._offset_ms + bruto

    def revisar_fin(self):
        if self._activo and not self._pausado and not pygame.mixer.music.get_busy():
            self._al_terminar()
            return True
        return False

    def _al_terminar(self):
        if self.repite == 2:
            self.tocar()
        elif self.idx < len(self.cola) - 1:
            self.idx += 1
            self.tocar()
        elif self.repite == 1 and len(self.cola) > 0:
            self.idx = 0
            self.tocar()
        else:
            self._activo = False
            self._pausado = False
            self.archivo = None

    def estado(self):
        self.revisar_fin()
        cambio = self._cambio_pista
        self._cambio_pista = False
        return {
            'tocando': self._activo and not self._pausado,
            'pausado': self._pausado,
            'pos_ms': self.pos_ms(),
            'dur_ms': self.dur_ms,
            'archivo': self.archivo or '',
            'vol': int(self.vol * 100),
            'mezcla': self.mezcla,
            'repite': self.repite,
            'hay_sig': self.idx < len(self.cola) - 1,
            'hay_ant': self.idx > 0,
            'tam_cola': len(self.cola),
            'idx_cola': self.idx,
            'cambio_pista': cambio,
        }

    def limpiar(self):
        try:
            pygame.mixer.music.stop()
            pygame.mixer.quit()
        except:
            pass
