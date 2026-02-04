#!/usr/bin/env python3
"""
🖥️ Roblox AutoRejoin - V11.0 (ANDROID 12+ FIX) 🖥️
Correção Crítica:
  - Traz o Termux para frente rapidinho para ler o clipboard
  - Contorna o bloqueio de privacidade do Android
"""

import os
import sys
import time
import json
import subprocess
import requests
from datetime import datetime

# ============================================
# 📍 COORDENADAS
# ============================================
COORD_TRIGGER = "801 351"   # Botão Get Key / Continue
COORD_INPUT   = "779 228"   # Campo de Texto

# ============================================
# ⚙️ CONFIGURAÇÃO
# ============================================
CONFIG_FILE = "hacker_config.json"
KEY_API_URL = "http://127.0.0.1:3000/get_key"

DEFAULT_CONFIG = {
    "web_link": "",
    "webhook_url": "", 
    "startup_delay": 25,
    "check_interval": 5,
    "packages": [],
    "browser_package": "com.android.chrome"
}

# ============================================
# 🎨 VISUAL
# ============================================
class HackerUI:
    RESET = "\033[0m"
    GREEN = "\033[38;5;46m"
    CYAN = "\033[38;5;51m"
    YELLOW = "\033[38;5;226m"
    RED = "\033[38;5;196m"
    PURPLE = "\033[38;5;93m"
    WHITE = "\033[37m"

    @staticmethod
    def log(tag, msg, color=CYAN):
        time_str = datetime.now().strftime("%H:%M:%S")
        print(f"{HackerUI.GREEN}[{time_str}] {color}[{tag:<8}] {HackerUI.RESET}{msg}")

    @staticmethod
    def banner():
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"{HackerUI.GREEN}")
        print("╔════════════════════════════════════════════╗")
        print("║   ROBLOX AUTO-SYSTEM V11.0 (PRIVACY FIX)   ║")
        print("║   [Auto-Focus Switch] -> [Read Clipboard]  ║")
        print("╚════════════════════════════════════════════╝")
        print(f"{HackerUI.RESET}")

