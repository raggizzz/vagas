#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup

def debug_catho_structure():
    print("=== Debug Catho Structure ===")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    # Testa a página que sabemos que funciona
    url = 'https://www.catho.com.br/vagas/?page=2'
    
    try:
        r = requests.get(url, headers=headers, timeout=30)
        print(f"Status: {r.status_code}, Tamanho: {len(r.text)}")
        
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            print(f"Title: {soup.title.get_text() if soup.title else 'Sem título'}")
            
            # Salva HTML para análise
            with open('catho_debug.html', 'w', encoding='utf-8') as f:
                f.write(r.text)
            print("HTML salvo em catho_debug.html")
            
            # Testa diferentes seletores para encontrar vagas
            selectors_to_test = [
                'a[href*="/vaga"]',
                'a[href*="/job"]', 
                'a[href*="/emprego"]',
                'a[href*="catho.com.br"]',
                '.job-card a',
                '.vaga-card a',
                '[data-testid*="job"] a',
                '[data-testid*="vaga"] a',
                'article a',
                '.card a'
            ]
            
            print("\n--- Testando seletores ---")
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
            job_patterns = ['/vaga', '/job', '/emprego', 'oportunidade']
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
                print("Primeiros 5 links potenciais:")
                for i, link in enumerate(potential_job_links[:5]):
                    print(f"  {i+1}: {link['href']} - {link['text']}")
                    print(f"      Classes: {link['classes']}")
            
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    debug_catho_structure()