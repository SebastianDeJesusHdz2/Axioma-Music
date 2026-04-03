import sys
import os
import traceback
import ctypes

def configurar_registro():
    ruta = os.path.join(os.path.expanduser('~'), '.axioma_music', 'app.log')
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    print("\n--- Inicio App ---", flush=True)

def manejador_excepciones(tipo, valor, traza):
    traceback.print_exception(tipo, valor, traza)
    try:
        from PyQt6.QtWidgets import QMessageBox
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle("Error Crítico")
        msg.setText(f"Error inesperado:\n{tipo.__name__}: {valor}")
        msg.exec()
    except:
        pass

def iniciar():
    configurar_registro()
    sys.excepthook = manejador_excepciones
    if os.name == 'nt':
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("axioma.music.player.1.0")
        except:
            pass
    try:
        os.environ["PATH"] += os.pathsep + os.path.dirname(sys.executable)
        from PyQt6.QtWidgets import QApplication
        from ui_main import VentanaPrincipal
        app = QApplication(sys.argv)
        app.setStyle("Fusion")
        ventana = VentanaPrincipal()
        ventana.show()
        sys.exit(app.exec())
    except Exception:
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    iniciar()
