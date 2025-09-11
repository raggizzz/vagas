import requests
import json
import time
import random
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class IndividualJobScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        # Mapeamento de setores
        self.sector_mapping = {
            'administracao': 'Administracao',
            'comercial-vendas': 'Comercial e vendas',
            'comunicacao-marketing': 'Comunicacao e marketing',
            'educacao': 'Educacao',
            'engenharia': 'Engenharia',
            'financeira': 'Financeira',
            'industrial': 'Industrial',
            'informatica': 'Informatica',
            'juridica': 'Juridica',
            'saude': 'Saude',
            'servico-social': 'ServicoSocial',
            'telecomunicacoes': 'Telecomunicacoes',
            'telemarketing': 'Telemarketing',
            'tecnica': 'Tecnica',
            'hotelaria-turismo': 'Hotelaria e turismo',
            'arquitetura-design': 'arquitetura e design',
            'pecuaria-veterinaria': 'pecuaria e veterinaria',
            'suprimentos': 'Suprimentos',
            'comercio-exterior': 'Comercio exterior'
        }
    
    def extract_job_details(self, job_url):
        """Extrai detalhes de uma vaga individual"""
        try:
            # Delay para evitar rate limiting
            time.sleep(random.uniform(1, 3))
            
            response = self.session.get(job_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extrair informações da vaga
            job_data = {
                'url': job_url,
                'titulo': self.extract_title(soup),
                'empresa': self.extract_company(soup),
                'localizacao': self.extract_location(soup),
                'salario': self.extract_salary(soup),
                'descricao': self.extract_description(soup),
                'requisitos': self.extract_requirements(soup),
                'beneficios': self.extract_benefits(soup),
                'tipo_contrato': self.extract_contract_type(soup),
                'nivel_experiencia': self.extract_experience_level(soup),
                'setor': self.extract_sector(soup, job_url),
                'data_publicacao': self.extract_publication_date(soup),
                'extracted_at': datetime.now().isoformat()
            }
            
            return job_data
            
        except Exception as e:
            logger.error(f"Erro ao extrair vaga {job_url}: {str(e)}")
            return None
    
    def extract_title(self, soup):
        """Extrai o título da vaga"""
        selectors = [
            'h1[data-testid="job-title"]',
            'h1.job-title',
            'h1',
            '.job-header h1',
            '[data-cy="job-title"]'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text(strip=True)
        
        return "Título não encontrado"
    
    def extract_company(self, soup):
        """Extrai o nome da empresa"""
        selectors = [
            '[data-testid="company-name"]',
            '.company-name',
            '.job-company',
            '[data-cy="company-name"]',
            '.company-info h2',
            '.company-info a'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                company = element.get_text(strip=True)
                if company and company.lower() != 'empresa confidencial':
                    return company
        
        return "Empresa Confidencial"
    
    def extract_location(self, soup):
        """Extrai a localização da vaga"""
        selectors = [
            '[data-testid="job-location"]',
            '.job-location',
            '.location',
            '[data-cy="job-location"]',
            '.job-info .location'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                location_text = element.get_text(strip=True)
                return self.parse_location(location_text)
        
        return {'cidade': 'Não informado', 'estado': 'Não informado'}
    
    def parse_location(self, location_text):
        """Parseia o texto de localização"""
        if not location_text:
            return {'cidade': 'Não informado', 'estado': 'Não informado'}
        
        # Padrões comuns: "Cidade - Estado", "Cidade, Estado", "Cidade/Estado"
        patterns = [
            r'([^,-/]+)\s*[-,/]\s*([A-Z]{2})\b',
            r'([^,-/]+)\s*[-,/]\s*([^,-/]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, location_text)
            if match:
                cidade = match.group(1).strip()
                estado = match.group(2).strip()
                return {'cidade': cidade, 'estado': estado}
        
        return {'cidade': location_text, 'estado': 'Não informado'}
    
    def extract_salary(self, soup):
        """Extrai informações de salário"""
        selectors = [
            '[data-testid="salary"]',
            '.salary',
            '.job-salary',
            '[data-cy="salary"]'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text(strip=True)
        
        return "A combinar"
    
    def extract_description(self, soup):
        """Extrai a descrição da vaga"""
        selectors = [
            '[data-testid="job-description"]',
            '.job-description',
            '.description',
            '[data-cy="job-description"]',
            '.job-content .description'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                # Remover tags HTML e limpar texto
                text = element.get_text(separator='\n', strip=True)
                return self.clean_text(text)
        
        return "Descrição não disponível"
    
    def extract_requirements(self, soup):
        """Extrai requisitos da vaga"""
        requirements_text = ""
        
        # Procurar seções de requisitos
        requirement_keywords = ['requisitos', 'requirements', 'qualificações', 'perfil']
        
        for keyword in requirement_keywords:
            elements = soup.find_all(text=re.compile(keyword, re.IGNORECASE))
            for element in elements:
                parent = element.parent
                if parent:
                    next_content = parent.find_next_sibling()
                    if next_content:
                        requirements_text += next_content.get_text(strip=True) + "\n"
        
        return self.clean_text(requirements_text) if requirements_text else "Não especificado"
    
    def extract_benefits(self, soup):
        """Extrai benefícios da vaga"""
        benefits_text = ""
        
        # Procurar seções de benefícios
        benefit_keywords = ['benefícios', 'benefits', 'oferecemos']
        
        for keyword in benefit_keywords:
            elements = soup.find_all(text=re.compile(keyword, re.IGNORECASE))
            for element in elements:
                parent = element.parent
                if parent:
                    next_content = parent.find_next_sibling()
                    if next_content:
                        benefits_text += next_content.get_text(strip=True) + "\n"
        
        return self.clean_text(benefits_text) if benefits_text else "Não especificado"
    
    def extract_contract_type(self, soup):
        """Extrai tipo de contrato"""
        contract_keywords = ['clt', 'pj', 'estágio', 'temporário', 'freelancer']
        
        page_text = soup.get_text().lower()
        
        for keyword in contract_keywords:
            if keyword in page_text:
                return keyword.upper()
        
        return "CLT"
    
    def extract_experience_level(self, soup):
        """Extrai nível de experiência"""
        experience_keywords = {
            'júnior': 'Junior',
            'junior': 'Junior',
            'pleno': 'Pleno',
            'sênior': 'Senior',
            'senior': 'Senior',
            'trainee': 'Trainee',
            'estágio': 'Estagio'
        }
        
        page_text = soup.get_text().lower()
        
        for keyword, level in experience_keywords.items():
            if keyword in page_text:
                return level
        
        return "Não especificado"
    
    def extract_sector(self, soup, job_url):
        """Extrai setor da vaga baseado na URL ou conteúdo"""
        # Tentar extrair da URL
        for sector_key, sector_name in self.sector_mapping.items():
            if sector_key in job_url:
                return sector_name
        
        # Se não encontrar na URL, tentar no conteúdo
        page_text = soup.get_text().lower()
        
        sector_keywords = {
            'administração': 'Administracao',
            'vendas': 'Comercial e vendas',
            'marketing': 'Comunicacao e marketing',
            'educação': 'Educacao',
            'engenharia': 'Engenharia',
            'financeiro': 'Financeira',
            'industrial': 'Industrial',
            'tecnologia': 'Informatica',
            'jurídico': 'Juridica',
            'saúde': 'Saude',
            'social': 'ServicoSocial',
            'telecomunicações': 'Telecomunicacoes'
        }
        
        for keyword, sector in sector_keywords.items():
            if keyword in page_text:
                return sector
        
        return "Geral"
    
    def extract_publication_date(self, soup):
        """Extrai data de publicação"""
        date_selectors = [
            '[data-testid="publication-date"]',
            '.publication-date',
            '.job-date'
        ]
        
        for selector in date_selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text(strip=True)
        
        return datetime.now().strftime('%Y-%m-%d')
    
    def clean_text(self, text):
        """Limpa e normaliza texto"""
        if not text:
            return ""
        
        # Remover múltiplas quebras de linha
        text = re.sub(r'\n+', '\n', text)
        # Remover espaços extras
        text = re.sub(r'\s+', ' ', text)
        # Remover caracteres especiais problemáticos
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)
        
        return text.strip()
    
    def scrape_job_urls_from_search(self, sector, max_pages=5):
        """Extrai URLs de vagas de uma busca por setor"""
        job_urls = []
        
        for page in range(1, max_pages + 1):
            try:
                search_url = f"https://www.catho.com.br/vagas/{sector}/?page={page}"
                logger.info(f"Buscando URLs na página {page} do setor {sector}")
                
                response = self.session.get(search_url, timeout=30)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Encontrar links de vagas
                job_links = soup.find_all('a', href=re.compile(r'/vagas/[^/]+/\d+'))
                
                page_urls = []
                for link in job_links:
                    href = link.get('href')
                    if href:
                        full_url = urljoin('https://www.catho.com.br', href)
                        if full_url not in job_urls:
                            job_urls.append(full_url)
                            page_urls.append(full_url)
                
                logger.info(f"Encontradas {len(page_urls)} URLs na página {page}")
                
                # Se não encontrou vagas, parar
                if not page_urls:
                    break
                
                time.sleep(random.uniform(2, 4))
                
            except Exception as e:
                logger.error(f"Erro ao buscar página {page} do setor {sector}: {str(e)}")
                break
        
        logger.info(f"Total de {len(job_urls)} URLs encontradas para o setor {sector}")
        return job_urls
    
    def scrape_sector_jobs(self, sector, max_jobs=50):
        """Faz scraping de vagas de um setor específico"""
        logger.info(f"Iniciando scraping do setor: {sector}")
        
        # Obter URLs das vagas
        job_urls = self.scrape_job_urls_from_search(sector, max_pages=10)
        
        if not job_urls:
            logger.warning(f"Nenhuma URL encontrada para o setor {sector}")
            return []
        
        # Limitar número de vagas
        job_urls = job_urls[:max_jobs]
        
        jobs_data = []
        
        for i, url in enumerate(job_urls, 1):
            logger.info(f"Extraindo vaga {i}/{len(job_urls)}: {url}")
            
            job_data = self.extract_job_details(url)
            
            if job_data:
                jobs_data.append(job_data)
                logger.info(f"Vaga extraída com sucesso: {job_data['titulo']}")
            else:
                logger.warning(f"Falha ao extrair vaga: {url}")
        
        logger.info(f"Scraping do setor {sector} concluído. {len(jobs_data)} vagas extraídas.")
        return jobs_data

def main():
    scraper = IndividualJobScraper()
    
    # Lista de setores para fazer scraping
    sectors = [
        'administracao',
        'comercial-vendas', 
        'comunicacao-marketing',
        'educacao',
        'engenharia',
        'financeira',
        'industrial',
        'informatica',
        'juridica',
        'saude'
    ]
    
    all_jobs = []
    
    for sector in sectors:
        try:
            sector_jobs = scraper.scrape_sector_jobs(sector, max_jobs=30)
            all_jobs.extend(sector_jobs)
            
            # Salvar dados parciais
            with open(f'vagas_{sector}_individuais.json', 'w', encoding='utf-8') as f:
                json.dump(sector_jobs, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Dados do setor {sector} salvos. Total de vagas até agora: {len(all_jobs)}")
            
            # Delay entre setores
            time.sleep(random.uniform(5, 10))
            
        except Exception as e:
            logger.error(f"Erro no scraping do setor {sector}: {str(e)}")
            continue
    
    # Salvar todos os dados
    with open('vagas_individuais_completo.json', 'w', encoding='utf-8') as f:
        json.dump(all_jobs, f, ensure_ascii=False, indent=2)
    
    # Converter para JSONL
    with open('vagas_individuais_completo.jsonl', 'w', encoding='utf-8') as f:
        for job in all_jobs:
            f.write(json.dumps(job, ensure_ascii=False) + '\n')
    
    logger.info(f"Scraping completo! Total de {len(all_jobs)} vagas extraídas.")
    
    # Relatório final
    report = {
        'total_jobs': len(all_jobs),
        'jobs_by_sector': {},
        'extraction_date': datetime.now().isoformat()
    }
    
    for job in all_jobs:
        sector = job.get('setor', 'Desconhecido')
        if sector not in report['jobs_by_sector']:
            report['jobs_by_sector'][sector] = 0
        report['jobs_by_sector'][sector] += 1
    
    with open('relatorio_scraping_individual.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n=== RELATÓRIO FINAL ===")
    print(f"Total de vagas extraídas: {len(all_jobs)}")
    print(f"Vagas por setor:")
    for sector, count in report['jobs_by_sector'].items():
        print(f"  {sector}: {count} vagas")

if __name__ == "__main__":
    main()