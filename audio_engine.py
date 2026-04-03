import os
import random
from PyQt6.QtCore import QObject, QUrl, pyqtSignal
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput

class MotorAudio(QObject):
    posicion_cambiada = pyqtSignal(int)
    duracion_cambiada = pyqtSignal(int)
    estado_reproduccion_cambiado = pyqtSignal(QMediaPlayer.PlaybackState)
    cancion_actual_cambiada = pyqtSignal(dict)
    cola_terminada = pyqtSignal()

    def __init__(self, padre=None):
        super().__init__(padre)
        self.reproductor = QMediaPlayer(self)
        self.salida_audio = QAudioOutput(self)
        self.reproductor.setAudioOutput(self.salida_audio)

        self.cola = []
        self.indice_actual = -1
        self._metadatos_actuales = {}
        self.bucle_cola = False
        self.modo_repetir_uno = False

        self.reproductor.positionChanged.connect(self.posicion_cambiada.emit)
        self.reproductor.durationChanged.connect(self.duracion_cambiada.emit)
        self.reproductor.playbackStateChanged.connect(self._al_cambiar_estado)
        self.reproductor.mediaStatusChanged.connect(self._al_cambiar_estado_media)

        self.salida_audio.setVolume(0.7)

    def _al_cambiar_estado(self, estado):
        self.estado_reproduccion_cambiado.emit(estado)

    def _al_cambiar_estado_media(self, estado):
        if estado == QMediaPlayer.MediaStatus.EndOfMedia:
            self.siguiente()

    def reproducir_archivo(self, metadatos):
        self.cola = [metadatos]
        self.indice_actual = 0
        self._cargar_y_reproducir(metadatos)

    def reproducir_cola(self, canciones, indice_inicio=0, aleatorio=False):
        self.cola = list(canciones)
        if aleatorio and len(self.cola) > 0:
            primera_cancion = self.cola[indice_inicio]
            random.shuffle(self.cola)
            self.cola.remove(primera_cancion)
            self.cola.insert(0, primera_cancion)
            self.indice_actual = 0
        else:
            self.indice_actual = indice_inicio
        if 0 <= self.indice_actual < len(self.cola):
            self._cargar_y_reproducir(self.cola[self.indice_actual])

    def _cargar_y_reproducir(self, metadatos):
        self._metadatos_actuales = metadatos
        ruta_archivo = metadatos.get('filepath', '')
        
        if not ruta_archivo or not os.path.exists(ruta_archivo):
            self.cancion_actual_cambiada.emit(metadatos)
            return
        
        try:
            ruta_normalizada = os.path.normpath(os.path.abspath(ruta_archivo))
            url = QUrl.fromLocalFile(ruta_normalizada)
            self.reproductor.setSource(url)
            self.reproductor.play()
        except Exception as e:
            print(f"[MotorAudio] Error cargando {ruta_archivo}: {e}")
        
        self.cancion_actual_cambiada.emit(metadatos)

    def reproducir(self):
        self.reproductor.play()

    def pausar(self):
        self.reproductor.pause()

    def alternar_reproduccion(self):
        if self.esta_reproduciendo():
            self.pausar()
        else:
            self.reproducir()

    def detener(self):
        self.reproductor.stop()

    def siguiente(self):
        if self.modo_repetir_uno:
            self._cargar_y_reproducir(self.cola[self.indice_actual])
        elif self.indice_actual < len(self.cola) - 1:
            self.indice_actual += 1
            self._cargar_y_reproducir(self.cola[self.indice_actual])
        else:
            if len(self.cola) > 0:
                self.indice_actual = 0
                self._cargar_y_reproducir(self.cola[self.indice_actual])
            else:
                self.detener()
                self.cola_terminada.emit()

    def anterior(self):
        if self.reproductor.position() > 3000:
            self.reproductor.setPosition(0)
        elif self.indice_actual > 0:
            self.indice_actual -= 1
            self._cargar_y_reproducir(self.cola[self.indice_actual])
        else:
            self.reproductor.setPosition(0)

    def establecer_volumen(self, valor):
        self.salida_audio.setVolume(valor / 100.0)

    def saltar_a(self, posicion_ms):
        self.reproductor.setPosition(posicion_ms)

    def obtener_metadatos_actuales(self):
        return self._metadatos_actuales

    def esta_reproduciendo(self):
        return self.reproductor.playbackState() == QMediaPlayer.PlaybackState.PlayingState

    def establecer_bucle_cola(self, habilitado):
        self.bucle_cola = habilitado

    def tiene_siguiente(self):
        return self.indice_actual < len(self.cola) - 1

    def tiene_anterior(self):
        return self.indice_actual > 0 or self.reproductor.position() > 3000
