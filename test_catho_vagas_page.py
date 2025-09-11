#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

def test_catho_vagas_page():
    print("Testando página específica de vagas do Catho...")
    
    # Configurar Chrome
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    try:
        # Navegar para página de vagas de desenvolvedor
        url = "https://www.catho.com.br/vagas/desenvolvedor/"
        print(f"\nAcessando: {url}")
        driver.get(url)
        
        # Aguardar carregamento
        time.sleep(5)
        
        print(f"URL atual: {driver.current_url}")
        print(f"Título: {driver.title}")
        
        # Aguardar elementos carregarem
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
        except:
            print("Timeout aguardando carregamento da página")
        
        # Obter HTML
        html_content = driver.page_source
        print(f"Tamanho do HTML: {len(html_content)}")
        
        # Analisar com BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Procurar por diferentes tipos de links
        print("\n=== ANÁLISE DE LINKS ===")
        
        # Links que contêm 'vaga'
        vaga_links = soup.select('a[href*="vaga"]')
        print(f"Links contendo 'vaga': {len(vaga_links)}")
        
        # Links que contêm 'emprego'
        emprego_links = soup.select('a[href*="emprego"]')
        print(f"Links contendo 'emprego': {len(emprego_links)}")
        
        # Links que contêm 'job'
        job_links = soup.select('a[href*="job"]')
        print(f"Links contendo 'job': {len(job_links)}")
        
        # Todos os links
        all_links = soup.find_all('a', href=True)
        print(f"Total de links na página: {len(all_links)}")
        
        # Analisar estrutura de cards/containers
        print("\n=== ANÁLISE DE ESTRUTURA ===")
        
        # Procurar por elementos com classes relacionadas a vagas
        job_cards = soup.find_all(attrs={'class': lambda x: x and any(word in str(x).lower() for word in ['job', 'vaga', 'card', 'item', 'listing'])})
        print(f"Elementos com classes relacionadas a vagas: {len(job_cards)}")
        
        # Procurar por data-testid
        test_elements = soup.find_all(attrs={'data-testid': True})
        print(f"Elementos com data-testid: {len(test_elements)}")
        
        # Mostrar alguns exemplos de links encontrados
        print("\n=== EXEMPLOS DE LINKS ===")
        unique_hrefs = set()
        for link in all_links[:50]:  # Primeiros 50 links
            href = link.get('href', '')
            if href and href not in unique_hrefs:
                unique_hrefs.add(href)
                text = link.get_text(strip=True)[:50]
                print(f"  {href} - {text}")
                if len(unique_hrefs) >= 10:
                    break
        
        # Salvar HTML para análise detalhada
        filename = "catho_vagas_desenvolvedor_analysis.html"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"\nHTML salvo em {filename}")
        
        # Procurar por elementos específicos do Catho
        print("\n=== ELEMENTOS ESPECÍFICOS DO CATHO ===")
        
        # Procurar por elementos com IDs ou classes específicas
        specific_selectors = [
            '[data-testid*="job"]',
            '[data-testid*="vaga"]',
            '.job-list',
            '.vacancy-list',
            '.search-results',
            '[class*="JobCard"]',
            '[class*="VagaCard"]',
            '[class*="job-item"]',
            '[class*="vaga-item"]'
        ]
        
        for selector in specific_selectors:
            elements = soup.select(selector)
            if elements:
                print(f"Encontrados {len(elements)} elementos com seletor: {selector}")
        
    except Exception as e:
        print(f"Erro durante o teste: {e}")
    
    finally:
        driver.quit()
        print("\nDriver fechado.")

if __name__ == "__main__":
    test_catho_vagas_page()