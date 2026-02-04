#!/usr/bin/env python3
"""
🖥️ Roblox AutoRejoin - Hacker Theme Ultimate 🖥️
Interface cyberpunk com Visão Computacional e Auto Key System
Versão: 5.1 - Fixed Coordinates Delta Update
"""

import os
import sys
import time
import json
import subprocess
import requests
import cv2
import numpy as np
from datetime import datetime
from typing import Dict

# ============================================
# 🎮 CONFIGURAÇÃO
# ============================================
CONFIG_FILE = "hacker_config.json"
TEMPLATES_DIR = "templates"
KEY_API_URL = "http://127.0.0.1:3000/get_key"

# Coordenadas extraídas das suas prints (Delta UI)
COORD_INPUT_BOX = "779 228"   # Campo para colar a key
COORD_CONFIRM_BTN = "801 351" # Botão Checkpoint/Continue

DEFAULT_CONFIG = {
    "web_link": "https://www.roblox.com/games/1537690962/Bee-Swarm-Simulator?privateServerLinkCode=54979473479340063836604255875447",
    "webhook_url": "https://discord.com/api/webhooks/1069275367581438022/kBC-roJY3Mb70Va14XOw33CH5CxvVW8dUDw0UTYPLPMFlMoF7W1rN2FD45Hq4VBjfO4M",
    "check_interval": 5,
    "low_cpu_threshold": 8.0,
    "max_lowcpu_time": 10,
    "cooldown_time": 15,
    "packages": [],
    "threshold": 0.85
}

# ============================================
# 🎨 TEMA HACKER CYBERPUNK
# ============================================
class HackerTheme:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    MATRIX = "\033[38;5;46m"
    CYAN = "\033[38;5;51m"
    PINK = "\033[38;5;201m"
    PURPLE = "\033[38;5;93m"
    RED = "\033[38;5;196m"
    YELLOW = "\033[38;5;226m"
    GREEN_DARK = "\033[38;5;22m"
    GREEN_NEON = "\033[38;5;82m"

# ============================================
# 🎨 INTERFACE HACKER
# ============================================
class HackerUI:
    @staticmethod
    def clear_screen():
        os.system('cls' if os.name == 'nt' else 'clear')

    @staticmethod
    def print_matrix_banner():
        print(f"{HackerTheme.MATRIX}")
        print("╔══════════════════════════════════════════════════════════════╗")
        print("║  █▀█░█▀█░█▀▄░█░░░█▀█░█░█░░░█▀▄▀█░█▀█░█▀▄░█▀▀░█▀▄  ║")
        print("║  █▀▄░█░█░█▀▄░█░░░█░█░▄▀▄░░░█░▀░█░█░█░█░█░█▀▀░█▀▄  ║")
        print("║  ▀░▀░▀▀▀░▀▀░░▀▀▀░▀▀▀░▀░▀░░░▀░░░▀░▀▀▀░▀▀░░▀▀▀░▀░▀  ║")
        print("╠══════════════════════════════════════════════════════════════╣")
        print(f"║  {HackerTheme.PINK}v5.1 • DELTA COORDINATES • AUTO BYPASS ENABLED      {HackerTheme.MATRIX}║")
        print("╚══════════════════════════════════════════════════════════════╝")
        print(f"{HackerTheme.RESET}")

    @staticmethod
    def print_log_entry(tag: str, message: str, level: str = "INFO"):
        colors = {
            "INFO": HackerTheme.CYAN, "WARN": HackerTheme.YELLOW,
            "ERROR": HackerTheme.RED, "SUCCESS": HackerTheme.GREEN_NEON,
            "KEY": HackerTheme.PINK, "VISION": HackerTheme.PURPLE
        }
        timestamp = datetime.now().strftime("%H:%M:%S")
        color = colors.get(level, HackerTheme.CYAN)
        print(f"{HackerTheme.GREEN_DARK}[{timestamp}] "
              f"[{color}{tag:<8}{HackerTheme.GREEN_DARK}] "
              f"{HackerTheme.RESET}{message}")

