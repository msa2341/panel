#!/usr/bin/env python3
"""
🖥️ Roblox AutoRejoin - Hacker Theme Ultimate 🖥️
Interface cyberpunk com Lógica Linear (Blind Mode)
Versão: 6.0 - Direct Coordinate Injection
"""

import os
import sys
import time
import json
import subprocess
import requests
from datetime import datetime
from typing import Dict, List, Optional

# ============================================
# 🎮 CONFIGURAÇÃO E CONSTANTES
# ============================================
CONFIG_FILE = "hacker_config.json"
KEY_API_URL = "http://127.0.0.1:3000/get_key" 

# --- COORDENADAS FIXAS (Baseado nas suas prints) ---
COORD_INPUT_BOX = "779 228"   # Onde clica para gerar o link / focar
COORD_CONFIRM_BTN = "801 351" # Botão "Continue" / "Checkpoint"

DEFAULT_CONFIG = {
    "web_link": "https://www.roblox.com/games/1537690962/Bee-Swarm-Simulator?privateServerLinkCode=54979473479340063836604255875447",
    "webhook_url": "https://discord.com/api/webhooks/1069275367581438022/kBC-roJY3Mb70Va14XOw33CH5CxvVW8dUDw0UTYPLPMFlMoF7W1rN2FD45Hq4VBjfO4M", # Opcional
    "check_interval": 5,
    "packages": [],
    "startup_delay": 20 # Tempo para esperar o jogo carregar antes de clicar
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
# 🎨 INTERFACE VISUAL
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
        print(f"║  {HackerTheme.PINK}v6.0 • BLIND MODE • AUTO DELTA BYPASS               {HackerTheme.MATRIX}║")
        print("╚══════════════════════════════════════════════════════════════╝")
        print(f"{HackerTheme.RESET}")

    @staticmethod
    def print_log_entry(tag: str, message: str, level: str = "INFO"):
        colors = {
            "INFO": HackerTheme.CYAN, "WARN": HackerTheme.YELLOW,
            "ERROR": HackerTheme.RED, "SUCCESS": HackerTheme.GREEN_NEON,
            "KEY": HackerTheme.PINK, "ACTION": HackerTheme.PURPLE
        }
        timestamp = datetime.now().strftime("%H:%M:%S")
        color = colors.get(level, HackerTheme.CYAN)
        print(f"{HackerTheme.GREEN_DARK}[{timestamp}] "
              f"[{color}{tag:<8}{HackerTheme.GREEN_DARK}] "
              f"{HackerTheme.RESET}{message}")

# ============================================
# 🧠 LÓGICA DO MONITOR (LINEAR)
# ============================================
class HackerMonitor:
    def __init__(self, config: dict):
        self.config = config
        self.running = True
        self.checked_startup = False # Controle para executar o bypass apenas uma vez por reinício

    def run_adb(self, cmd: str):
        try:
            args = ["adb"] + cmd.split()
            res = subprocess.run(args, capture_output=True, timeout=10)
            return res.stdout.decode().strip()
        except:
            return ""

    # --- LÓGICA PRINCIPAL DO BYPASS ---
    def execute_blind_bypass(self):
        HackerUI.print_log_entry("BYPASS", f"Iniciando verificação cega em {self.config['startup_delay']}s...", "WARN")
        
        # 1. Clicar para tentar gerar o link ou focar
        HackerUI.print_log_entry("ACTION", f"Clicando no Trigger: {COORD_INPUT_BOX}", "INFO")
        self.run_adb(f'shell input tap {COORD_INPUT_BOX}')
        time.sleep(1.5) # Tempo para o Delta reagir e copiar o link

        # 2. Verificar Clipboard
        link = ""
        try:
            res = subprocess.run(["termux-clipboard-get"], capture_output=True, timeout=3)
            link = res.stdout.decode().strip()
        except: pass

        # 3. Decisão
        if link and ("http" in link) and ("gateway" in link or "delta" in link.lower()):
            HackerUI.print_log_entry("KEY", f"🔗 LINK DETECTADO! Iniciando injeção...", "SUCCESS")
            
            # Notifica Discord (Opcional)
            if self.config["webhook_url"]:
                try: requests.post(self.config["webhook_url"], json={"content": f"Bypass Started: {link}"})
                except: pass

            # --- BUSCA A KEY ---
            key = None
            HackerUI.print_log_entry("API", "Buscando Key no servidor local...", "INFO")
            try:
                # Se sua API precisa do link via POST, descomente a linha abaixo:
                # r = requests.post(KEY_API_URL, json={"url": link}, timeout=10)
                # Se for só GET no endpoint local:
                r = requests.get(KEY_API_URL, timeout=10)
                key = r.text.strip()
            except Exception as e:
                HackerUI.print_log_entry("API", f"Erro na API: {e}", "ERROR")

            # --- INJETA A KEY ---
            if key and len(key) > 5:
                HackerUI.print_log_entry("KEY", "🔑 Key Válida! Digitando...", "SUCCESS")
                
                # Garante foco novamente
                self.run_adb(f'shell input tap {COORD_INPUT_BOX}')
                time.sleep(0.5)
                
                # Digita a key (limpa caracteres estranhos)
                safe_key = key.replace(" ", "%s").replace("&", "\&").replace("'", "")
                self.run_adb(f'shell input text "{safe_key}"')
                time.sleep(1.0)
                
                # Clica em continuar
                HackerUI.print_log_entry("ACTION", f"Confirmando em {COORD_CONFIRM_BTN}...", "SUCCESS")
                self.run_adb(f'shell input tap {COORD_CONFIRM_BTN}')
                
                HackerUI.print_log_entry("DONE", "🔓 Processo de Bypass Finalizado.", "SUCCESS")
                return True
            else:
                HackerUI.print_log_entry("FAIL", "Key não retornada pela API.", "ERROR")
                return False

        else:
            HackerUI.print_log_entry("SYSTEM", "Nenhum link de key detectado. Assumindo jogo normal.", "INFO")
            # Limpa clipboard para não confundir na próxima
            try: subprocess.run(["termux-clipboard-set", ""], timeout=1)
            except: pass
            return True

    # --- REINICIALIZAÇÃO ---
    def restart_app(self, package):
        HackerUI.print_log_entry("RESTART", f"Reiniciando {package}...", "WARN")
        self.run_adb(f"shell am force-stop {package}")
        time.sleep(2)
        
        # Link VIP ou apenas abrir o app
        link_vip = self.config['web_link']
        if "roblox.com" in link_vip:
            cmd = f"shell am start -a android.intent.action.VIEW -d \"{link_vip}\" {package}"
        else:
            cmd = f"shell monkey -p {package} -c android.intent.category.LAUNCHER 1"
            
        self.run_adb(cmd)
        
        # Reseta a flag para fazer a verificação na próxima inicialização
        self.checked_startup = False 

    # --- LOOP PRINCIPAL ---
    def start(self):
        HackerUI.print_matrix_banner()
        if not self.config["packages"]:
            HackerUI.print_log_entry("ERROR", "Nenhum pacote configurado!", "ERROR")
            return

        HackerUI.print_log_entry("SYSTEM", "Monitoramento Linear Iniciado.", "INFO")
        
        while self.running:
            try:
                for pkg in self.config["packages"]:
                    
                    # 1. Verifica se o APP está rodando
                    pid = self.run_adb(f"shell pidof {pkg}")
                    
                    if not pid:
                        HackerUI.print_log_entry("PROC", f"{pkg} não está rodando.", "WARN")
                        self.restart_app(pkg)
                        continue

                    # 2. LÓGICA DE STARTUP (Roda 1x quando abre)
                    if not self.checked_startup:
                        HackerUI.print_log_entry("WAIT", f"Aguardando carregamento ({self.config['startup_delay']}s)...", "INFO")
                        
                        # Espera o tempo configurado (ex: 20s) para o jogo abrir e o Delta aparecer
                        time.sleep(self.config['startup_delay'])
                        
                        # Tenta o Bypass
                        self.execute_blind_bypass()
                        
                        # Marca como checado para parar de clicar
                        self.checked_startup = True
                        HackerUI.print_log_entry("MONITOR", "Modo de vigilância ativado (Anti-Crash).", "INFO")
                        continue

                    # 3. MONITORAMENTO DE CRASH (Opcional - verifica se travou total)
                    # Se quiser simplificar, pode deixar apenas o loop verificar se o PID existe.
                    # Mas vamos adicionar uma checagem leve.
                    try:
                        # Se o processo sumir, o loop `if not pid` ali em cima pega.
                        # Aqui só dormimos para não spammar CPU.
                        pass 
                    except: pass

                time.sleep(5) # Checa status a cada 5 segundos

            except KeyboardInterrupt:
                self.running = False
                print(f"\n{HackerTheme.RED}Encerrando...{HackerTheme.RESET}")
            except Exception as e:
                HackerUI.print_log_entry("CRITICAL", f"Erro: {e}", "ERROR")
                time.sleep(5)

# ============================================
# 🔧 MENU E SISTEMA
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
        print(f"{HackerTheme.GREEN_DARK}┌──[ MENU PRINCIPAL ]──────────────────────────────┐")
        print(f"│ 1. {HackerTheme.CYAN}INICIAR MONITOR (Modo Cego){HackerTheme.GREEN_DARK}                   │")
        print(f"│ 2. {HackerTheme.YELLOW}DETECTAR ROBLOX (Auto-Setup){HackerTheme.GREEN_DARK}                  │")
        print(f"│ 3. {HackerTheme.PINK}CONFIGURAR LINK VIP{HackerTheme.GREEN_DARK}                           │")
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
                print(f"\n{HackerTheme.GREEN_NEON}Detectados: {pkgs}{HackerTheme.RESET}")
            else:
                print(f"\n{HackerTheme.RED}Nenhum Roblox encontrado!{HackerTheme.RESET}")
            time.sleep(2)
        elif opt == "3":
            link = input("Cole seu Link VIP: ")
            config["web_link"] = link.strip()
            save_config(config)
            print("Salvo!")
            time.sleep(1)
        elif opt == "4":
            sys.exit()

if __name__ == "__main__":
    main()
