from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import json

def extract_catho_job_titles():
    # Configurar o Chrome
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # Navegar para a página
        print("Navegando para https://www.catho.com.br/vagas/")
        driver.get("https://www.catho.com.br/vagas/")
        
        # Aguardar a página carregar
        time.sleep(5)
        
        # Tentar diferentes seletores para encontrar os títulos das vagas
        selectors = [
            "h2",
            "h3", 
            ".job-title",
            "[data-testid*='job']",
            ".vaga-titulo",
            ".titulo-vaga",
            "a[href*='/vagas/']",
            "[class*='title']",
            "[class*='titulo']",
            "[class*='job']"
        ]
        
        job_titles = []
        
        for selector in selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                print(f"Seletor '{selector}': {len(elements)} elementos encontrados")
                
                for element in elements:
                    try:
                        text = element.text.strip()
                        if text and len(text) > 10 and text not in job_titles:
                            # Filtrar textos que parecem ser títulos de vagas
                            if any(keyword in text.lower() for keyword in ['desenvolvedor', 'analista', 'gerente', 'coordenador', 'assistente', 'técnico', 'especialista', 'consultor', 'supervisor', 'diretor']):
                                job_titles.append(text)
                                print(f"Título encontrado: {text}")
                    except Exception as e:
                        continue
                        
            except Exception as e:
                print(f"Erro com seletor '{selector}': {e}")
                continue
        
        # Se não encontrou títulos específicos, pegar todos os links que parecem ser vagas
        if not job_titles:
            print("Tentando abordagem alternativa...")
            try:
                # Procurar por links que contenham '/vagas/' na URL
                vaga_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/vagas/']")
                print(f"Links de vagas encontrados: {len(vaga_links)}")
                
                for link in vaga_links[:20]:  # Limitar aos primeiros 20
                    try:
                        text = link.text.strip()
                        if text and len(text) > 5 and text not in job_titles:
                            job_titles.append(text)
                            print(f"Título de link: {text}")
                    except:
                        continue
            except Exception as e:
                print(f"Erro na abordagem alternativa: {e}")
        
        print(f"\nTotal de títulos únicos encontrados: {len(job_titles)}")
        
        # Salvar os resultados
        with open('catho_job_titles.json', 'w', encoding='utf-8') as f:
            json.dump({
                'total_titles': len(job_titles),
                'titles': job_titles,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }, f, ensure_ascii=False, indent=2)
        
        return job_titles
        
    except Exception as e:
        print(f"Erro geral: {e}")
        return []
    
    finally:
        driver.quit()

if __name__ == "__main__":
    titles = extract_catho_job_titles()
    print("\n=== TÍTULOS DAS VAGAS ENCONTRADOS ===")
    for i, title in enumerate(titles, 1):
        print(f"{i}. {title}")