# ============================================
# 🧠 MONITOR INTELIGENTE (OPENCV + ADB)
# ============================================
class HackerMonitor:
    def __init__(self, config: dict):
        self.config = config
        self.running = True
        self.lowcpu_count: Dict[str, int] = {}
        self.last_screen_hash = None
        self.last_screen_time = time.time()
        
        if not os.path.exists(TEMPLATES_DIR):
            os.makedirs(TEMPLATES_DIR)

    # --- FUNÇÕES ADB BÁSICAS ---
    def run_adb(self, cmd: str, binary=False):
        try:
            args = ["adb"] + cmd.split()
            res = subprocess.run(args, capture_output=True, timeout=10)
            return res.stdout if binary else res.stdout.decode().strip()
        except:
            return b"" if binary else ""

    # --- VISÃO COMPUTACIONAL ---
    def screenshot(self):
        raw = self.run_adb("exec-out screencap -p", binary=True)
        if not raw: return None
        try:
            arr = np.frombuffer(raw, np.uint8)
            return cv2.imdecode(arr, cv2.IMREAD_COLOR)
        except:
            return None

    def find_click(self, screen, template_name):
        path = os.path.join(TEMPLATES_DIR, template_name)
        if not os.path.exists(path): return False
        
        tpl = cv2.imread(path)
        if tpl is None: return False

        res = cv2.matchTemplate(screen, tpl, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(res)

        if max_val >= self.config["threshold"]:
            h, w = tpl.shape[:2]
            cx, cy = max_loc[0] + w // 2, max_loc[1] + h // 2
            HackerUI.print_log_entry("VISION", f"Objeto detectado: {template_name} ({max_val:.2f})", "SUCCESS")
            self.run_adb(f"shell input tap {cx} {cy}")
            return True
        return False

    def check_freeze(self, screen):
        small = cv2.resize(screen, (50, 50))
        curr_hash = hash(small.tobytes())
        
        if curr_hash == self.last_screen_hash:
            if time.time() - self.last_screen_time > 60:
                return True
        else:
            self.last_screen_hash = curr_hash
            self.last_screen_time = time.time()
        return False

    # --- LÓGICA DO KEY SYSTEM (ATUALIZADA) ---
    def handle_key_system(self, screen):
        # Gatilho: Ainda usa imagem para saber SE precisa da key, mas usa coords para agir
        # Você pode substituir "receive_key.png" por qualquer imagem que apareça quando o Delta abre
        if self.find_click(screen, "receive_key.png") or self.find_click(screen, "get_key.png"):
            HackerUI.print_log_entry("KEY", "⚠️ DELTA UI DETECTADO! INICIANDO BYPASS...", "KEY")
            time.sleep(5) 
            
            self.run_adb("shell am force-stop com.android.chrome")
            time.sleep(1)
            
            # 1. Tenta pegar link
            link = ""
            try:
                res = subprocess.run(["termux-clipboard-get"], capture_output=True, timeout=3)
                link = res.stdout.decode().strip()
            except: pass
            
            if "http" not in link:
                HackerUI.print_log_entry("KEY", "Link não copiado. Aguardando...", "WARN")
                return True
                
            HackerUI.print_log_entry("KEY", f"Link capturado: {link[:30]}...", "SUCCESS")
            
            # Webhook Discord
            if self.config["webhook_url"]:
                try: requests.post(self.config["webhook_url"], json={"content": f"!bypass {link}"})
                except: pass

            # 2. Aguarda Key da API Local
            HackerUI.print_log_entry("KEY", "Solicitando Key à API...", "INFO")
            key = None
            for _ in range(20):
                try:
                    r = requests.get(KEY_API_URL, timeout=2)
                    if len(r.text) > 5:
                        key = r.text.strip()
                        break
                except: pass
                time.sleep(2)
            
            if key:
                HackerUI.print_log_entry("KEY", "🔑 KEY RECEBIDA! INJETANDO COM COORDENADAS...", "SUCCESS")
                
                # --- PASSO A PASSO COM COORDENADAS FIXAS ---
                
                # A. Clicar no Campo de Texto (Foco)
                HackerUI.print_log_entry("ACTION", f"Clicando no input: {COORD_INPUT_BOX}", "INFO")
                self.run_adb(f'shell input tap {COORD_INPUT_BOX}')
                time.sleep(0.5)
                
                # B. Limpar campo (Opcional - seleciona tudo e apaga)
                # self.run_adb("shell input keyevent 29 29 112") # Ctrl+A Del (complicado no android puro)
                # Vamos confiar que o clique foca no fim ou o campo está vazio
                
                # C. Digitar a Key
                HackerUI.print_log_entry("ACTION", "Digitando Key...", "INFO")
                # Escapa caracteres especiais se necessário
                safe_key = key.replace(" ", "%s").replace("&", "\&")
                self.run_adb(f'shell input text "{safe_key}"')
                time.sleep(1.0)
                
                # D. Clicar no botão Continue/Checkpoint
                HackerUI.print_log_entry("ACTION", f"Confirmando Checkpoint: {COORD_CONFIRM_BTN}", "SUCCESS")
                self.run_adb(f'shell input tap {COORD_CONFIRM_BTN}')
                
                HackerUI.print_log_entry("KEY", "🔓 FLUXO DE INJEÇÃO CONCLUÍDO", "SUCCESS")
            else:
                HackerUI.print_log_entry("KEY", "Timeout: Nenhuma key recebida da API", "ERROR")
            
            return True 
        return False

    # --- GERENCIAMENTO DE APP ---
    def restart_app(self, package):
        HackerUI.print_log_entry("RESTART", f"Reiniciando {package}...", "WARN")
        self.run_adb(f"shell am force-stop {package}")
        time.sleep(2)
        cmd = f"shell am start -a android.intent.action.VIEW -d \"{self.config['web_link']}\" {package}"
        self.run_adb(cmd)
        self.lowcpu_count[package] = 0

    # --- LOOP PRINCIPAL ---
    def start(self):
        HackerUI.print_matrix_banner()
        if not self.config["packages"]:
            HackerUI.print_log_entry("ERROR", "Configure os pacotes na opção 2!", "ERROR")
            return

        HackerUI.print_log_entry("SYSTEM", "Monitoramento Ativo. Pressione Ctrl+C para sair.", "INFO")
        
        while self.running:
            try:
                screen = self.screenshot()
                if screen is None:
                    HackerUI.print_log_entry("ADB", "Erro de conexão ADB / Screen", "ERROR")
                    time.sleep(5)
                    continue

                if self.handle_key_system(screen):
                    time.sleep(2)
                    continue

                if self.check_freeze(screen):
                    HackerUI.print_log_entry("FREEZE", "Tela congelada! Reiniciando...", "ERROR")
                    self.restart_app(self.config["packages"][0])
                    continue

                for pkg in self.config["packages"]:
                    pid = self.run_adb(f"shell pidof {pkg}")
                    
                    if not pid:
                        HackerUI.print_log_entry("PROC", f"{pkg} fechado. Reiniciando...", "WARN")
                        self.restart_app(pkg)
                        continue
                    
                    try:
                        top = self.run_adb(f"shell top -n 1 -b | grep {pid}")
                        cpu = float(top.split()[8].replace('%', '')) if top else 0
                        
                        if cpu < self.config["low_cpu_threshold"]:
                            self.lowcpu_count[pkg] = self.lowcpu_count.get(pkg, 0) + 1
                            HackerUI.print_log_entry("CPU", f"{pkg}: {cpu}% (Baixo) [{self.lowcpu_count[pkg]}/{self.config['max_lowcpu_time']}]", "WARN")
                            
                            if self.lowcpu_count[pkg] >= self.config["max_lowcpu_time"]:
                                self.restart_app(pkg)
                        else:
                            self.lowcpu_count[pkg] = 0
                            # HackerUI.print_log_entry("STATUS", f"{pkg}: {cpu}% OK", "SUCCESS") # Spam reduction
                    except: pass

                time.sleep(self.config["check_interval"])

            except KeyboardInterrupt:
                self.running = False
            except Exception as e:
                HackerUI.print_log_entry("CRITICAL", f"Erro: {e}", "ERROR")

# ============================================
# 🔧 SISTEMA
# ============================================
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return {**DEFAULT_CONFIG, **json.load(f)}
    return DEFAULT_CONFIG

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

def detect_packages():
    HackerUI.print_log_entry("SCAN", "Procurando Roblox...", "INFO")
    res = subprocess.run(["adb", "shell", "pm", "list", "packages"], capture_output=True, text=True)
    pkgs = [line.split(":")[1].strip() for line in res.stdout.splitlines() if "roblox" in line.lower()]
    return pkgs

def main():
    while True:
        HackerUI.clear_screen()
        HackerUI.print_matrix_banner()
        print(f"{HackerTheme.GREEN_DARK}┌──[ MENU ]────────────────────────────────────────┐")
        print(f"│ 1. {HackerTheme.CYAN}INICIAR (Delta Bypass Mode){HackerTheme.GREEN_DARK}                   │")
        print(f"│ 2. {HackerTheme.YELLOW}DETECTAR ROBLOX{HackerTheme.GREEN_DARK}                               │")
        print(f"│ 3. {HackerTheme.PINK}LINK VIP{HackerTheme.GREEN_DARK}                                      │")
        print(f"│ 4. {HackerTheme.RED}SAIR{HackerTheme.GREEN_DARK}                                          │")
        print(f"└──────────────────────────────────────────────────┘{HackerTheme.RESET}")
        
        opt = input(f"\n{HackerTheme.BOLD}root@termux:~$ {HackerTheme.RESET}")
        
        config = load_config()
        
        if opt == "1":
            mon = HackerMonitor(config)
            mon.start()
        elif opt == "2":
            pkgs = detect_packages()
            if pkgs:
                config["packages"] = pkgs
                save_config(config)
                print(f"\nSalvo: {pkgs}")
            else:
                print("\nRoblox não encontrado!")
            time.sleep(2)
        elif opt == "3":
            config["web_link"] = input("Link VIP: ").strip()
            save_config(config)
        elif opt == "4":
            sys.exit()

if __name__ == "__main__":
    main()
