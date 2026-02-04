#!/usr/bin/env python3
import subprocess, time, cv2, numpy as np, requests, os
from datetime import datetime

# --- CONFIGURAÇÕES ---
VIP_LINK = "https://discord.com/api/webhooks/1069275367581438022/kBC-roJY3Mb70Va14XOw33CH5CxvVW8dUDw0UTYPLPMFlMoF7W1rN2FD45Hq4VBjfO4M"
WEBHOOK_DISCORD = "https://discord.com/api/webhooks/1069275367581438022/kBC-roJY3Mb70Va14XOw33CH5CxvVW8dUDw0UTYPLPMFlMoF7W1rN2FD45Hq4VBjfO4M"
KEY_API_URL = "http://127.0.0.1:3000/get_key" # Onde seu bot local hospeda a key
TEMPLATES_DIR = "templates"
THRESHOLD = 0.85 # Precisão da busca de imagem (0.8 = 80%)

# Variáveis Globais de Estado
last_screen_hash = None
last_screen_time = time.time()
current_package_index = 0

def log(tag, msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] [{tag}] {msg}")

# --- ADB WRAPPER ---
def adb(cmd_str):
    try:
        # Executa comandos adb shell
        cmd = f"adb {cmd_str}"
        res = subprocess.run(cmd.split(), capture_output=True, timeout=10)
        return res.stdout
    except:
        return b""

def get_installed_roblox():
    # Busca pacotes originais e clones comuns
    raw = adb("shell pm list packages")
    packages = []
    for line in raw.decode().splitlines():
        pkg = line.replace("package:", "").strip()
        if "roblox" in pkg.lower():
            packages.append(pkg)
    if not packages:
        log("ERRO", "Nenhum Roblox encontrado!")
    else:
        log("SYSTEM", f"Roblox detectados: {packages}")
    return packages

# --- VISÃO COMPUTACIONAL ---
def screenshot():
    raw = adb("exec-out screencap -p")
    if not raw:
        return None
    arr = np.frombuffer(raw, np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    return img

def find_click(screen, template_name):
    path = os.path.join(TEMPLATES_DIR, template_name)
    if not os.path.exists(path):
        return False
        
    tpl = cv2.imread(path)
    if tpl is None: return False

    res = cv2.matchTemplate(screen, tpl, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(res)

    if max_val >= THRESHOLD:
        h, w = tpl.shape[:2]
        cx = max_loc[0] + w // 2
        cy = max_loc[1] + h // 2
        log("CLICK", f"Clicando em {template_name} ({max_val:.2f})")
        adb(f"shell input tap {cx} {cy}")
        return True
    return False

# --- FUNÇÕES DE CHECK ---
def check_freeze(screen):
    global last_screen_hash, last_screen_time
    
    # Reduz a imagem para comparar rápido
    small = cv2.resize(screen, (50, 50))
    current_hash = hash(small.tobytes())

    if current_hash == last_screen_hash:
        if time.time() - last_screen_time > 60: # 60 segundos sem mudar nada
            log("FREEZE", "Tela congelada detectada!")
            return True
    else:
        last_screen_hash = current_hash
        last_screen_time = time.time()
    
    return False

def get_clipboard_link():
    # Tenta pegar link via Termux API (mais confiável) ou logcat
    try:
        # Método 1: Termux API (Requer pkg install termux-api e app instalado)
        res = subprocess.run(["termux-clipboard-get"], capture_output=True, timeout=3)
        text = res.stdout.decode().strip()
        if "http" in text: return text
    except:
        pass
    
    # Método 2: Fallback simples (pode não funcionar no Android 10+)
    return ""

# --- LÓGICA PRINCIPAL (STATE MACHINE) ---

def resolver_key_system(screen):
    # 1. Detectou botão Receive Key?
    if find_click(screen, "receive_key.png"):
        log("KEY", "Iniciando processo de Key...")
        time.sleep(5) # Espera abrir navegador
        
        # Fecha navegador para garantir foco
        adb("shell am force-stop com.android.chrome")
        time.sleep(1)
        
        link = get_clipboard_link()
        if not link:
            log("KEY", "Link não encontrado no clipboard. Tentando clicar novamente...")
            return True # Retorna para tentar de novo
            
        log("KEY", f"Link capturado: {link[:30]}...")
        
        # Envia para Discord/Bypass
        try:
            requests.post(WEBHOOK_DISCORD, json={"content": f"!bypass {link}"})
        except:
            log("ERRO", "Falha ao enviar webhook")

        # Aguarda a Key
        log("KEY", "Aguardando Key da API local...")
        key_recebida = None
        for _ in range(30): # Tenta por 60 segundos
            try:
                r = requests.get(KEY_API_URL, timeout=2)
                if len(r.text) > 5:
                    key_recebida = r.text.strip()
                    break
            except:
                pass
            time.sleep(2)
            
        if key_recebida:
            log("KEY", f"Key recebida! Colando...")
            # Cola a key via ADB
            adb(f'shell input text "{key_recebida}"')
            time.sleep(1)
            # Clica no Enter Key se existir imagem, ou Enter do teclado
            if not find_click(screen, "enter_key.png"):
                 adb("shell input keyevent 66") # Enter
            
            time.sleep(2)
            find_click(screen, "continue.png")
            return True
            
    return False

def reiniciar_roblox(package_name):
    log("RECONNECT", f"Reiniciando {package_name}...")
    adb(f"shell am force-stop {package_name}")
    time.sleep(2)
    # Abre o app (monkey é um truque para abrir sem saber a Activity exata)
    adb(f"shell monkey -p {package_name} -c android.intent.category.LAUNCHER 1")
    time.sleep(10) # Espera carregar menu inicial
    
    # Abre o Link VIP (Deeplink)
    log("RECONNECT", "Entrando no VIP...")
    adb(f'shell am start -a android.intent.action.VIEW -d "{VIP_LINK}" {package_name}')

def main():
    log("SYSTEM", "Monitor Inteligente Iniciado v2.0")
    
    packages = get_installed_roblox()
    if not packages: return

    while True:
        try:
            screen = screenshot()
            if screen is None:
                log("ERRO", "Falha no Screenshot. ADB desconectado?")
                time.sleep(5)
                continue

            # --- PRIORIDADE 1: KEY SYSTEM ---
            # Se encontrar qualquer elemento de key, foca nisso
            if resolver_key_system(screen):
                time.sleep(2)
                continue

            # --- PRIORIDADE 2: FREEZE ---
            if check_freeze(screen):
                reiniciar_roblox(packages[0])
                last_screen_time = time.time() # Reseta timer
                continue

            # --- PRIORIDADE 3: ESTÁ RODANDO? ---
            # Verifica se o processo do Roblox principal morreu
            proc = adb(f"shell pidof {packages[0]}")
            if not proc:
                log("MONITOR", "Roblox fechado. Reiniciando...")
                reiniciar_roblox(packages[0])
                time.sleep(15)
                continue
            
            # Se chegou aqui, está tudo bem. Espera um pouco.
            time.sleep(5)

        except Exception as e:
            log("CRITICAL", f"Erro no loop: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
