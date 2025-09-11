import requests
from bs4 import BeautifulSoup

# Headers completos para burlar proteções
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Cache-Control': 'max-age=0',
    'Referer': 'https://www.google.com/',
    'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': '"Windows"'
}

# Testar diferentes URLs
urls = [
    'https://www.catho.com.br/vagas/desenvolvedor/',
    'https://www.catho.com.br/vagas/desenvolvedor/?page=2',
    'https://www.catho.com.br/vagas/desenvolvedor',
    'https://www.catho.com.br/vagas/desenvolvedor?page=2'
]

session = requests.Session()
session.headers.update(headers)

for url in urls:
    print(f"\nTestando: {url}")
    try:
        response = session.get(url, timeout=15)
        print(f"Status: {response.status_code}")
        print(f"Content-Length: {len(response.content)}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            title = soup.find('title')
            print(f"Title: {title.text if title else 'N/A'}")
            
            # Procurar por links de vagas
            job_links = soup.select('a[href*="/vaga"]')
            print(f"Links de vagas encontrados: {len(job_links)}")
            
            if job_links:
                print("Primeiros 3 links:")
                for i, link in enumerate(job_links[:3]):
                    print(f"  {i+1}. {link.get('href')}")
        else:
            print(f"Erro: {response.status_code}")
            print(f"Response headers: {dict(response.headers)}")
            
    except Exception as e:
        print(f"Erro na requisição: {e}")