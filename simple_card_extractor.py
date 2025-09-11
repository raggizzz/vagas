import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def extract_job_data_simple(driver, card, job_link):
    """Extração simplificada: clica no card, pega todo o texto, fecha e vai para próxima"""
    
    job_data = {
        'link': job_link,
        'titulo': '',
        'empresa': '',
        'localizacao': '',
        'salario': '',
        'descricao': '',
        'requisitos': '',
        'beneficios': '',
        'modalidade': '',
        'horario': '',
        'regime_contratacao': '',
        'data_publicacao': '',
        'nivel': ''
    }
    
    try:
        print(f"[DEBUG] Processando vaga: {job_link}")
        
        # 1. Clicar no card para abrir
        print(f"[DEBUG] Clicando no card...")
        card.click()
        time.sleep(3)  # Aguardar carregamento
        
        # 2. Extrair TODO o texto visível da página
        try:
            body_element = driver.find_element(By.TAG_NAME, "body")
            full_text = body_element.text
            print(f"[DEBUG] Texto completo extraído: {len(full_text)} caracteres")
            
            # Salvar o texto completo como descrição
            job_data['descricao'] = full_text[:5000] if full_text else ''
            
            # Tentar extrair título do texto (primeira linha que parece um título)
            lines = full_text.split('\n')
            for line in lines[:10]:  # Verificar primeiras 10 linhas
                line = line.strip()
                if len(line) > 10 and len(line) < 200:  # Tamanho razoável para título
                    job_data['titulo'] = line
                    break
                    
        except Exception as e:
            print(f"[ERROR] Erro ao extrair texto: {e}")
        
        # 3. Tentar fechar o card/modal
        close_selectors = [
            '[data-testid="close"]',
            '.close',
            '.fechar', 
            'button[aria-label="Fechar"]',
            'button[title="Fechar"]',
            '.modal-close',
            '[role="button"][aria-label="Close"]',
            'button:contains("×")',
            '.btn-close',
            '[data-dismiss="modal"]'
        ]
        
        closed = False
        for selector in close_selectors:
            try:
                close_btn = driver.find_element(By.CSS_SELECTOR, selector)
                close_btn.click()
                print(f"[DEBUG] Card fechado com sucesso usando: {selector}")
                time.sleep(1)
                closed = True
                break
            except:
                continue
        
        if not closed:
            # Se não conseguiu fechar, tentar ESC
            try:
                from selenium.webdriver.common.keys import Keys
                driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
                print(f"[DEBUG] Card fechado com ESC")
                time.sleep(1)
            except:
                print(f"[WARNING] Não foi possível fechar o card")
        
        print(f"[DEBUG] Vaga processada com sucesso")
        return job_data
        
    except Exception as e:
        print(f"[ERROR] Erro ao processar card: {str(e)}")
        return None

def test_simple_extraction():
    """Teste da extração simplificada"""
    
    # Configurar Chrome
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    
    driver = webdriver.Chrome(options=options)
    
    try:
        # Ir para página do Catho
        url = "https://www.catho.com.br/vagas/?area_id%5B0%5D=51&area_id%5B1%5D=52"  # Informática
        print(f"Acessando: {url}")
        driver.get(url)
        time.sleep(5)
        
        # Fechar overlay de LGPD se existir
        lgpd_selectors = [
            '#lgpd-consent-widget button',
            '.lgpd-close',
            '[data-testid="lgpd-accept"]',
            'button:contains("Aceitar")',
            'button:contains("Continuar")',
            '.cookie-accept',
            '.consent-accept'
        ]
        
        for selector in lgpd_selectors:
            try:
                lgpd_btn = driver.find_element(By.CSS_SELECTOR, selector)
                lgpd_btn.click()
                print(f"[DEBUG] Overlay LGPD fechado com: {selector}")
                time.sleep(2)
                break
            except:
                continue
        
        # Encontrar cards de vagas
        card_selectors = [
            '[data-testid="job-card"]',
            '.job-card',
            '.vaga-card',
            'article',
            '.sc-fzXfMO'
        ]
        
        cards = []
        for selector in card_selectors:
            try:
                found_cards = driver.find_elements(By.CSS_SELECTOR, selector)
                if found_cards:
                    cards = found_cards
                    print(f"Encontrados {len(cards)} cards com seletor: {selector}")
                    break
            except:
                continue
        
        if not cards:
            print("Nenhum card encontrado!")
            return
        
        # Processar apenas os primeiros 3 cards
        for i, card in enumerate(cards[:3]):
            print(f"\n=== PROCESSANDO CARD {i+1} ===")
            
            # Extrair link da vaga
            job_link = "#"
            try:
                link_elem = card.find_element(By.CSS_SELECTOR, "a")
                job_link = link_elem.get_attribute("href") or "#"
            except:
                pass
            
            # Extrair dados
            job_data = extract_job_data_simple(driver, card, job_link)
            
            if job_data:
                print(f"Título: {job_data['titulo'][:100]}...")
                print(f"Descrição: {len(job_data['descricao'])} caracteres")
            
            time.sleep(2)  # Pausa entre cards
    
    finally:
        driver.quit()

if __name__ == "__main__":
    test_simple_extraction()