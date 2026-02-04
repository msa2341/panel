#!/usr/bin/env python3
import subprocess, time, cv2, numpy as np, requests, os, signal
from datetime import datetime

VIP_LINK = "COLE_SEU_LINK_VIP"
WEBHOOK = "COLE_SEU_WEBHOOK"
KEY_ENDPOINT = "http://127.0.0.1:3000/get_key"

TEMPLATES_DIR = "templates"
THRESHOLD = 0.80

def log(tag, msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] [{tag}] {msg}")

def adb(cmd):
    try:
        r = subprocess.run(
            ["adb"] + cmd.split(),
            capture_output=True,
            timeout=15
        )
        return r.stdout
    except:
        return b""

# --------------------------------------------------
# 📸 SCREENSHOT
# --------------------------------------------------
def screenshot():
    img = adb("exec-out screencap -p")
    img = cv2.imdecode(np.frombuffer(img, np.uint8), cv2.IMREAD_COLOR)
    return img

# --------------------------------------------------
# 🔍 TEMPLATE MATCH
# --------------------------------------------------
def find_template(screen, template_name):
    tpl = cv2.imread(os.path.join(TEMPLATES_DIR, template_name))
    if tpl is None:
        return None

    res = cv2.matchTemplate(screen, tpl, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(res)

    if max_val >= THRESHOLD:
        h, w = tpl.shape[:2]
        x = max_loc[0] + w // 2
        y = max_loc[1] + h // 2
        return (x, y, max_val)

    return None

# --------------------------------------------------
# 🖱️ CLICK
# --------------------------------------------------
def tap(x, y):
    adb(f"shell input tap {x} {y}")

# --------------------------------------------------
# 🔑 RECEIVE KEY FLOW
# --------------------------------------------------
def handle_receive_key():
    screen = screenshot()

    rk = find_template(screen, "receive_key.png")
    if not rk:
        return False

    log("KEY", "Receive Key detectado")
    tap(rk[0], rk[1])
    time.sleep(5)

    adb("shell am force-stop com.android.chrome")

    clip = adb("shell logcat -d | grep Clipboard | tail -n 1").decode()
    if "http" not in clip:
        log("KEY", "Link não copiado")
        return False

    link = clip.split("text=")[-1].strip()
    log("KEY", "Link capturado")

    requests.post(WEBHOOK, json={"content": f"!bypass {link}"})

    key = None
    for _ in range(60):
        try:
            r = requests.get(KEY_ENDPOINT, timeout=3)
            if len(r.text.strip()) > 5:
                key = r.text.strip()
                break
        except:
            pass
        time.sleep(2)

    if not key:
        log("KEY", "Key não retornou")
        return False

    log("KEY", "Colando key")
    adb(f'shell am broadcast -a clipper.set -e text "{key}"')
    time.sleep(1)

    screen = screenshot()

    ek = find_template(screen, "enter_key.png")
    if ek:
        tap(ek[0], ek[1])
        time.sleep(1)
        adb("shell input keyevent 279")

    time.sleep(1)

    cont = find_template(screen, "continue.png")
    if cont:
        tap(cont[0], cont[1])

    log("KEY", "Processo finalizado")
    return True

# --------------------------------------------------
# 🔁 LOOP
# --------------------------------------------------
def main():
    log("SYSTEM", "Monitor iniciado")
    while True:
        handle_receive_key()
        time.sleep(5)

if __name__ == "__main__":
    main()
