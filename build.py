import subprocess
import shutil
import os
import sys

DIR_PROYECTO = os.path.dirname(os.path.abspath(__file__))
DIR_DIST = os.path.join(DIR_PROYECTO, "dist")
DIR_BUILD = os.path.join(DIR_PROYECTO, "build")

def limpiar():
    for d in [DIR_DIST, DIR_BUILD]:
        if os.path.exists(d): shutil.rmtree(d)
    spec = os.path.join(DIR_PROYECTO, "AxiomaMusic.spec")
    if os.path.exists(spec): os.remove(spec)

def compilar():
    limpiar()
    ruta_icono = os.path.join(DIR_PROYECTO, "Ax.ico")
    resultado = subprocess.run([
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--noconsole",
        "--name=AxiomaMusic",
        f"--icon={ruta_icono}",
        "--add-data", "Ax.png;.",
        "--hidden-import=PyQt6.QtMultimedia",
        "--hidden-import=PyQt6.QtMultimediaWidgets",
        "main.py"
    ], cwd=DIR_PROYECTO)
    
    if resultado.returncode == 0:
        exe = os.path.join(DIR_DIST, "AxiomaMusic.exe")
        if os.path.exists(exe):
            mb = os.path.getsize(exe) / (1024 * 1024)
            print(f"Éxito: {exe} ({mb:.1f} MB)")

if __name__ == "__main__":
    compilar()
