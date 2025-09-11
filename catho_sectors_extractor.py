import requests
import pandas as pd
import json
import time
import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import random

# Mapeamento de setores do Catho
CATHO_SECTORS = {
    'administracao': {
        'name': 'Administração',
        'url': 'https://www.catho.com.br/vagas/?area_id%5B0%5D=1&area_id%5B1%5D=3&area_id%5B2%5D=12&area_id%5B3%5D=20&area_id%5B4%5D=47&area_id%5B5%5D=67&area_id%5B6%5D=69&area_id%5B7%5D=73&area_id%5B8%5D=74&area_id%5B9%5D=75&area_id%5B10%5D=1906&area_id%5B11%5D=1937'
    },
    'comercial_vendas': {
        'name': 'Comercial e Vendas',
        'url': 'https://www.catho.com.br/vagas/area-comercial-vendas/'
    },
    'comercio_exterior': {
        'name': 'Comércio Exterior',
        'url': 'https://www.catho.com.br/vagas/?area_id%5B0%5D=15&area_id%5B1%5D=70'
    },
    'educacao': {
        'name': 'Educação',
        'url': 'https://www.catho.com.br/vagas/?area_id%5B0%5D=24&area_id%5B1%5D=87'
    },
    'financeira': {
        'name': 'Financeira',
        'url': 'https://www.catho.com.br/vagas/?area_id%5B0%5D=2&area_id%5B1%5D=11&area_id%5B2%5D=19&area_id%5B3%5D=23&area_id%5B4%5D=40&area_id%5B5%5D=76'
    },
    'hotelaria_turismo': {
        'name': 'Hotelaria e Turismo',
        'url': 'https://www.catho.com.br/vagas/?area_id%5B0%5D=48&area_id%5B1%5D=72'
    },
    'informatica': {
        'name': 'Informática',
        'url': 'https://www.catho.com.br/vagas/?area_id%5B0%5D=51&area_id%5B1%5D=52'
    },
    'saude': {
        'name': 'Saúde',
        'url': 'https://www.catho.com.br/vagas/?area_id%5B0%5D=13&area_id%5B1%5D=26&area_id%5B2%5D=39&area_id%5B3%5D=41&area_id%5B4%5D=43&area_id%5B5%5D=45&area_id%5B6%5D=46&area_id%5B7%5D=58&area_id%5B8%5D=61&area_id%5B9%5D=62&area_id%5B10%5D=65&area_id%5B11%5D=1902'
    },
    'suprimentos': {
        'name': 'Suprimentos',
        'url': 'https://www.catho.com.br/vagas/?area_id%5B0%5D=55&area_id%5B1%5D=88'
    },
    'agricultura_pecuaria_veterinaria': {
        'name': 'Agricultura, Pecuária e Veterinária',
        'url': 'https://www.catho.com.br/vagas/?area_id%5B0%5D=1858&area_id%5B1%5D=1859&area_id%5B2%5D=1904&area_id%5B3%5D=1943'
    },
    'artes_arquitetura_design': {
        'name': 'Artes, Arquitetura e Design',
        'url': 'https://www.catho.com.br/vagas/?area_id%5B0%5D=5&area_id%5B1%5D=6&area_id%5B2%5D=7&area_id%5B3%5D=21&area_id%5B4%5D=60'
    },
    'comunicacao_marketing': {
        'name': 'Comunicação e Marketing',
        'url': 'https://www.catho.com.br/vagas/?area_id%5B0%5D=53&area_id%5B1%5D=57&area_id%5B2%5D=66&area_id%5B3%5D=71&area_id%5B4%5D=1965'
    },
    'engenharia': {
        'name': 'Engenharia',
        'url': 'https://www.catho.com.br/vagas/?area_id%5B0%5D=18&area_id%5B1%5D=29&area_id%5B2%5D=30&area_id%5B3%5D=31&area_id%5B4%5D=32&area_id%5B5%5D=34&area_id%5B6%5D=35&area_id%5B7%5D=36&area_id%5B8%5D=37&area_id%5B9%5D=38&area_id%5B10%5D=483&area_id%5B11%5D=484'
    },
    'industrial': {
        'name': 'Industrial',
        'url': 'https://www.catho.com.br/vagas/?area_id%5B0%5D=9&area_id%5B1%5D=10&area_id%5B2%5D=25&area_id%5B3%5D=50&area_id%5B4%5D=56'
    },
    'juridica': {
        'name': 'Jurídica',
        'url': 'https://www.catho.com.br/vagas/area-juridica/'
    },
    'tecnica': {
        'name': 'Técnica',
        'url': 'https://www.catho.com.br/vagas/?area_id%5B0%5D=79&area_id%5B1%5D=80'
    },
    'telemarketing': {
        'name': 'Telemarketing',
        'url': 'https://www.catho.com.br/vagas/area-atendimento-ao-cliente-call-center-telemarketing/'
    },
    'telecomunicacoes': {
        'name': 'Telecomunicações',
        'url': 'https://www.catho.com.br/vagas/area-telecomunicacoes-engenharia-de-telecomunicacoes/'
    },
    'servico_social': {
        'name': 'Serviço Social',
        'url': 'https://www.catho.com.br/vagas/area-servico-social/'
    }
}

