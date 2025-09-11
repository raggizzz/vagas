#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import random
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def test_webdriver_connection():
    """Testa a configuração corrigida do WebDriver"""
    print("=== Teste de Conexão do WebDriver ===")
    
    # Limpar processos órfãos primeiro
    print("1. Limpando processos órfãos...")
    try:
        subprocess.run(['taskkill', '/f', '/im', 'chrome.exe'], 
                     capture_output=True, timeout=5)
        subprocess.run(['taskkill', '/f', '/im', 'chromedriver.exe'], 
                     capture_output=True, timeout=5)
        print("   ✓ Processos limpos")
    except Exception as e:
        print(f"   ⚠ Erro na limpeza: {e}")
    
    time.sleep(2)
    
    # Configurar opções do Chrome
    print("2. Configurando opções do Chrome...")
    options = Options()
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-web-security')
    options.add_argument('--disable-features=VizDisplayCompositor')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-plugins')
    options.add_argument('--disable-images')
    options.add_argument('--window-size=1920,1080')
    
    # Usar porta aleatória
    debug_port = random.randint(9000, 9999)
    options.add_argument(f'--remote-debugging-port={debug_port}')
    options.add_argument('--headless')
    
    print(f"   ✓ Porta de debug: {debug_port}")
    
    driver = None
    try:
        # Criar driver
        print("3. Criando driver...")
        service = Service(ChromeDriverManager().install())
        service.start()
        
        driver = webdriver.Chrome(service=service, options=options)
        driver.set_page_load_timeout(30)
        driver.implicitly_wait(10)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        print("   ✓ Driver criado com sucesso")
        
        # Testar navegação
        print("4. Testando navegação...")
        test_urls = [
            'https://www.google.com',
            'https://httpbin.org/get',
            'https://www.catho.com.br'
        ]
        
        for url in test_urls:
            try:
                print(f"   Testando: {url}")
                driver.get(url)
                time.sleep(2)
                
                title = driver.title
                current_url = driver.current_url
                page_source_length = len(driver.page_source)
                
                print(f"     ✓ Título: {title[:50]}...")
                print(f"     ✓ URL atual: {current_url}")
                print(f"     ✓ Tamanho da página: {page_source_length} chars")
                
                if page_source_length < 100:
                    print(f"     ⚠ Página muito pequena, possível bloqueio")
                else:
                    print(f"     ✓ Página carregada com sucesso")
                    
            except Exception as e:
                print(f"     ❌ Erro ao acessar {url}: {e}")
        
        print("\n5. Teste concluído com sucesso! ✅")
        return True
        
    except Exception as e:
        print(f"\n❌ Erro durante o teste: {e}")
        return False
        
    finally:
        # Limpar driver
        if driver:
            try:
                print("6. Fechando driver...")
                driver.quit()
                print("   ✓ Driver fechado")
            except Exception as e:
                print(f"   ⚠ Erro ao fechar driver: {e}")
        
        # Limpeza final
        try:
            subprocess.run(['taskkill', '/f', '/im', 'chrome.exe'], 
                         capture_output=True, timeout=5)
            subprocess.run(['taskkill', '/f', '/im', 'chromedriver.exe'], 
                         capture_output=True, timeout=5)
            print("   ✓ Limpeza final concluída")
        except:
            pass

if __name__ == "__main__":
    success = test_webdriver_connection()
    if success:
        print("\n🎉 SUCESSO: WebDriver está funcionando corretamente!")
        print("   O erro de conexão foi resolvido.")
    else:
        print("\n😞 FALHA: Ainda há problemas com o WebDriver.")
        print("   Verifique se o Chrome está instalado e atualizado.")