import sys
import os
import traceback
import faulthandler

RUTA_LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "crash_log.txt")
f_log = open(RUTA_LOG, "w", encoding="utf-8")
faulthandler.enable(file=f_log)

class EscritorTee:
    def __init__(self, *escritores):
        self.escritores = escritores
    def write(self, s):
        for w in self.escritores:
            try:
                w.write(s)
                w.flush()
            except:
                pass
    def flush(self):
        for w in self.escritores:
            try:
                w.flush()
            except:
                pass

sys.stderr = EscritorTee(sys.__stderr__, f_log)
sys.stdout = EscritorTee(sys.__stdout__, f_log)

def gancho_excepciones(tipo, valor, traza):
    msg = "".join(traceback.format_exception(tipo, valor, traza))
    print(f"ERROR:\n{msg}", file=sys.__stderr__)

sys.excepthook = gancho_excepciones

try:
    from PyQt6.QtWidgets import QApplication
    from ui_main import VentanaPrincipal
    os.environ["PATH"] += os.pathsep + os.path.dirname(sys.executable)
    app = QApplication(sys.argv)
    ventana = VentanaPrincipal()
    ventana.show()
    sys.exit(app.exec())
except Exception:
    print(f"FATAL:\n{traceback.format_exc()}")
    input("Pulsa Enter...")
finally:
    f_log.close()
