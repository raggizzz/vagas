#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste visual do scraper - versão sem headless para visualizar o funcionamento
"""

import sys
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import subprocess
import random

def cleanup_chrome_processes():
    """Limpa processos órfãos do Chrome e chromedriver"""
    try:
        subprocess.run(['taskkill', '/f', '/im', 'chrome.exe'], 
                      capture_output=True, text=True, check=False)
        subprocess.run(['taskkill', '/f', '/im', 'chromedriver.exe'], 
                      capture_output=True, text=True, check=False)
        time.sleep(2)
    except Exception as e:
        print(f"Erro ao limpar processos: {e}")

def setup_visual_driver():
    """Configura driver Chrome VISUAL (sem headless) para teste"""
    cleanup_chrome_processes()
    
    options = Options()
    
    # Configurações anti-detecção
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    # User agent
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    # Configurações de performance e segurança
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-web-security')
    options.add_argument('--disable-features=VizDisplayCompositor')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-plugins')
    
    # Configurações de janela
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--start-maximized')
    
    # Porta de depuração aleatória
    debug_port = random.randint(9000, 9999)
    options.add_argument(f'--remote-debugging-port={debug_port}')
    
    # NÃO adicionar --headless para ver o navegador
    print("🌐 Iniciando Chrome em modo VISUAL (você verá o navegador)...")
    
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        # Configurações de timeout
        driver.set_page_load_timeout(30)
        driver.implicitly_wait(10)
        
        # Remove propriedade webdriver para evitar detecção
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        print("✅ Driver Chrome configurado com sucesso!")
        return driver
        
    except Exception as e:
        print(f"❌ Erro ao configurar driver: {e}")
        cleanup_chrome_processes()
        raise

def test_visual_scraping():
    """Testa o scraping de forma visual"""
    driver = None
    
    try:
        print("🚀 Iniciando teste visual do scraper...")
        driver = setup_visual_driver()
        
        # Teste 1: Google
        print("\n📍 Teste 1: Acessando Google...")
        driver.get('https://www.google.com')
        time.sleep(3)
        print(f"✅ Google carregado: {driver.title}")
        
        # Teste 2: Catho página principal
        print("\n📍 Teste 2: Acessando Catho...")
        driver.get('https://www.catho.com.br')
        time.sleep(5)
        print(f"✅ Catho carregado: {driver.title}")
        
        # Teste 3: Página de vagas específica
        print("\n📍 Teste 3: Acessando página de vagas Industrial...")
        catho_url = 'https://www.catho.com.br/vagas/industrial/'
        driver.get(catho_url)
        time.sleep(5)
        print(f"✅ Página de vagas carregada: {driver.title}")
        
        # Teste 4: Procurar por elementos de vagas
        print("\n📍 Teste 4: Procurando elementos de vagas...")
        try:
            # Aguardar elementos de vagas carregarem
            wait = WebDriverWait(driver, 15)
            
            # Tentar diferentes seletores para vagas
            selectors = [
                "[data-testid='job-card']",
                ".sc-bdvvtL",
                "article",
                ".job-card",
                "[data-cy='job-card']"
            ]
            
            vagas_encontradas = 0
            for selector in selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        vagas_encontradas = len(elements)
                        print(f"✅ Encontradas {vagas_encontradas} vagas com seletor: {selector}")
                        break
                except:
                    continue
            
            if vagas_encontradas == 0:
                print("⚠️ Nenhuma vaga encontrada com os seletores testados")
                print("📄 HTML da página:")
                print(driver.page_source[:1000] + "...")
            
        except Exception as e:
            print(f"❌ Erro ao procurar vagas: {e}")
        
        print("\n⏳ Aguardando 10 segundos para você visualizar...")
        time.sleep(10)
        
        print("\n✅ Teste visual concluído com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro durante teste visual: {e}")
        
    finally:
        if driver:
            print("\n🔄 Fechando navegador...")
            try:
                driver.quit()
            except:
                pass
            cleanup_chrome_processes()

if __name__ == "__main__":
    test_visual_scraping()
"""
Teste visual do scraper com navegador visível
"""

import sys
import os
import time
import random
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def cleanup_chrome_processes():
    """Limpa processos órfãos do Chrome"""
    try:
        subprocess.run(["taskkill", "/f", "/im", "chrome.exe"], 
                      capture_output=True, text=True, check=False)
        subprocess.run(["taskkill", "/f", "/im", "chromedriver.exe"], 
                      capture_output=True, text=True, check=False)
        time.sleep(2)
    except Exception as e:
        print(f"Erro ao limpar processos: {e}")

def setup_visual_driver():
    """Configura driver Chrome VISÍVEL para teste"""
    print("🧹 Limpando processos órfãos do Chrome...")
    cleanup_chrome_processes()
    
    print("⚙️ Configurando Chrome visível...")
    
    chrome_options = Options()
    
    # REMOVEMOS --headless para tornar o navegador VISÍVEL
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # User agent mais realista
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # Tamanho da janela
    chrome_options.add_argument("--window-size=1200,800")
    
    # Porta de debug aleatória
    debug_port = random.randint(9000, 9999)
    chrome_options.add_argument(f"--remote-debugging-port={debug_port}")
    
    try:
        print("📦 Instalando ChromeDriver...")
        service = Service(ChromeDriverManager().install())
        
        print("🚀 Iniciando Chrome visível...")
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Remove propriedade webdriver para evitar detecção
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        # Timeouts
        driver.set_page_load_timeout(30)
        driver.implicitly_wait(10)
        
        print("✅ Chrome iniciado com sucesso!")
        return driver
        
    except Exception as e:
        print(f"❌ Erro ao configurar driver: {e}")
        cleanup_chrome_processes()
        return None

def test_catho_visual():
    """Testa acesso visual ao Catho"""
    driver = None
    
    try:
        driver = setup_visual_driver()
        if not driver:
            return False
            
        print("\n🌐 Testando Google...")
        driver.get("https://www.google.com")
        time.sleep(3)
        print(f"✅ Google carregado: {driver.title}")
        
        print("\n🔍 Testando Catho...")
        driver.get("https://www.catho.com.br")
        time.sleep(5)
        print(f"✅ Catho carregado: {driver.title}")
        
        # Tenta encontrar elementos da página
        try:
            # Procura por links de vagas
            wait = WebDriverWait(driver, 10)
            
            # Diferentes seletores para encontrar vagas
            selectors = [
                "a[href*='/vagas/']",
                "a[href*='/vaga/']",
                ".job-item",
                ".vaga",
                "[data-testid*='job']"
            ]
            
            found_elements = False
            for selector in selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        print(f"✅ Encontrados {len(elements)} elementos com seletor: {selector}")
                        found_elements = True
                        break
                except:
                    continue
            
            if not found_elements:
                print("⚠️ Nenhum elemento de vaga encontrado")
            
        except Exception as e:
            print(f"⚠️ Erro ao procurar elementos: {e}")
        
        print("\n⏱️ Aguardando 10 segundos para você ver o navegador...")
        time.sleep(10)
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False
        
    finally:
        if driver:
            print("\n🔒 Fechando navegador...")
            try:
                driver.quit()
            except:
                pass
            cleanup_chrome_processes()

if __name__ == "__main__":
    print("🧪 TESTE VISUAL DO SCRAPER")
    print("=" * 40)
    print("Este teste abrirá o Chrome VISÍVEL para você ver o que está acontecendo.")
    print("O navegador ficará aberto por 10 segundos após carregar o Catho.")
    print("=" * 40)
    
    success = test_catho_visual()
    
    if success:
        print("\n✅ Teste concluído com sucesso!")
        print("Se você viu o navegador abrir e carregar as páginas, o WebDriver está funcionando.")
    else:
        print("\n❌ Teste falhou!")
        print("Verifique os erros acima para diagnosticar o problema.")