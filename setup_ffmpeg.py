import os
import sys
import subprocess
import shutil

def existe_ffmpeg():
    if shutil.which("ffmpeg"): return True
    for ruta in os.environ["PATH"].split(os.pathsep):
        if os.path.exists(os.path.join(ruta, "ffmpeg.exe")): return True
    return False

def configurar():
    if existe_ffmpeg(): return True
    print("ffmpeg no encontrado.")
    return False

if __name__ == "__main__":
    configurar()