# ============================================
# 🧠 SISTEMA
# ============================================
class AutoSystem:
    def __init__(self):
        self.config = self.load_config()
        self.running = True
        self.checked_startup = False
        self.low_cpu_count = 0

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                return {**DEFAULT_CONFIG, **json.load(f)}
        return DEFAULT_CONFIG

    def save_config(self):
        with open(CONFIG_FILE, 'w') as f:
            json.dump(self.config, f, indent=4)

    def run_adb(self, cmd):
        try:
            subprocess.run(f"adb shell {cmd}", shell=True, timeout=5, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except: pass

    # --- NOVO: Traz o Termux para frente para ler o clipboard ---
    def get_clipboard_secure(self):
        # 1. Traz o Termux para o foco
        # HackerUI.log("FOCUS", "Trocando para Termux para ler clipboard...", HackerUI.YELLOW)
        subprocess.run("adb shell monkey -p com.termux -c android.intent.category.LAUNCHER 1", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(1.5) # Dá tempo do Android liberar a permissão

        # 2. Lê o Clipboard
        content = ""
        try:
            res = subprocess.run(["termux-clipboard-get"], capture_output=True, timeout=2)
            content = res.stdout.decode().strip()
        except: pass

        return content

    # --- Volta para o Roblox ---
    def return_to_game(self, pkg):
        # HackerUI.log("FOCUS", "Voltando para o jogo...", HackerUI.YELLOW)
        subprocess.run(f"adb shell monkey -p {pkg} -c android.intent.category.LAUNCHER 1", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(1.0)

    def get_cpu_usage(self, pkg):
        try:
            cmd = f"adb shell top -n 1 -b | grep {pkg}"
            res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if res.stdout:
                parts = res.stdout.split()
                for p in parts:
                    if "%" in p: return float(p.replace("%", ""))
                return float(parts[8])
        except: pass
        return 0.0

    # --- LÓGICA DO BYPASS 5.0 (SWITCH MODE) ---
    def execute_bypass_logic(self, pkg):
        HackerUI.log("ACTION", f"Clicando no Trigger (3x)...", HackerUI.YELLOW)
        
        # 1. SPAM DE CLIQUES
        for i in range(3):
            self.run_adb(f"input tap {COORD_TRIGGER}")
            time.sleep(0.5) 
        
        # 2. ESPERA NAVEGADOR E MATA
        HackerUI.log("WAIT", "Aguardando navegador (6s)...", HackerUI.CYAN)
        time.sleep(6) 
        
        HackerUI.log("KILL", "Fechando navegador...", HackerUI.RED)
        self.run_adb(f"am force-stop {self.config['browser_package']}")
        time.sleep(1)

        # 3. LEITURA SEGURA (PULO DO GATO)
        HackerUI.log("READ", "Lendo Clipboard (Trocando app)...", HackerUI.PURPLE)
        link = self.get_clipboard_secure() # Vai pro Termux e volta
        
        # Se precisar voltar pro jogo manualmente (caso o get_clipboard_secure não tenha voltado)
        # Mas vamos voltar agora para garantir que a tela esteja pronta para injetar
        self.return_to_game(pkg) 

        HackerUI.log("DEBUG", f"Conteúdo lido: '{link}'", HackerUI.WHITE)
        
        # Valida Link
        if link and "http" in link:
            HackerUI.log("LINK", f"Link Capturado! Processando...", HackerUI.GREEN)
            
            # 4. ENVIA PARA DISCORD
            if self.config["webhook_url"]:
                try:
                    payload = {"content": f"!bypass {link}"}
                    requests.post(self.config["webhook_url"], json=payload)
                    HackerUI.log("DISCORD", "Enviado para Webhook.", HackerUI.PURPLE)
                except:
                    HackerUI.log("ERROR", "Webhook falhou.", HackerUI.RED)
            
            # 5. ESPERA KEY
            HackerUI.log("WAIT", "Aguardando Key da API (40s)...", HackerUI.CYAN)
            key = None
            
            for i in range(20):
                try:
                    r = requests.get(KEY_API_URL, timeout=2)
                    if len(r.text) > 5 and "http" not in r.text: 
                        key = r.text.strip()
                        break
                except: pass
                time.sleep(2)
            
            # 6. INJETA A KEY
            if key:
                HackerUI.log("KEY", "Injetando Key...", HackerUI.GREEN)
                
                # Garante que o jogo está em foco de novo
                self.return_to_game(pkg)
                
                self.run_adb(f"input tap {COORD_INPUT}")
                time.sleep(0.5)
                
                safe_key = key.replace(" ", "%s").replace("&", "\&").replace("'", "")
                self.run_adb(f"input text \"{safe_key}\"")
                time.sleep(1.0)
                
                self.run_adb(f"input tap {COORD_TRIGGER}")
                HackerUI.log("SUCCESS", "Bypass Finalizado!", HackerUI.GREEN)
            else:
                HackerUI.log("FAIL", "Key não retornada.", HackerUI.RED)
        else:
            HackerUI.log("INFO", "Nenhum link detectado após leitura.", HackerUI.CYAN)

    def restart_game(self, pkg):
        HackerUI.log("RESTART", f"Reiniciando {pkg}...", HackerUI.RED)
        self.run_adb(f"am force-stop {pkg}")
        time.sleep(2)
        link = self.config['web_link']
        self.run_adb(f"am start -a android.intent.action.VIEW -d \"{link}\" {pkg}")
        self.checked_startup = False 
        self.low_cpu_count = 0

    def start(self):
        HackerUI.banner()
        
        if not self.config["packages"]:
            HackerUI.log("SETUP", "Detectando Roblox...", HackerUI.YELLOW)
            res = subprocess.run("adb shell pm list packages", shell=True, capture_output=True, text=True)
            pkgs = [l.split(":")[1].strip() for l in res.stdout.splitlines() if "roblox" in l.lower()]
            if pkgs:
                self.config["packages"] = pkgs
                self.save_config()
                HackerUI.log("SETUP", f"Alvo: {pkgs[0]}", HackerUI.GREEN)
            else:
                HackerUI.log("ERROR", "Roblox não encontrado!", HackerUI.RED)
                return

        HackerUI.log("SYSTEM", "Sistema V11.0 Iniciado.", HackerUI.GREEN)

        while self.running:
            try:
                for pkg in self.config["packages"]:
                    
                    # Checagem de Processo
                    pid_res = subprocess.run(f"adb shell pidof {pkg}", shell=True, capture_output=True)
                    if not pid_res.stdout:
                        self.restart_game(pkg)
                        continue

                    # Startup Check
                    if not self.checked_startup:
                        delay = self.config['startup_delay']
                        HackerUI.log("WAIT", f"Carregando Jogo ({delay}s)...", HackerUI.CYAN)
                        time.sleep(delay)
                        
                        # Passamos o pkg para poder voltar ao jogo depois de ler o clipboard
                        self.execute_bypass_logic(pkg)
                        
                        self.checked_startup = True
                        HackerUI.log("MONITOR", "Vigilância Ativa.", HackerUI.GREEN)
                        continue

                    # Anti-Crash
                    cpu = self.get_cpu_usage(pkg)
                    if cpu < 2.0:
                        self.low_cpu_count += 1
                        if self.low_cpu_count >= 12: 
                            HackerUI.log("FREEZE", "Jogo Congelado.", HackerUI.RED)
                            self.restart_game(pkg)
                    else:
                        self.low_cpu_count = 0

                time.sleep(self.config["check_interval"])

            except KeyboardInterrupt:
                self.running = False
                print("\nSaindo...")
            except Exception as e:
                HackerUI.log("ERROR", str(e), HackerUI.RED)
                time.sleep(5)

if __name__ == "__main__":
    app = AutoSystem()
    app.start()
