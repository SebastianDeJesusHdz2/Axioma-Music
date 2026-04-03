# 🎵 Axioma Music Player

Axioma is a premium, high-performance music player built with **Python 3** and **PyQt6**. It features a modern, high-contrast dark interface inspired by high-end audio hardware, with vibrant atmospheric accents (Cyan, Violet) and smooth interactive animations.

![Preview](C:/Users/sebas/.gemini/antigravity/brain/a668f82e-09aa-468c-bb3e-15aa37c12f15/media__1775157180460.png)

---

## ✨ Características Principales

*   **Reproductor de Vinilo Animado**: El reproductor central incluye una representación visual de un disco de vinilo que gira en tiempo real durante la reproducción, con surcos realistas y resplandor neón.
*   **Controles de Navegación Esféricos**: Botones circulares blancos de alta visibilidad que cambian de estado (Cian brillante) cuando funciones como el **Aleatorio** o la **Repetición** están activos.
*   **Gestor de Biblioteca Inteligente**: Escaneo automático de carpetas de música, filtrado en tiempo real y detección de metadatos (Título, Artista, Álbum, Duración, Portadas).
*   **Gestión de Playlists**: Creación, edición y eliminación de listas de reproducción personalizadas. Lista de **Favoritos** integrada con marcadores visuales (Corazón rojo/vacío).
*   **Motor de Audio FFmpeg**: Compatible con una amplia gama de formatos de audio (MP3, WAV, FLAC, M4A) mediante la integración de `QtMultimedia` y `FFmpeg`.
*   **Persistencia de Configuración**: Tus carpetas de música y listas de reproducción se guardan automáticamente en un directorio de configuración seguro en tu sistema.

---

## 🛠️ Requisitos del Sistema

*   **Python**: Versión 3.10 o superior recomendada.
*   **FFmpeg**: El sistema requiere que FFmpeg esté instalado y configurado en el `PATH` para poder decodificar la mayoría de los archivos de audio.
*   **S.O.**: Optimizado para Windows 10/11 (pero compatible con Linux/macOS mediante Python).

---

## 🚀 Instalación y Uso

1.  **Clona este repositorio**:
    ```bash
    git clone https://github.com/tu-usuario/axioma-music-player.git
    cd axioma-music-player
    ```

2.  **Configura un entorno virtual (recomendado)**:
    ```bash
    python -m venv .venv
    # En Windows:
    .venv\Scripts\activate
    # En Linux/Mac:
    source .venv/bin/activate
    ```

3.  **Instala las dependencias necesarias**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Ejecuta la aplicación**:
    ```bash
    python main.py
    ```

---

## 📦 Crear Ejecutable para Windows (.exe)

Este proyecto incluye un script de construcción (`build.py`) automatizado que utiliza **PyInstaller**:

```bash
python build.py
```
El archivo ejecutable se generará en la carpeta `dist/`, empaquetando todos los iconos y recursos necesarios sin necesidad de consola.

---

## 🎨 Diseño Visual

*   **Paleta de Colores**: Profundo Obscuro (`#0c0c18`), Cian Eléctrico (`#00D9FF`), Violeta Vibrante (`#8B2BE2`), Blanco Puro (`#ffffff`).
*   **Tipografía**: Segoe UI / Manrope.
*   **Estilo**: Glassmorphism suave, esferas de alto contraste y animaciones de rotación a 60 FPS.

---

*Desarrollado como una alternativa premium y personalizable para los amantes de la música que valoran la estética retro-moderna.*
