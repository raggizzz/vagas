#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extrator de Vagas do Catho - Versão Demo
Extrai algumas vagas de cada setor para demonstração rápida
"""

import json
import time
import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import re

class CathoSectorsExtractorDemo:
    def __init__(self):
        self.sectors = {
            "Administração": {
                "url": "https://www.catho.com.br/vagas/?area_id%5B0%5D=1&area_id%5B1%5D=3&area_id%5B2%5D=12&area_id%5B3%5D=20&area_id%5B4%5D=47&area_id%5B5%5D=67&area_id%5B6%5D=69&area_id%5B7%5D=73&area_id%5B8%5D=74&area_id%5B9%5D=75&area_id%5B10%5D=1906&area_id%5B11%5D=1937",
                "keywords": ["administração", "administrativo", "gestão", "coordenação", "supervisão", "gerência"]
            },
            "Comercial e Vendas": {
                "url": "https://www.catho.com.br/vagas/area-comercial-vendas/",
                "keywords": ["vendas", "comercial", "representante", "consultor", "account", "business"]
            },
            "Informática": {
                "url": "https://www.catho.com.br/vagas/?area_id%5B0%5D=51&area_id%5B1%5D=52",
                "keywords": ["desenvolvedor", "programador", "analista", "ti", "tecnologia", "software", "python", "java", "javascript"]
            },
            "Saúde": {
                "url": "https://www.catho.com.br/vagas/?area_id%5B0%5D=13&area_id%5B1%5D=26&area_id%5B2%5D=39&area_id%5B3%5D=41&area_id%5B4%5D=43&area_id%5B5%5D=45&area_id%5B6%5D=46&area_id%5B7%5D=58&area_id%5B8%5D=61&area_id%5B9%5D=62&area_id%5B10%5D=65&area_id%5B11%5D=1902",
                "keywords": ["enfermeiro", "médico", "saúde", "hospital", "clínica", "farmácia", "fisioterapeuta"]
            },
            "Engenharia": {
                "url": "https://www.catho.com.br/vagas/?area_id%5B0%5D=18&area_id%5B1%5D=29&area_id%5B2%5D=30&area_id%5B3%5D=31&area_id%5B4%5D=32&area_id%5B5%5D=34&area_id%5B6%5D=35&area_id%5B7%5D=36&area_id%5B8%5D=37&area_id%5B9%5D=38&area_id%5B10%5D=483&area_id%5B11%5D=484",
                "keywords": ["engenheiro", "engenharia", "técnico", "projeto", "construção", "civil", "mecânica"]
            }
        }
        
        self.driver = None
        self.jobs_data = []
        self.extraction_stats = {
            "total_jobs": 0,
            "jobs_by_sector": {},
            "extraction_time": None,
            "timestamp": datetime.now().isoformat()
        }
    
    def setup_driver(self):
        """Configura o driver do Chrome"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.implicitly_wait(10)
    
    def extract_job_details(self, job_element):
        """Extrai detalhes de uma vaga"""
        try:
            # Título da vaga
            title_element = job_element.find_element(By.CSS_SELECTOR, "h2 a, .job-title a, [data-testid='job-title'] a")
            title = title_element.text.strip()
            job_url = title_element.get_attribute("href")
            
            # Empresa
            try:
                company_element = job_element.find_element(By.CSS_SELECTOR, ".company-name, [data-testid='company-name'], .job-company")
                company = company_element.text.strip()
            except NoSuchElementException:
                company = "Não informado"
            
            # Localização
            try:
                location_element = job_element.find_element(By.CSS_SELECTOR, ".job-location, [data-testid='job-location'], .location")
                location = location_element.text.strip()
            except NoSuchElementException:
                location = "Não informado"
            
            # Salário
            try:
                salary_element = job_element.find_element(By.CSS_SELECTOR, ".salary, [data-testid='salary'], .job-salary")
                salary = salary_element.text.strip()
            except NoSuchElementException:
                salary = "A combinar"
            
            # Descrição
            try:
                desc_element = job_element.find_element(By.CSS_SELECTOR, ".job-description, .description, [data-testid='job-description']")
                description = desc_element.text.strip()
            except NoSuchElementException:
                description = ""
            
            return {
                "title": title,
                "company": company,
                "location": location,
                "salary": salary,
                "description": description,
                "url": job_url,
                "extracted_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"   ❌ Erro ao extrair vaga: {e}")
            return None
    
    def classify_job_sector(self, job_data):
        """Classifica a vaga em um setor baseado em palavras-chave"""
        text_to_analyze = f"{job_data['title']} {job_data['description']}".lower()
        
        sector_scores = {}
        
        for sector_name, sector_info in self.sectors.items():
            score = 0
            for keyword in sector_info['keywords']:
                if keyword.lower() in text_to_analyze:
                    score += 1
            
            if score > 0:
                sector_scores[sector_name] = score
        
        if sector_scores:
            # Retorna o setor com maior pontuação
            best_sector = max(sector_scores, key=sector_scores.get)
            return best_sector
        
        return "Outros"
    
    def extract_jobs_from_sector(self, sector_name, sector_info, max_jobs=10):
        """Extrai vagas de um setor específico (limitado para demo)"""
        print(f"🔍 Extraindo vagas do setor: {sector_name}")
        
        try:
            self.driver.get(sector_info['url'])
            time.sleep(3)
            
            # Aguarda carregar as vagas
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='job-card'], .job-item, .vacancy-item"))
            )
            
            # Encontra elementos de vagas
            job_elements = self.driver.find_elements(By.CSS_SELECTOR, "[data-testid='job-card'], .job-item, .vacancy-item")
            
            if not job_elements:
                print(f"   ⚠️ Nenhuma vaga encontrada para {sector_name}")
                return []
            
            jobs_extracted = []
            
            # Extrai apenas as primeiras vagas (para demo)
            for i, job_element in enumerate(job_elements[:max_jobs]):
                job_data = self.extract_job_details(job_element)
                
                if job_data:
                    # Classifica o setor
                    classified_sector = self.classify_job_sector(job_data)
                    job_data['sector'] = classified_sector
                    job_data['original_sector'] = sector_name
                    
                    jobs_extracted.append(job_data)
                    print(f"   ✅ Vaga {i+1}: {job_data['title'][:50]}... (Setor: {classified_sector})")
                
                time.sleep(1)  # Pausa entre extrações
            
            print(f"   📊 Total extraído de {sector_name}: {len(jobs_extracted)} vagas")
            return jobs_extracted
            
        except TimeoutException:
            print(f"   ⏰ Timeout ao carregar {sector_name}")
            return []
        except Exception as e:
            print(f"   ❌ Erro ao extrair {sector_name}: {e}")
            return []
    
    def run_extraction(self):
        """Executa a extração de todos os setores"""
        start_time = time.time()
        
        print("🚀 Iniciando extração DEMO dos setores do Catho...")
        print(f"📋 Total de setores: {len(self.sectors)}")
        
        self.setup_driver()
        
        try:
            for sector_name, sector_info in self.sectors.items():
                sector_jobs = self.extract_jobs_from_sector(sector_name, sector_info, max_jobs=5)
                
                if sector_jobs:
                    self.jobs_data.extend(sector_jobs)
                    self.extraction_stats['jobs_by_sector'][sector_name] = len(sector_jobs)
                
                time.sleep(2)  # Pausa entre setores
            
            # Finaliza estatísticas
            self.extraction_stats['total_jobs'] = len(self.jobs_data)
            self.extraction_stats['extraction_time'] = f"{time.time() - start_time:.2f} segundos"
            
            print(f"\n🎉 Extração concluída!")
            print(f"📊 Total de vagas extraídas: {self.extraction_stats['total_jobs']}")
            print(f"⏱️ Tempo de extração: {self.extraction_stats['extraction_time']}")
            
            # Salva os resultados
            self.save_results()
            
        finally:
            if self.driver:
                self.driver.quit()
    
    def save_results(self):
        """Salva os resultados em arquivos JSON e CSV"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Salva JSON completo
        json_filename = f"catho_vagas_demo_{timestamp}.json"
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump({
                "jobs": self.jobs_data,
                "statistics": self.extraction_stats,
                "sectors_info": self.sectors
            }, f, ensure_ascii=False, indent=2)
        
        # Salva CSV
        if self.jobs_data:
            df = pd.DataFrame(self.jobs_data)
            csv_filename = f"catho_vagas_demo_{timestamp}.csv"
            df.to_csv(csv_filename, index=False, encoding='utf-8')
            
            print(f"💾 Arquivos salvos:")
            print(f"   📄 JSON: {json_filename}")
            print(f"   📊 CSV: {csv_filename}")
            
            # Mostra estatísticas por setor
            print(f"\n📈 Estatísticas por setor:")
            for sector, count in self.extraction_stats['jobs_by_sector'].items():
                print(f"   {sector}: {count} vagas")

if __name__ == "__main__":
    extractor = CathoSectorsExtractorDemo()
    extractor.run_extraction()