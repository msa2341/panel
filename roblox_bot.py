#!/usr/bin/env python3
"""
🖥️ Roblox AutoRejoin - V8.0 (FULL FEATURE) 🖥️
Funcionalidades:
  1. Monitoramento de Crash e Freeze (CPU)
  2. Clique nas Coordenadas Exatas (801 351)
  3. Envio de Webhook (!bypass link)
  4. Injeção Automática da Key
"""

import os
import sys
import time
import json
import subprocess
import requests
from datetime import datetime

# ============================================
# 📍 COORDENADAS (Ajustadas)
# ============================================
COORD_TRIGGER = "801 351"   # Botão Get Key / Continue
COORD_INPUT   = "779 228"   # Campo de Texto

# ============================================
# ⚙️ CONFIGURAÇÃO
# ============================================
CONFIG_FILE = "hacker_config.json"
KEY_API_URL = "http://127.0.0.1:3000/get_key" # Onde a key vai aparecer depois que o bot do discord fizer o bypass

DEFAULT_CONFIG = {
    # Seu Link VIP
    "web_link": "https://www.roblox.com/games/1537690962/Bee-Swarm-Simulator?privateServerLinkCode=54979473479340063836604255875447",
    # Seu Webhook do Discord
    "webhook_url": "https://discord.com/api/webhooks/SEU_WEBHOOK_AQUI", 
    "startup_delay": 25, # Tempo pro jogo abrir e carregar o Delta
    "check_interval": 5,
    "packages": []
}

# ============================================
# 🎨 VISUAL & LOGS
# ============================================
class HackerUI:
    RESET = "\033[0m"
    GREEN = "\033[38;5;46m"
    CYAN = "\033[38;5;51m"
    YELLOW = "\033[38;5;226m"
    RED = "\033[38;5;196m"
    PURPLE = "\033[38;5;93m"

    @staticmethod
    def log(tag, msg, color=CYAN):
        time_str = datetime.now().strftime("%H:%M:%S")
        print(f"{HackerUI.GREEN}[{time_str}] {color}[{tag:<8}] {HackerUI.RESET}{msg}")

    @staticmethod
    def banner():
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"{HackerUI.GREEN}")
        print("╔════════════════════════════════════════════╗")
        print("║   ROBLOX AUTO-SYSTEM V8.0 (FULL STACK)     ║")
        print("║   [Monitor] + [Webhook] + [Auto-Click]     ║")
        print("╚════════════════════════════════════════════╝")
        print(f"{HackerUI.RESET}")

