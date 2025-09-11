import cloudscraper
from bs4 import BeautifulSoup
import time

# Criar scraper que contorna Cloudflare
scraper = cloudscraper.create_scraper(
    browser={
        'browser': 'chrome',
        'platform': 'windows',
        'desktop': True
    }
)

# URLs específicas encontradas nos resultados de busca
urls = [
    'https://www.catho.com.br/empresas/anunciar-vaga/',
    'https://www.catho.com.br/carreira-sucesso/catho-gratis-tempo-ilimitado/',
    'https://www.catho.com.br/carreira-sucesso/',
    'https://www.catho.com.br/empresas/'
]

for url in urls:
    print(f"\nTestando URL específica: {url}")
    try:
        response = scraper.get(url, timeout=30)
        print(f"Status: {response.status_code}")
        print(f"Content-Length: {len(response.content)}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            title = soup.find('title')
            print(f"Title: {title.text if title else 'N/A'}")
            
            # Procurar por links de navegação ou busca
            nav_links = soup.find_all('a', href=True)
            vaga_links = []
            search_links = []
            
            for link in nav_links:
                href = link.get('href', '').lower()
                text = link.get_text(strip=True).lower()
                
                if 'vaga' in href or 'vaga' in text:
                    vaga_links.append(link)
                elif 'busca' in href or 'search' in href or 'pesquisa' in href:
                    search_links.append(link)
            
            print(f"Links relacionados a vagas: {len(vaga_links)}")
            print(f"Links de busca: {len(search_links)}")
            
            if len(vaga_links) > 0:
                print("Links de vagas encontrados:")
                for i, link in enumerate(vaga_links[:3]):
                    href = link.get('href', '')
                    text = link.get_text(strip=True)[:50]
                    print(f"  {i+1}. {href} - {text}")
            
            if len(search_links) > 0:
                print("Links de busca encontrados:")
                for i, link in enumerate(search_links[:3]):
                    href = link.get('href', '')
                    text = link.get_text(strip=True)[:50]
                    print(f"  {i+1}. {href} - {text}")
            
            # Procurar por formulários de busca
            forms = soup.find_all('form')
            print(f"Formulários encontrados: {len(forms)}")
            
            # Salvar HTML para análise
            filename = f"catho_working_{url.split('/')[-2] or 'root'}.html"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(response.text)
            print(f"HTML salvo em {filename}")
            
        elif response.status_code == 404:
            print(f"Erro 404: {response.text[:200]}")
        else:
            print(f"Erro {response.status_code}: {response.text[:200]}")
            
    except Exception as e:
        print(f"Erro na requisição: {e}")
    
    time.sleep(2)

print("\nTeste concluído!")