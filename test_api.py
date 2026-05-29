import sys, os, time, threading, webview
sys.path.insert(0, r'c:\Users\sebas\Documents\Tareas y pendientes\Repo\app para musica')
os.chdir(r'c:\Users\sebas\Documents\Tareas y pendientes\Repo\app para musica')
from main import Api

a = Api()
html = os.path.join('web', 'index.html')
vent = webview.create_window('Test', url=html, js_api=a)
a.set_window(vent)

def do_check():
    time.sleep(3)
    try:
        vent.evaluate_js('window.pywebview.api.get_library().then(res => { document.getElementById("lbl-carpetas").textContent = "API returned: " + res.length; }).catch(err => { document.getElementById("lbl-carpetas").textContent = "API error: " + String(err); })')
        time.sleep(2)
        res = vent.evaluate_js('document.getElementById("lbl-carpetas").textContent')
        print('LBL:', res)
    except Exception as e:
        print('ERROR:', e)
    finally:
        vent.destroy()

threading.Thread(target=do_check, daemon=True).start()
webview.start()
a.motor.limpiar()
