from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import random

def test_catho_with_basic_selenium():
    print("Iniciando teste com Selenium básico...")
    
    # Configurar opções do Chrome
    options = Options()
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    # Criar driver
    driver = None
    try:
        driver = webdriver.Chrome(options=options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        # URLs para testar
        urls = [
            'https://www.catho.com.br/',
            'https://www.catho.com.br/vagas/',
            'https://www.catho.com.br/vagas/desenvolvedor/'
        ]
        
        for url in urls:
            print(f"\nTestando: {url}")
            try:
                driver.get(url)
                
                # Aguardar carregamento
                time.sleep(random.uniform(3, 6))
                
                # Verificar se a página carregou
                current_url = driver.current_url
                title = driver.title
                page_source_length = len(driver.page_source)
                
                print(f"URL atual: {current_url}")
                print(f"Título: {title}")
                print(f"Tamanho do HTML: {page_source_length}")
                
                # Verificar se é página de erro 404
                if "operação inválida" in title.lower() or "404" in title.lower():
                    print("❌ Página de erro 404 detectada")
                    continue
                
                # Verificar se há proteção Cloudflare
                if "cloudflare" in driver.page_source.lower() or "checking your browser" in driver.page_source.lower():
                    print("🔒 Proteção Cloudflare detectada, aguardando...")
                    time.sleep(10)
                    
                # Procurar por elementos de vagas
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                
                # Procurar links de vagas
                job_links = []
                selectors = [
                    'a[href*="/vaga"]',
                    'a[href*="/vagas/"]',
                    'a[href*="/emprego"]',
                    '.job-card a',
                    '.vacancy-card a'
                ]
                
                for selector in selectors:
                    links = soup.select(selector)
                    if links:
                        job_links.extend(links)
                        print(f"✅ Encontrados {len(links)} links com seletor '{selector}'")
                
                # Procurar formulário de busca
                search_forms = soup.find_all('form')
                search_inputs = soup.find_all('input', {'type': ['search', 'text']})
                
                print(f"Formulários encontrados: {len(search_forms)}")
                print(f"Campos de busca encontrados: {len(search_inputs)}")
                
                if len(job_links) > 0:
                    print(f"✅ SUCESSO! Encontrados {len(job_links)} links de vagas")
                    print("Primeiros 3 links:")
                    for i, link in enumerate(job_links[:3]):
                        href = link.get('href', '')
                        text = link.get_text(strip=True)[:50]
                        print(f"  {i+1}. {href} - {text}")
                    
                    # Salvar HTML de sucesso
                    filename = f"catho_selenium_success_{url.split('/')[-2] or 'root'}.html"
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(driver.page_source)
                    print(f"HTML salvo em {filename}")
                    
                    return True  # Sucesso!
                else:
                    print("❌ Nenhum link de vaga encontrado")
                    
                    # Salvar HTML para análise
                    filename = f"catho_selenium_debug_{url.split('/')[-2] or 'root'}.html"
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(driver.page_source)
                    print(f"HTML salvo em {filename} para análise")
                
            except Exception as e:
                print(f"❌ Erro ao acessar {url}: {e}")
            
            # Delay entre requisições
            time.sleep(random.uniform(2, 4))
        
        return False
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        return False
    
    finally:
        if driver:
            try:
                driver.quit()
                print("\nDriver fechado.")
            except:
                pass

if __name__ == "__main__":
    success = test_catho_with_basic_selenium()
    if success:
        print("\n🎉 SUCESSO! Conseguimos acessar o Catho com Selenium!")
    else:
        print("\n😞 Falha: Não conseguimos acessar o Catho mesmo com Selenium.")
        print("\n💡 RECOMENDAÇÃO: O Catho.com.br parece estar completamente bloqueado.")
        print("   Alternativas sugeridas:")
        print("   1. Usar outros sites de vagas (InfoJobs, LinkedIn, Indeed)")
        print("   2. Usar proxy/VPN para contornar bloqueio por região")
        print("   3. Focar nos scrapers que já funcionam (InfoJobs, LinkedIn)")