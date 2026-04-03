import sys
import os
import json
from PyQt6.QtGui import QPixmap, QPainter, QImage, QPainterPath, QColor, QIcon, QRadialGradient, QPen, QCursor
from PyQt6.QtWidgets import (
    QApplication, QStyle, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QSlider, QListWidget, QListWidgetItem, QTabWidget,
    QFileDialog, QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit,
    QMessageBox, QMenu, QInputDialog, QFrame
)
from PyQt6.QtCore import Qt, QTimer, QSize, QRect
from PyQt6.QtMultimedia import QMediaPlayer

from audio_engine import MotorAudio
from metadata_utils import escanear_directorio, es_archivo_audio, obtener_metadatos, formatear_duracion
import styles

def ruta_recurso(ruta_relativa):
    try:
        base = sys._MEIPASS
    except:
        base = os.path.abspath(".")
    return os.path.join(base, ruta_relativa)

DIR_CONFIG = os.path.join(os.path.expanduser('~'), '.axioma_music')
FICHERO_CONFIG = os.path.join(DIR_CONFIG, 'config.json')

def cargar_configuracion():
    if os.path.exists(FICHERO_CONFIG):
        try:
            with open(FICHERO_CONFIG, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {"folders": [], "playlists": {"Favoritos": []}}

def guardar_configuracion(config):
    os.makedirs(DIR_CONFIG, exist_ok=True)
    try:
        with open(FICHERO_CONFIG, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error: {e}")

class WidgetDisco(QWidget):
    def __init__(self, padre=None):
        super().__init__(padre)
        self.setMinimumSize(350, 350)
        self.angulo = 0
        self.pixmap_portada = None
        self.reloj = QTimer(self)
        self.reloj.timeout.connect(self.rotar)
        self._girando = False

    def establecer_portada(self, datos):
        if datos:
            img = QImage()
            if img.loadFromData(datos) and not img.isNull():
                self.pixmap_portada = QPixmap.fromImage(img)
            else:
                self.pixmap_portada = None
        else:
            self.pixmap_portada = None
        self.update()

    def iniciar_giro(self):
        if not self._girando:
            self.reloj.start(50)
            self._girando = True

    def detener_giro(self):
        if self._girando:
            self.reloj.stop()
            self._girando = False

    def rotar(self):
        self.angulo = (self.angulo + 2) % 360
        self.update()

    def paintEvent(self, evento):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        tam = min(w, h) - 40
        cx, cy = w / 2.0, h / 2.0
        r = tam / 2.0

        # Fondo/Resplandor
        g_glow = QRadialGradient(cx, cy, r + 15)
        g_glow.setColorAt(0.8, QColor(139, 43, 226, 35))
        g_glow.setColorAt(1.0, QColor(139, 43, 226, 0))
        p.setBrush(g_glow)
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(int(cx - r - 15), int(cy - r - 15), int((r+15)*2), int((r+15)*2))

        # El vinilo (Cuerpo negro)
        p.setBrush(QColor("#0a0a0a"))
        p.drawEllipse(int(cx - r), int(cy - r), int(tam), int(tam))

        # Surcos de vinilo
        p.setPen(QPen(QColor(255, 255, 255, 18), 1))
        for step in range(12, int(r - 45), 8):
            p.drawEllipse(int(cx - step), int(cy - step), step * 2, step * 2)

        p.translate(cx, cy)
        p.rotate(self.angulo)

        # Portada (Centro)
        r_img = int(r * 0.42)
        t_img = r_img * 2
        path = QPainterPath()
        path.addEllipse(-float(r_img), -float(r_img), float(t_img), float(t_img))
        p.setClipPath(path)

        if self.pixmap_portada:
            pm = self.pixmap_portada.scaled(t_img, t_img, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
            p.drawPixmap(int(-r_img + (t_img - pm.width()) / 2), int(-r_img + (t_img - pm.height()) / 2), pm)
        else:
            p.setBrush(QColor("#8B2BE2"))
            p.drawEllipse(-r_img, -r_img, t_img, t_img)
            p.setPen(QColor("#ffffff"))
            p.drawText(QRect(-r_img, -r_img, t_img, t_img), Qt.AlignmentFlag.AlignCenter, "AXIOMA")

        # Centro (agujero)
        p.setClipping(False)
        p.setBrush(QColor("#0c0c18"))
        p.setPen(QPen(QColor("#00D9FF"), 1))
        p.drawEllipse(-8, -8, 16, 16)

class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Axioma Music Player")
        self.resize(1100, 780)
        self.setStyleSheet(styles.HOJA_ESTILOS)
        icono = ruta_recurso("Ax.png")
        if os.path.exists(icono): self.setWindowIcon(QIcon(icono))
        self.motor = MotorAudio(self)
        self.conf = cargar_configuracion()
        self.canciones = []
        self.carpetas = list(self.conf.get("folders", []))
        self.listas = {}
        self.aleatorio_habilitado = False
        self.modo_repeticion = 0
        
        self.motor.posicion_cambiada.connect(self.actualizar_posicion)
        self.motor.duracion_cambiada.connect(self.actualizar_duracion)
        self.motor.estado_reproduccion_cambiado.connect(self.actualizar_estado)
        self.motor.cancion_actual_cambiada.connect(self.actualizar_cancion)
        self.motor.cola_terminada.connect(self.al_terminar_cola)
        
        self.configurar_ui()
        self.cargar_datos()

    def cargar_datos(self):
        self.canciones = []
        for c in self.carpetas:
            if os.path.isdir(c):
                pistas = escanear_directorio(c)
                for p in pistas:
                    p.pop('cover_art', None)
                    if not any(x['filepath'] == p['filepath'] for x in self.canciones):
                        self.canciones.append(p)
        
        crudas = self.conf.get("playlists", {"Favoritos": []})
        rebuild = {}
        for n, ruts in crudas.items():
            en_lista = []
            if isinstance(ruts, list):
                for r in ruts:
                    found = next((x for x in self.canciones if x['filepath'] == r), None)
                    if found: en_lista.append(found)
            rebuild[n] = en_lista
        
        if "Favoritos" not in rebuild: rebuild["Favoritos"] = []
        self.listas = rebuild
        self.refrescar_listas()
        self.refrescar_biblioteca()

    def refrescar_listas(self):
        self.lst_listas.clear()
        for n in self.listas.keys():
            it = QListWidgetItem(n)
            if n == "Favoritos": 
                it.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogYesButton))
            self.lst_listas.addItem(it)

    def configurar_ui(self):
        root = QWidget()
        self.setCentralWidget(root)
        main_l = QVBoxLayout(root)
        main_l.setContentsMargins(0, 0, 0, 0)
        self.tabs = QTabWidget()
        self.pestana_biblioteca()
        self.pestana_reproductor()
        self.pestana_listas()
        main_l.addWidget(self.tabs)
        self.barra_controles(main_l)

    def pestana_biblioteca(self):
        p = QWidget()
        l = QVBoxLayout(p)
        l.setContentsMargins(30, 25, 30, 25)
        
        # Header y Stats
        top_l = QHBoxLayout()
        tit = QLabel("Biblioteca")
        tit.setObjectName("pageTitle")
        top_l.addWidget(tit)
        top_l.addStretch()
        
        stats_w = QWidget()
        stats_hl = QHBoxLayout(stats_w)
        stats_hl.setContentsMargins(0, 10, 0, 15)
        self.st_songs = self.crear_stat_card(stats_hl, "Canciones", "🎵")
        self.st_folders = self.crear_stat_card(stats_hl, "Carpetas", "📁")
        self.st_lists = self.crear_stat_card(stats_hl, "Listas", "📜")
        
        l.addLayout(top_l)
        l.addWidget(stats_w)

        # Buscador
        self.busqueda_bib = QLineEdit()
        self.busqueda_bib.setPlaceholderText("Buscar canción, artista o álbum...")
        self.busqueda_bib.textChanged.connect(self.filtrar_biblioteca)
        l.addWidget(self.busqueda_bib)

        # Tabla
        self.tabla_bib = QTableWidget(0, 5)
        self.tabla_bib.setHorizontalHeaderLabels([" ♡ ", "Título", "Artista", "Álbum", "Duración"])
        self.tabla_bib.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.tabla_bib.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla_bib.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabla_bib.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tabla_bib.customContextMenuRequested.connect(self.menu_contextual_biblioteca)
        self.tabla_bib.itemDoubleClicked.connect(self.reproducir_bib)
        l.addWidget(self.tabla_bib)

        # Bottom ctrls
        low = QHBoxLayout()
        self.lbl_carpetas = QLabel("No hay fuentes cargadas")
        self.lbl_carpetas.setObjectName("libraryStatsLabel")
        low.addWidget(self.lbl_carpetas)
        low.addStretch()
        bad = QPushButton("Añadir Carpeta"); bad.setObjectName("primaryBtn"); bad.clicked.connect(self.anadir_carpeta)
        bre = QPushButton("Quitar Carpeta"); bre.setObjectName("secondaryBtn"); bre.clicked.connect(self.quitar_carpeta)
        low.addWidget(bre); low.addWidget(bad)
        l.addLayout(low)
        self.tabs.addTab(p, "BIBLIOTECA")

    def crear_stat_card(self, layout, titulo, icon):
        card = QFrame()
        card.setObjectName("statCard")
        cl = QVBoxLayout(card)
        cl.setContentsMargins(12, 8, 12, 8)
        
        top = QHBoxLayout()
        il = QLabel(icon); il.setObjectName("statIcon")
        top.addWidget(il); top.addStretch()
        cl.addLayout(top)
        
        val = QLabel("0"); val.setObjectName("statNumber")
        cl.addWidget(val)
        lab = QLabel(titulo); lab.setObjectName("statLabel")
        cl.addWidget(lab)
        
        bar = QFrame(); bar.setObjectName("statBar"); bar.setFixedHeight(3)
        cl.addWidget(bar)
        layout.addWidget(card)
        return val

    def pestana_reproductor(self):
        p = QWidget()
        l = QVBoxLayout(p)
        l.setContentsMargins(40, 40, 40, 40)
        l.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.disco = WidgetDisco()
        l.addWidget(self.disco)
        
        self.lbl_titulo = QLabel("Axioma Player")
        self.lbl_titulo.setObjectName("songTitle")
        self.lbl_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        l.addWidget(self.lbl_titulo)
        
        self.lbl_artista = QLabel("Tu música favorita")
        self.lbl_artista.setObjectName("songArtist")
        self.lbl_artista.setAlignment(Qt.AlignmentFlag.AlignCenter)
        l.addWidget(self.lbl_artista)
        
        self.lbl_sig = QLabel("")
        self.lbl_sig.setObjectName("nextSongLabel")
        self.lbl_sig.setAlignment(Qt.AlignmentFlag.AlignCenter)
        l.addWidget(self.lbl_sig)
        l.addStretch()
        self.tabs.addTab(p, "REPRODUCTOR")

    def pestana_listas(self):
        p = QWidget()
        l = QVBoxLayout(p)
        l.setContentsMargins(20, 20, 20, 20)
        
        hl = QHBoxLayout()
        t = QLabel("Tus Playlists")
        t.setObjectName("pageTitle")
        btn = QPushButton("NUEVA LISTA"); btn.setObjectName("primaryBtn"); btn.clicked.connect(self.nueva_lista)
        hl.addWidget(t); hl.addStretch(); hl.addWidget(btn)
        l.addLayout(hl)

        c = QHBoxLayout()
        self.lst_listas = QListWidget()
        self.lst_listas.setMaximumWidth(240)
        self.lst_listas.currentItemChanged.connect(self.cambio_lista)
        self.lst_listas.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.lst_listas.customContextMenuRequested.connect(self.menu_listas)
        c.addWidget(self.lst_listas)
        
        vl = QVBoxLayout()
        self.busqueda_lista = QLineEdit(); self.busqueda_lista.setPlaceholderText("Filtrar en esta lista...")
        self.busqueda_lista.textChanged.connect(self.filtrar_lista)
        vl.addWidget(self.busqueda_lista)
        
        self.tab_lista = QTableWidget(0, 4)
        self.tab_lista.setHorizontalHeaderLabels(["Título", "Artista", "Dura", "Acción"])
        self.tab_lista.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.tab_lista.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tab_lista.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tab_lista.itemDoubleClicked.connect(self.reproducir_de_lista)
        self.tab_lista.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tab_lista.customContextMenuRequested.connect(self.menu_contextual_playlist_cancion)
        vl.addWidget(self.tab_lista)
        
        c.addLayout(vl)
        l.addLayout(c)
        self.tabs.addTab(p, "PLAYLISTS")

    def barra_controles(self, layout):
        b = QWidget(); b.setObjectName("bottomBar")
        bl = QHBoxLayout(b)
        bl.setContentsMargins(20, 10, 20, 10)
        
        inf = QHBoxLayout(); inf.setSpacing(12)
        self.mini_p = QLabel(); self.mini_p.setFixedSize(55, 55)
        self.mini_p.setStyleSheet("border-radius: 6px; background: #1a1a30; border: 1px solid #8B2BE2;")
        self.mini_p.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        tl = QVBoxLayout(); tl.setSpacing(2)
        self.mini_t = QLabel("--"); self.mini_t.setObjectName("miniTitle")
        self.mini_a = QLabel("--"); self.mini_a.setObjectName("miniArtist")
        tl.addWidget(self.mini_t); tl.addWidget(self.mini_a); tl.addStretch()
        
        inf.addWidget(self.mini_p); inf.addLayout(tl); inf.addStretch()
        bl.addLayout(inf, 1)

        cen = QVBoxLayout()
        btns = QHBoxLayout(); btns.setAlignment(Qt.AlignmentFlag.AlignCenter); btns.setSpacing(18)
        s = self.style()
        self.b_shuf = QPushButton("🔀"); self.b_shuf.setObjectName("controlBtn")
        self.b_shuf.setFixedSize(40, 40)
        self.b_shuf.setToolTip("Modo Aleatorio (Desactivado)")
        self.b_shuf.setCursor(Qt.CursorShape.PointingHandCursor)
        self.b_shuf.clicked.connect(self.toggle_shuf)

        self.b_prev = QPushButton("⏮"); self.b_prev.setObjectName("controlBtn")
        self.b_prev.setFixedSize(40, 40)
        self.b_prev.setToolTip("Anterior")
        self.b_prev.setCursor(Qt.CursorShape.PointingHandCursor)
        self.b_prev.clicked.connect(self.motor.anterior)

        self.b_play = QPushButton("▶"); self.b_play.setObjectName("playBtn")
        self.b_play.setFixedSize(70, 70)
        self.b_play.setToolTip("Reproducir/Pausar")
        self.b_play.setCursor(Qt.CursorShape.PointingHandCursor)
        self.b_play.clicked.connect(self.motor.alternar_reproduccion)

        self.b_next = QPushButton("⏭"); self.b_next.setObjectName("controlBtn")
        self.b_next.setFixedSize(40, 40)
        self.b_next.setToolTip("Siguiente")
        self.b_next.setCursor(Qt.CursorShape.PointingHandCursor)
        self.b_next.clicked.connect(self.motor.siguiente)

        self.b_rep = QPushButton("🔁"); self.b_rep.setObjectName("controlBtn")
        self.b_rep.setFixedSize(40, 40)
        self.b_rep.setToolTip("Modo Repetición: No repetir")
        self.b_rep.setCursor(Qt.CursorShape.PointingHandCursor)
        self.b_rep.clicked.connect(self.ciclar_rep)
        
        btns.addWidget(self.b_shuf); btns.addWidget(self.b_prev)
        btns.addWidget(self.b_play); btns.addWidget(self.b_next); btns.addWidget(self.b_rep)
        cen.addLayout(btns)
        
        pr = QHBoxLayout()
        self.cur_t = QLabel("0:00")
        self.slider = QSlider(Qt.Orientation.Horizontal); self.slider.sliderMoved.connect(self.motor.saltar_a)
        self.tot_t = QLabel("0:00")
        pr.addWidget(self.cur_t); pr.addWidget(self.slider); pr.addWidget(self.tot_t)
        cen.addLayout(pr)
        bl.addLayout(cen, 2)

        vol = QHBoxLayout(); vol.addStretch()
        self.vs = QSlider(Qt.Orientation.Horizontal); self.vs.setRange(0, 100); self.vs.setValue(70); self.vs.setFixedWidth(100)
        self.vs.valueChanged.connect(self.motor.establecer_volumen)
        vol.addWidget(QLabel("Vol:")); vol.addWidget(self.vs)
        bl.addLayout(vol, 1)
        layout.addWidget(b)

    def refrescar_biblioteca(self):
        self.tabla_bib.setRowCount(0)
        for i, c in enumerate(self.canciones):
            self.tabla_bib.insertRow(i)
            
            w = QWidget()
            cl = QHBoxLayout(w); cl.setContentsMargins(0,0,0,0); cl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            fav = self.es_fav(c)
            bf = QPushButton("❤" if fav else "♡")
            bf.setObjectName("favBtn")
            bf.setProperty("fav", "true" if fav else "false")
            bf.setFixedSize(32, 32)
            bf.setCursor(Qt.CursorShape.PointingHandCursor)
            bf.clicked.connect(lambda chk=False, s=c: self.tog_fav(s))
            cl.addWidget(bf)
            
            self.tabla_bib.setCellWidget(i, 0, w)
            self.tabla_bib.setItem(i, 1, QTableWidgetItem(c.get('title')))
            self.tabla_bib.setItem(i, 2, QTableWidgetItem(c.get('artist')))
            self.tabla_bib.setItem(i, 3, QTableWidgetItem(c.get('album')))
            self.tabla_bib.setItem(i, 4, QTableWidgetItem(formatear_duracion(c.get('duration', 0))))
        
        self.st_songs.setText(str(len(self.canciones)))
        self.st_folders.setText(str(len(self.carpetas)))
        self.st_lists.setText(str(len(self.listas)))
        txt = " | ".join(self.carpetas) if self.carpetas else "Sin fuentes"
        self.lbl_carpetas.setText(f"Fuentes: {txt}")
        self.filtrar_biblioteca(self.busqueda_bib.text())

    def es_fav(self, c):
        return any(x['filepath'] == c['filepath'] for x in self.listas.get("Favoritos", []))

    def tog_fav(self, c):
        f = self.listas.get("Favoritos", [])
        ex = next((i for i, x in enumerate(f) if x['filepath'] == c['filepath']), -1)
        if ex != -1: f.pop(ex)
        else: f.append(c)
        self.guardar(); self.refrescar_biblioteca()

    def reproducir_bib(self, item):
        self.repro_contexto(self.canciones, item.row())

    def reproducir_de_lista(self, item):
        nom = self.lst_listas.currentItem().text()
        self.repro_contexto(self.listas.get(nom, []), item.row())

    def repro_contexto(self, lista, idx):
        self.tabs.setCurrentIndex(1)
        self.motor.reproducir_cola(lista, idx, aleatorio=self.aleatorio_habilitado)

    def menu_contextual_biblioteca(self, pos):
        it = self.tabla_bib.itemAt(pos)
        if not it: return
        c = self.canciones[it.row()]
        self.lanzar_menu_cancion(pos, c, self.tabla_bib)

    def menu_contextual_playlist_cancion(self, pos):
        it = self.tab_lista.itemAt(pos)
        if not it: return
        n = self.lst_listas.currentItem().text()
        c = self.listas.get(n, [])[it.row()]
        self.lanzar_menu_cancion(pos, c, self.tab_lista)

    def lanzar_menu_cancion(self, pos, c, w):
        menu = QMenu()
        menu.addAction("Reproducir Ahora").triggered.connect(lambda: self.repro_contexto([c], 0))
        t_f = "Quitar de Favoritos" if self.es_fav(c) else "Marcar como Favorito"
        menu.addAction(t_f).triggered.connect(lambda: self.tog_fav(c))
        
        sub = menu.addMenu("Añadir a Playlist...")
        for n in self.listas.keys():
            if n != "Favoritos":
                sub.addAction(n).triggered.connect(lambda chk=False, name=n, s=c: self.meter_en_lista(name, s))
        
        menu.addAction("Eliminar archivo del sistema").triggered.connect(lambda: self.borrar_fisico(c))
        menu.exec(w.viewport().mapToGlobal(pos))

    def meter_en_lista(self, n, c):
        if c not in self.listas[n]:
            self.listas[n].append(c); self.guardar()
            if self.lst_listas.currentItem() and self.lst_listas.currentItem().text() == n:
                self.cambio_lista(self.lst_listas.currentItem())

    def borrar_fisico(self, c):
        q = QMessageBox.question(self, "Eliminar", f"¿Deseas borrar permanentemente {c.get('title')}?")
        if q == QMessageBox.StandardButton.Yes:
            try:
                if os.path.exists(c['filepath']): os.remove(c['filepath'])
                self.cargar_datos(); self.guardar()
            except Exception as e: print(f"Error: {e}")

    def nueva_lista(self):
        n, ok = QInputDialog.getText(self, "Nueva Playlist", "Nombre de la lista:")
        if ok and n and n not in self.listas:
            self.listas[n] = []; self.refrescar_listas(); self.guardar()

    def menu_listas(self, pos):
        it = self.lst_listas.itemAt(pos)
        if not it or it.text() == "Favoritos": return
        menu = QMenu()
        menu.addAction("Eliminar esta Playlist").triggered.connect(lambda: self.borrar_lista(it.text()))
        menu.exec(self.lst_listas.mapToGlobal(pos))

    def borrar_lista(self, n):
        if n in self.listas:
            del self.listas[n]; self.refrescar_listas(); self.guardar()

    def cambio_lista(self, it):
        if not it: return
        ss = self.listas.get(it.text(), [])
        self.tab_lista.setRowCount(0)
        for i, c in enumerate(ss):
            self.tab_lista.insertRow(i)
            self.tab_lista.setItem(i, 0, QTableWidgetItem(c.get('title')))
            self.tab_lista.setItem(i, 1, QTableWidgetItem(c.get('artist')))
            self.tab_lista.setItem(i, 2, QTableWidgetItem(formatear_duracion(c.get('duration', 0))))
            
            w = QWidget()
            cl = QHBoxLayout(w); cl.setContentsMargins(0,0,0,0); cl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            bx = QPushButton("✕"); bx.setObjectName("delBtn"); bx.setFixedSize(26, 26)
            bx.setCursor(Qt.CursorShape.PointingHandCursor)
            bx.clicked.connect(lambda chk=False, s=c, n=it.text(): self.sacar_de_lista(n, s))
            cl.addWidget(bx)
            self.tab_lista.setCellWidget(i, 3, w)
        self.filtrar_lista(self.busqueda_lista.text())

    def sacar_de_lista(self, n, c):
        if c in self.listas.get(n, []):
            self.listas[n].remove(c); self.guardar()
            self.cambio_lista(self.lst_listas.currentItem())

    def guardar(self):
        lp = {}
        for n, cs in self.listas.items(): lp[n] = [x['filepath'] for x in cs if 'filepath' in x]
        guardar_configuracion({"folders": self.carpetas, "playlists": lp})

    def toggle_shuf(self):
        self.aleatorio_habilitado = not self.aleatorio_habilitado
        st = "true" if self.aleatorio_habilitado else "false"
        self.b_shuf.setProperty("active", st)
        self.b_shuf.setToolTip(f"Aleatorio ({'Activo' if self.aleatorio_habilitado else 'Inactivo'})")
        self.b_shuf.style().unpolish(self.b_shuf)
        self.b_shuf.style().polish(self.b_shuf)

    def ciclar_rep(self):
        self.modo_repeticion = (self.modo_repeticion + 1) % 3
        # 0: None (Blanco), 1: All (Cian), 2: One (Cian + 🔂)
        modos = ["🔁", "🔁", "🔂"]
        activos = ["false", "true", "true"]
        txts = ["Repetir: No", "Repetir: Todo", "Repetir: Una"]
        
        self.b_rep.setText(modos[self.modo_repeticion])
        self.b_rep.setProperty("active", activos[self.modo_repeticion])
        self.b_rep.setToolTip(txts[self.modo_repeticion])
        
        self.b_rep.style().unpolish(self.b_rep)
        self.b_rep.style().polish(self.b_rep)
        self.motor.modo_repetir_uno = (self.modo_repeticion == 2)

    def actualizar_posicion(self, ms):
        if not self.slider.isSliderDown(): self.slider.setValue(ms)
        self.cur_t.setText(formatear_duracion(ms // 1000))

    def actualizar_duracion(self, ms):
        self.slider.setRange(0, ms); self.tot_t.setText(formatear_duracion(ms // 1000))

    def actualizar_estado(self, st):
        if st == QMediaPlayer.PlaybackState.PlayingState:
            self.b_play.setText("⏸")
            self.disco.iniciar_giro()
        else:
            self.b_play.setText("▶")
            self.disco.detener_giro()

    def actualizar_cancion(self, m):
        self.lbl_titulo.setText(m.get('title', 'Axioma Music'))
        self.lbl_artista.setText(m.get('artist', 'Desconocido'))
        self.mini_t.setText(m.get('title', '--')); self.mini_a.setText(m.get('artist', '--'))
        dd = obtener_metadatos(m.get('filepath', ''))
        co = dd.get('cover_art')
        self.disco.establecer_portada(co)
        if co:
            im = QImage(); im.loadFromData(co)
            px = QPixmap.fromImage(im).scaled(55, 55, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
            self.mini_p.setPixmap(px)
        else: self.mini_p.clear()
        self.act_sig()

    def act_sig(self):
        if self.motor.tiene_siguiente():
            s = self.motor.cola[self.motor.indice_actual+1]
            self.lbl_sig.setText(f"Siguiente: {s.get('title')}")
        else: self.lbl_sig.setText("")

    def al_terminar_cola(self): self.lbl_titulo.setText("Lista terminada"); self.disco.detener_giro()

    def filtrar_biblioteca(self, t):
        for i in range(self.tabla_bib.rowCount()):
            v = False
            for j in [1, 2, 3]:
                it = self.tabla_bib.item(i, j)
                if it and t.lower() in it.text().lower(): v = True
            self.tabla_bib.setRowHidden(i, not v)

    def filtrar_lista(self, t):
        for i in range(self.tab_lista.rowCount()):
            v = False
            for j in [0, 1]:
                it = self.tab_lista.item(i, j)
                if it and t.lower() in it.text().lower(): v = True
            self.tab_lista.setRowHidden(i, not v)

    def anadir_carpeta(self):
        d = QFileDialog.getExistingDirectory(self, "Elija Carpeta")
        if d and d not in self.carpetas: self.carpetas.append(d); self.cargar_datos(); self.guardar()

    def quitar_carpeta(self):
        if not self.carpetas: return
        c, ok = QInputDialog.getItem(self, "Quitar", "Carpeta:", self.carpetas, 0, False)
        if ok and c: self.carpetas.remove(c); self.cargar_datos(); self.guardar()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    win = VentanaPrincipal()
    win.showMaximized()
    sys.exit(app.exec())
