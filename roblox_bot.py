#!/usr/bin/env python3
"""
🖥️ Roblox AutoRejoin - V10.0 (NUCLEAR MODE) 🖥️
Correções:
  1. Mata o navegador sem perguntar (Garante o fechamento)
  2. Mostra o conteúdo exato do Clipboard (Debug)
  3. Filtro de link mais permissivo
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
COORD_TRIGGER = "801 351"   # Botão Get Key (Onde clica 3x)
COORD_INPUT   = "779 228"   # Onde cola a key

# ============================================
# ⚙️ CONFIGURAÇÃO
# ============================================
CONFIG_FILE = "hacker_config.json"
KEY_API_URL = "http://127.0.0.1:3000/get_key"

DEFAULT_CONFIG = {
    "web_link": "https://www.roblox.com/games/1537690962/Bee-Swarm-Simulator?privateServerLinkCode=54979473479340063836604255875447",
    "webhook_url": "https://discord.com/api/webhooks/1069275367581438022/kBC-roJY3Mb70Va14XOw33CH5CxvVW8dUDw0UTYPLPMFlMoF7W1rN2FD45Hq4VBjfO4M", 
    "startup_delay": 25,
    "check_interval": 5,
    "packages": [],
    "browser_package": "com.android.chrome" # Confirme se é esse seu navegador
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
        print("║   ROBLOX AUTO-SYSTEM V10.0 (NUCLEAR)       ║")
        print("║   [Force Kill Browser] + [Debug Mode]      ║")
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

    def get_clipboard(self):
        try:
            res = subprocess.run(["termux-clipboard-get"], capture_output=True, timeout=2)
            return res.stdout.decode().strip()
        except: return ""

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

    # --- LÓGICA DO BYPASS 4.0 (NUCLEAR) ---
    def execute_bypass_logic(self):
        HackerUI.log("ACTION", f"Iniciando sequência de cliques (3x)...", HackerUI.YELLOW)
        
        # 1. SPAM DE CLIQUES
        for i in range(3):
            self.run_adb(f"input tap {COORD_TRIGGER}")
            time.sleep(0.5) 
        
        # 2. ESPERA O NAVEGADOR ABRIR (Sem checar, só espera)
        HackerUI.log("WAIT", "Aguardando 6s para navegador processar...", HackerUI.CYAN)
        time.sleep(6) 

        # 3. MATA O NAVEGADOR (NUCLEAR KILL)
        HackerUI.log("KILL", f"Forçando fechamento de {self.config['browser_package']}...", HackerUI.RED)
        self.run_adb(f"am force-stop {self.config['browser_package']}")
        time.sleep(1.5) # Tempo para o sistema voltar ao jogo

        # 4. VERIFICA CLIPBOARD COM DEBUG
        link = self.get_clipboard()
        HackerUI.log("DEBUG", f"Conteúdo do Clipboard: '{link}'", HackerUI.WHITE) # MOSTRA O QUE PEGOU
        
        # Valida Link (Filtro Relaxado)
        if link and "http" in link:
            HackerUI.log("LINK", f"Link Capturado! Enviando...", HackerUI.GREEN)
            
            # 5. ENVIA PARA DISCORD
            if self.config["webhook_url"]:
                try:
                    payload = {"content": f"!bypass {link}"}
                    requests.post(self.config["webhook_url"], json=payload)
                    HackerUI.log("DISCORD", "Webhook enviado com sucesso.", HackerUI.PURPLE)
                except Exception as e:
                    HackerUI.log("ERROR", f"Webhook falhou: {e}", HackerUI.RED)
            else:
                HackerUI.log("WARN", "Sem Webhook configurado!", HackerUI.RED)
                return

            # 6. ESPERA RETORNO DA API
            HackerUI.log("WAIT", "Aguardando Key da API (40s)...", HackerUI.CYAN)
            key = None
            
            # Polling por 40 segundos
            for i in range(20):
                try:
                    r = requests.get(KEY_API_URL, timeout=2)
                    # Verifica se não é o próprio link que voltou
                    if len(r.text) > 5 and "http" not in r.text: 
                        key = r.text.strip()
                        break
                except: pass
                time.sleep(2)
            
            # 7. INJETA A KEY
            if key:
                HackerUI.log("KEY", "Key Recebida! Injetando...", HackerUI.GREEN)
                
                self.run_adb(f"input tap {COORD_INPUT}")
                time.sleep(0.5)
                
                safe_key = key.replace(" ", "%s").replace("&", "\&").replace("'", "")
                self.run_adb(f"input text \"{safe_key}\"")
                time.sleep(1.0)
                
                self.run_adb(f"input tap {COORD_TRIGGER}")
                HackerUI.log("SUCCESS", "Bypass Finalizado!", HackerUI.GREEN)
            else:
                HackerUI.log("FAIL", "Timeout: Key não chegou na API.", HackerUI.RED)
        
        else:
            HackerUI.log("INFO", "Nenhum link 'http' encontrado.", HackerUI.CYAN)

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

        HackerUI.log("SYSTEM", "Sistema V10.0 Iniciado.", HackerUI.GREEN)

        while self.running:
            try:
                for pkg in self.config["packages"]:
                    
                    # Checagem de Processo
                    pid_res = subprocess.run(f"adb shell pidof {pkg}", shell=True, capture_output=True)
                    if not pid_res.stdout:
                        self.restart_game(pkg)
                        continue

                    # Startup Check (1x por boot)
                    if not self.checked_startup:
                        delay = self.config['startup_delay']
                        HackerUI.log("WAIT", f"Carregando Jogo ({delay}s)...", HackerUI.CYAN)
                        time.sleep(delay)
                        
                        self.execute_bypass_logic()
                        
                        self.checked_startup = True
                        HackerUI.log("MONITOR", "Vigilância Ativa.", HackerUI.GREEN)
                        continue

                    # Anti-Crash (CPU Monitor)
                    cpu = self.get_cpu_usage(pkg)
                    if cpu < 2.0:
                        self.low_cpu_count += 1
                        if self.low_cpu_count >= 12: # ~1 min travado
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
    menu_opt = input("Pressione ENTER para iniciar v10.0...")
    app = AutoSystem()
    app.start()