# Função de classificação removida - keywords foram removidas do dicionário

def setup_selenium_driver():
    """Configura o driver do Selenium"""
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
    
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def extract_jobs_from_sector(sector_key, sector_info, max_pages=5):
    """Extrai vagas de um setor específico"""
    print(f"\n🔍 Extraindo vagas do setor: {sector_info['name']}")
    
    driver = setup_selenium_driver()
    jobs = []
    
    try:
        for page in range(1, max_pages + 1):
            print(f"   📄 Página {page}/{max_pages}")
            
            # Constrói URL da página
            if '?' in sector_info['url']:
                page_url = f"{sector_info['url']}&page={page}"
            else:
                page_url = f"{sector_info['url']}?page={page}"
            
            driver.get(page_url)
            time.sleep(random.uniform(2, 4))
            
            # Aguarda carregamento da página
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid*='job'], .job-item, .vaga-item, h2, h3"))
                )
            except TimeoutException:
                print(f"      ⚠️ Timeout na página {page}")
                continue
            
            # Extrai vagas da página
            job_elements = driver.find_elements(By.CSS_SELECTOR, 
                "[data-testid*='job'], .job-item, .vaga-item, .job-card, .vacancy-card")
            
            if not job_elements:
                # Fallback: busca por títulos
                job_elements = driver.find_elements(By.CSS_SELECTOR, "h2, h3")
            
            page_jobs = 0
            for element in job_elements:
                try:
                    # Extrai título
                    title_elem = element.find_element(By.CSS_SELECTOR, "h2, h3, .job-title, .vaga-titulo, a")
                    title = title_elem.text.strip()
                    
                    if not title or len(title) < 5:
                        continue
                    
                    # Extrai link
                    link = ""
                    try:
                        link_elem = element.find_element(By.CSS_SELECTOR, "a")
                        link = link_elem.get_attribute('href') or ""
                    except:
                        pass
                    
                    # Extrai empresa
                    company = ""
                    try:
                        company_elem = element.find_element(By.CSS_SELECTOR, ".company, .empresa, .job-company")
                        company = company_elem.text.strip()
                    except:
                        pass
                    
                    # Extrai localização
                    location = ""
                    try:
                        location_elem = element.find_element(By.CSS_SELECTOR, ".location, .localidade, .job-location")
                        location = location_elem.text.strip()
                    except:
                        pass
                    
                    # Extrai descrição (se disponível)
                    description = ""
                    try:
                        desc_elem = element.find_element(By.CSS_SELECTOR, ".description, .descricao, .job-description")
                        description = desc_elem.text.strip()
                    except:
                        pass
                    
                    job = {
                        'title': title,
                        'company': company,
                        'location': location,
                        'description': description,
                        'link': link,
                        'source_sector': sector_key,
                        'source_sector_name': sector_info['name'],
                        'extraction_date': datetime.now().isoformat(),
                        'page': page
                    }
                    
                    jobs.append(job)
                    page_jobs += 1
                    
                except Exception as e:
                    continue
            
            print(f"      ✅ {page_jobs} vagas extraídas da página {page}")
            
            # Se não encontrou vagas, para a extração
            if page_jobs == 0:
                print(f"      🛑 Nenhuma vaga encontrada na página {page}, parando extração")
                break
            
            # Delay entre páginas
            time.sleep(random.uniform(1, 3))
    
    except Exception as e:
        print(f"      ❌ Erro na extração do setor {sector_info['name']}: {str(e)}")
    
    finally:
        driver.quit()
    
    print(f"   📊 Total de vagas extraídas do setor {sector_info['name']}: {len(jobs)}")
    return jobs