# ============================================
# 🧠 SISTEMA PRINCIPAL
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

    # --- COMANDOS ADB ---
    def run_adb(self, cmd):
        try:
            # Roda comando silencioso
            subprocess.run(f"adb shell {cmd}", shell=True, timeout=5, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except: pass

    def get_clipboard(self):
        try:
            res = subprocess.run(["termux-clipboard-get"], capture_output=True, timeout=2)
            return res.stdout.decode().strip()
        except: return ""

    def get_cpu_usage(self, pkg):
        try:
            # Pega uso de CPU do processo
            cmd = f"adb shell top -n 1 -b | grep {pkg}"
            res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if res.stdout:
                # O formato do top pode variar, geralmente é a coluna 9 (index 8)
                parts = res.stdout.split()
                for p in parts:
                    if "%" in p:
                        return float(p.replace("%", ""))
                return float(parts[8]) # Tentativa padrão
        except: pass
        return 0.0

    # --- LÓGICA DO BYPASS (WEBHOOK -> API -> INJECT) ---
    def execute_bypass_logic(self):
        HackerUI.log("BYPASS", f"Clicando no Trigger ({COORD_TRIGGER})...", HackerUI.YELLOW)
        
        # 1. Clica para gerar link
        self.run_adb(f"input tap {COORD_TRIGGER}")
        time.sleep(2)

        # 2. Pega Link da Clipboard
        link = self.get_clipboard()
        
        # Valida se é um link do Delta/Gateway
        if link and "http" in link and ("gateway" in link or "delta" in link.lower()):
            HackerUI.log("LINK", "Link Delta detectado!", HackerUI.GREEN)
            
            # 3. MANDA PRO DISCORD (!bypass url)
            if self.config["webhook_url"]:
                HackerUI.log("DISCORD", f"Enviando '!bypass' para webhook...", HackerUI.PURPLE)
                try:
                    payload = {"content": f"!bypass {link}"}
                    requests.post(self.config["webhook_url"], json=payload)
                except Exception as e:
                    HackerUI.log("ERROR", f"Falha no Webhook: {e}", HackerUI.RED)
            else:
                HackerUI.log("WARN", "Webhook não configurado! Configure na opção 3.", HackerUI.RED)
                return

            # 4. AGUARDA A KEY (Polling na API Local)
            HackerUI.log("WAIT", "Aguardando bot externo retornar a key na API...", HackerUI.CYAN)
            key = None
            
            # Tenta buscar a key por 30 segundos
            for i in range(15):
                try:
                    r = requests.get(KEY_API_URL, timeout=2)
                    if len(r.text) > 5:
                        key = r.text.strip()
                        break
                except: pass
                time.sleep(2)
            
            # 5. INJETA A KEY
            if key:
                HackerUI.log("KEY", "Key recebida! Injetando...", HackerUI.GREEN)
                
                # Clica no input
                self.run_adb(f"input tap {COORD_INPUT}")
                time.sleep(0.5)
                
                # Digita a key (limpa caracteres especiais para não bugar o adb)
                safe_key = key.replace(" ", "%s").replace("&", "\&").replace("'", "")
                self.run_adb(f"input text \"{safe_key}\"")
                time.sleep(1.0)
                
                # Confirma
                self.run_adb(f"input tap {COORD_TRIGGER}")
                HackerUI.log("SUCCESS", "Bypass finalizado com sucesso!", HackerUI.GREEN)
            else:
                HackerUI.log("FAIL", "Tempo esgotado. Key não apareceu na API.", HackerUI.RED)
        
        else:
            # Se não tem link, assume que o jogo já está logado ou não carregou
            HackerUI.log("INFO", "Nenhum link de key na clipboard. Jogo normal.", HackerUI.CYAN)

    # --- RESTART DO JOGO ---
    def restart_game(self, pkg):
        HackerUI.log("RESTART", f"Reiniciando {pkg}...", HackerUI.RED)
        self.run_adb(f"am force-stop {pkg}")
        time.sleep(2)
        
        link = self.config['web_link']
        # Abre direto no Link VIP
        self.run_adb(f"am start -a android.intent.action.VIEW -d \"{link}\" {pkg}")
        
        self.checked_startup = False # Reseta para fazer o bypass de novo
        self.low_cpu_count = 0

    # --- LOOP PRINCIPAL ---
    def start(self):
        HackerUI.banner()
        
        # Auto-detectar pacote
        if not self.config["packages"]:
            HackerUI.log("SETUP", "Detectando Roblox...", HackerUI.YELLOW)
            res = subprocess.run("adb shell pm list packages", shell=True, capture_output=True, text=True)
            pkgs = [l.split(":")[1].strip() for l in res.stdout.splitlines() if "roblox" in l.lower()]
            if pkgs:
                self.config["packages"] = pkgs
                self.save_config()
                HackerUI.log("SETUP", f"Alvo definido: {pkgs[0]}", HackerUI.GREEN)
            else:
                HackerUI.log("ERROR", "Roblox não instalado/encontrado!", HackerUI.RED)
                return

        HackerUI.log("SYSTEM", "Monitoramento + Webhook Ativo.", HackerUI.GREEN)

        while self.running:
            try:
                for pkg in self.config["packages"]:
                    
                    # 1. CHECAGEM DE PROCESSO (Se fechou, reabre)
                    pid_res = subprocess.run(f"adb shell pidof {pkg}", shell=True, capture_output=True)
                    if not pid_res.stdout:
                        self.restart_game(pkg)
                        continue

                    # 2. LOGICA DE STARTUP (Roda 1x ao abrir)
                    if not self.checked_startup:
                        delay = self.config['startup_delay']
                        HackerUI.log("WAIT", f"Aguardando carregamento ({delay}s)...", HackerUI.CYAN)
                        time.sleep(delay)
                        
                        # Tenta o Bypass (Clique -> Webhook -> Key -> Cola)
                        self.execute_bypass_logic()
                        
                        self.checked_startup = True
                        HackerUI.log("MONITOR", "Entrando em modo de vigilância.", HackerUI.GREEN)
                        continue

                    # 3. MONITORAMENTO DE CPU (Anti-Freeze)
                    cpu = self.get_cpu_usage(pkg)
                    
                    # Se CPU < 2.0% por muito tempo, o jogo provavelmente travou ou caiu a conexão
                    if cpu < 2.0:
                        self.low_cpu_count += 1
                        HackerUI.log("CPU", f"Uso baixo ({cpu}%). Contagem: {self.low_cpu_count}/10", HackerUI.YELLOW)
                        
                        if self.low_cpu_count >= 10: # 10 checks * 5 segs = 50 segundos travado
                            HackerUI.log("FREEZE", "Jogo detectado como congelado.", HackerUI.RED)
                            self.restart_game(pkg)
                    else:
                        self.low_cpu_count = 0
                        # Opcional: Mostrar status
                        # HackerUI.log("STATUS", f"Jogo rodando. CPU: {cpu}%", HackerUI.CYAN)

                time.sleep(self.config["check_interval"])

            except KeyboardInterrupt:
                self.running = False
                print("\nEncerrando...")
            except Exception as e:
                HackerUI.log("ERROR", str(e), HackerUI.RED)
                time.sleep(5)

# ============================================
# 🔧 MENU DE CONFIGURAÇÃO
# ============================================
def menu():
    app = AutoSystem()
    while True:
        HackerUI.banner()
        print(f"{HackerUI.GREEN}[1] INICIAR MONITOR COMPLETO")
        print(f"{HackerUI.YELLOW}[2] CONFIGURAR LINK VIP")
        print(f"{HackerUI.PURPLE}[3] CONFIGURAR WEBHOOK DISCORD")
        print(f"{HackerUI.RED}[4] SAIR{HackerUI.RESET}")
        
        opt = input("\nroot@termux:~$ ")
        
        if opt == "1":
            app.start()
        elif opt == "2":
            link = input("Cole o Link VIP: ").strip()
            if link:
                app.config["web_link"] = link
                app.save_config()
        elif opt == "3":
            url = input("Cole o Webhook URL: ").strip()
            if url.startswith("http"):
                app.config["webhook_url"] = url
                app.save_config()
        elif opt == "4":
            sys.exit()

if __name__ == "__main__":
    menu()
