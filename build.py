import subprocess
import shutil
import os
import sys

DIR_PROY = os.path.dirname(os.path.abspath(__file__))
DIR_SAL = os.path.join(DIR_PROY, "dist")
DIR_TMP = os.path.join(DIR_PROY, "build")


def limpiar():
    for d in [DIR_SAL, DIR_TMP]:
        if os.path.exists(d):
            shutil.rmtree(d)
    for spec in ["AxiomaMusic.spec", "VibePulse.spec"]:
        ruta = os.path.join(DIR_PROY, spec)
        if os.path.exists(ruta):
            os.remove(ruta)


def compilar():
    limpiar()
    icono = os.path.join(DIR_PROY, "Ax.ico")

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--noconsole",
        "--name=VibePulse",
        f"--icon={icono}",
        "--add-data", f"web{os.pathsep}web",
        "--add-data", f"Ax.png{os.pathsep}.",
        "--hidden-import=pygame",
        "--hidden-import=pygame.mixer",
        "--hidden-import=pygame.mixer_music",
        "--hidden-import=webview",
        "--hidden-import=mutagen",
        "--hidden-import=mutagen.mp3",
        "--hidden-import=mutagen.flac",
        "--hidden-import=mutagen.oggvorbis",
        "--hidden-import=mutagen.mp4",
        "--hidden-import=mutagen.wave",
        "--hidden-import=mutagen.aac",
        "--hidden-import=mutagen.oggopus",
        "--collect-all=webview",
        "main.py"
    ]

    print("=" * 60)
    print("  VIBE PULSE - Build")
    print("=" * 60)

    res = subprocess.run(cmd, cwd=DIR_PROY)

    if res.returncode == 0:
        exe = os.path.join(DIR_SAL, "VibePulse.exe")
        if os.path.exists(exe):
            mb = os.path.getsize(exe) / (1024 * 1024)
            print()
            print("=" * 60)
            print(f"  [OK] Build exitoso!")
            print(f"  Exe: {exe}")
            print(f"  Tam: {mb:.1f} MB")
            print("=" * 60)
    else:
        print(f"  [ERROR] Fallo ({res.returncode})")


if __name__ == "__main__":
    compilar()