def extract_all_sectors(max_pages_per_sector=3):
    """Extrai vagas de todos os setores"""
    print("🚀 Iniciando extração de TODOS os setores do Catho...")
    print(f"📋 Total de setores: {len(CATHO_SECTORS)}")
    print(f"📄 Máximo de páginas por setor: {max_pages_per_sector}")
    
    all_jobs = []
    sector_stats = {}
    
    for sector_key, sector_info in CATHO_SECTORS.items():
        try:
            sector_jobs = extract_jobs_from_sector(sector_key, sector_info, max_pages_per_sector)
            all_jobs.extend(sector_jobs)
            sector_stats[sector_key] = {
                'name': sector_info['name'],
                'jobs_count': len(sector_jobs)
            }
        except Exception as e:
            print(f"❌ Erro no setor {sector_info['name']}: {str(e)}")
            sector_stats[sector_key] = {
                'name': sector_info['name'],
                'jobs_count': 0,
                'error': str(e)
            }
    
    # Cria estrutura final
    final_data = {
        'metadata': {
            'extraction_date': datetime.now().isoformat(),
            'total_jobs': len(all_jobs),
            'total_sectors': len(CATHO_SECTORS),
            'max_pages_per_sector': max_pages_per_sector,
            'sector_stats': sector_stats,
            'extraction_method': 'catho_sectors_extraction',
            'version': '1.0'
        },
        'sectors': CATHO_SECTORS,
        'jobs': all_jobs
    }
    
    # Salva arquivo JSON
    output_file = f'catho_all_sectors_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(final_data, f, ensure_ascii=False, indent=2)
    
    # Salva também como CSV
    csv_file = f'catho_all_sectors_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    df = pd.DataFrame(all_jobs)
    df.to_csv(csv_file, index=False, encoding='utf-8')
    
    # Estatísticas finais
    print("\n" + "="*60)
    print("📊 RELATÓRIO FINAL DA EXTRAÇÃO")
    print("="*60)
    print(f"📁 Arquivo JSON: {output_file}")
    print(f"📁 Arquivo CSV: {csv_file}")
    print(f"📊 Total de vagas extraídas: {len(all_jobs)}")
    print(f"📋 Setores processados: {len(CATHO_SECTORS)}")
    print("\n📈 Vagas por setor:")
    
    for sector_key, stats in sector_stats.items():
        if 'error' in stats:
            print(f"   ❌ {stats['name']}: ERRO - {stats['error']}")
        else:
            print(f"   ✅ {stats['name']}: {stats['jobs_count']} vagas")
    
    # Análise de classificação
    print("\n🎯 Análise de classificação por setor:")
    classification_stats = {}
    for job in all_jobs:
        classified = job['classified_sector']
        if classified not in classification_stats:
            classification_stats[classified] = 0
        classification_stats[classified] += 1
    
    for sector, count in sorted(classification_stats.items(), key=lambda x: x[1], reverse=True):
        sector_name = CATHO_SECTORS.get(sector, {}).get('name', sector)
        print(f"   📊 {sector_name}: {count} vagas")
    
    return output_file, csv_file

if __name__ == "__main__":
    # Executa extração de todos os setores
    json_file, csv_file = extract_all_sectors(max_pages_per_sector=2)
    print(f"\n🎉 Extração concluída!")
    print(f"📁 Arquivos gerados:")
    print(f"   - {json_file}")
    print(f"   - {csv_file}")