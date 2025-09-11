#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

def debug_infojobs_structure():
    print("=== Debug InfoJobs Structure ===")
    
    # Primeiro tenta com requests normal
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    url = 'https://www.infojobs.com.br/vagas-de-emprego.aspx'
    
    print("\n--- Testando com requests ---")
    try:
        r = requests.get(url, headers=headers, timeout=30)
        print(f"Status: {r.status_code}, Tamanho: {len(r.text)}")
        
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            print(f"Title: {soup.title.get_text() if soup.title else 'Sem título'}")
            
            # Salva HTML para análise
            with open('infojobs_debug_requests.html', 'w', encoding='utf-8') as f:
                f.write(r.text)
            print("HTML salvo em infojobs_debug_requests.html")
            
    except Exception as e:
        print(f"Erro com requests: {e}")
    
    print("\n--- Testando com Playwright ---")
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent=headers['User-Agent'],
                locale="pt-BR"
            )
            page = context.new_page()
            
            print(f"Acessando: {url}")
            response = page.goto(url, wait_until="domcontentloaded", timeout=30000)
            
            print(f"Status: {response.status if response else 'N/A'}")
            
            # Aguarda carregamento
            page.wait_for_timeout(3000)
            
            # Faz alguns scrolls para carregar conteúdo
            for i in range(3):
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                page.wait_for_timeout(2000)
            
            html = page.content()
            print(f"HTML coletado: {len(html)} caracteres")
            
            # Salva HTML para análise
            with open('infojobs_debug_playwright.html', 'w', encoding='utf-8') as f:
                f.write(html)
            print("HTML salvo em infojobs_debug_playwright.html")
            
            # Testa diferentes seletores para encontrar vagas
            selectors_to_test = [
                'a[href*="/vaga/"]',
                'a[href*="/vagas/"]',
                'a[href*="aspx"]',
                '.job-item a',
                '.vaga-item a',
                '.listado-ofertas a',
                '[data-testid*="job"] a',
                'article a',
                '.card a',
                '.offer a',
                '.vacancy a',
                'a[href*="emprego"]',
                'a[href*="oportunidade"]'
            ]
            
            print("\n--- Testando seletores ---")
            soup = BeautifulSoup(html, 'html.parser')
            for selector in selectors_to_test:
                try:
                    elements = soup.select(selector)
                    if elements:
                        print(f"{selector}: {len(elements)} elementos")
                        # Mostra os primeiros 3 links
                        for i, elem in enumerate(elements[:3]):
                            href = elem.get('href', '')
                            text = elem.get_text().strip()[:50]
                            print(f"  {i+1}: {href} - {text}...")
                except Exception as e:
                    print(f"{selector}: ERRO - {e}")
            
            # Procura por todos os links e filtra manualmente
            print("\n--- Análise de todos os links ---")
            all_links = soup.select('a[href]')
            print(f"Total de links: {len(all_links)}")
            
            # Filtra links que podem ser de vagas
            job_patterns = ['/vaga', '/job', '/emprego', '/oportunidade', 'aspx']
            potential_job_links = []
            
            for a in all_links:
                href = a.get('href', '').lower()
                text = a.get_text().strip().lower()
                
                # Verifica se o link ou texto contém padrões de vaga
                if any(pattern in href for pattern in job_patterns) or any(pattern in text for pattern in ['vaga', 'emprego', 'oportunidade']):
                    potential_job_links.append({
                        'href': a.get('href'),
                        'text': a.get_text().strip()[:100],
                        'classes': a.get('class', [])
                    })
            
            print(f"Links potenciais de vagas: {len(potential_job_links)}")
            if potential_job_links:
                print("Primeiros 10 links potenciais:")
                for i, link in enumerate(potential_job_links[:10]):
                    print(f"  {i+1}: {link['href']} - {link['text']}")
                    print(f"      Classes: {link['classes']}")
            
            context.close()
            browser.close()
            
    except Exception as e:
        print(f"Erro com Playwright: {e}")

if __name__ == "__main__":
    debug_infojobs_structure()