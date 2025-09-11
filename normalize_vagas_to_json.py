#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Normalizador de Vagas para JSON - Versão 7.0
Processa descrições complexas extraindo informações completas
"""

import pandas as pd
import json
import re
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
from collections import Counter

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('normalize_vagas.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class Seniority(Enum):
    JUNIOR = "Júnior"
    PLENO = "Pleno"
    SENIOR = "Sênior"
    COORDENADOR = "Coordenador"
    GERENTE = "Gerente"
    DIRETOR = "Diretor"
    ESTAGIARIO = "Estagiário"
    TRAINEE = "Trainee"
    ESPECIALISTA = "Especialista"
    ANALISTA = "Analista"
    ASSISTENTE = "Assistente"
    AUXILIAR = "Auxiliar"
    TECNICO = "Técnico"
    NAO_ESPECIFICADO = "Não especificado"

class EmploymentType(Enum):
    CLT = "CLT"
    PJ = "PJ"
    FREELANCER = "Freelancer"
    ESTAGIO = "Estágio"
    TEMPORARIO = "Temporário"
    TERCEIRIZADO = "Terceirizado"
    NAO_ESPECIFICADO = "Não especificado"

class Modality(Enum):
    PRESENCIAL = "Presencial"
    REMOTO = "Remoto"
    HIBRIDO = "Híbrido"
    NAO_ESPECIFICADO = "Não especificado"

@dataclass
class JobData:
    title: str
    seniority: str
    area: str
    company_name: str
    industry: str
    employment_type: str
    work_schedule: str
    modality: str
    location_city: str
    location_state: str
    location_region: str
    salary_min: Optional[float]
    salary_max: Optional[float]
    salary_currency: str
    salary_period: str
    benefits: List[str]
    rewards: List[str]
    requirements_must: List[str]
    requirements_nice: List[str]
    education_level: str
    responsibilities: List[str]
    pcd: bool
    tags: List[str]
    source_name: str
    source_url: str
    raw_excerpt: str
    confidence: float
    parsed_at: str

class AdvancedVagasNormalizer:
    def __init__(self):
        self.state_regions = {
            'AC': 'Norte', 'AL': 'Nordeste', 'AP': 'Norte', 'AM': 'Norte', 'BA': 'Nordeste',
            'CE': 'Nordeste', 'DF': 'Centro-Oeste', 'ES': 'Sudeste', 'GO': 'Centro-Oeste',
            'MA': 'Nordeste', 'MT': 'Centro-Oeste', 'MS': 'Centro-Oeste', 'MG': 'Sudeste',
            'PA': 'Norte', 'PB': 'Nordeste', 'PR': 'Sul', 'PE': 'Nordeste', 'PI': 'Nordeste',
            'RJ': 'Sudeste', 'RN': 'Nordeste', 'RS': 'Sul', 'RO': 'Norte', 'RR': 'Norte',
            'SC': 'Sul', 'SP': 'Sudeste', 'SE': 'Nordeste', 'TO': 'Norte'
        }
        
        # Padrões para extração
        self.salary_patterns = [
            r'R\$\s*([\d.,]+)\s*(?:a|até)\s*R\$\s*([\d.,]+)',
            r'salário[:\s]*R\$\s*([\d.,]+)',
            r'remuneração[:\s]*R\$\s*([\d.,]+)',
            r'([\d.,]+)\s*reais?',
            r'De R\$\s*([\d.,]+)\s*a\s*R\$\s*([\d.,]+)',
            r'Até R\$\s*([\d.,]+)'
        ]
        
        self.location_patterns = [
            r'([A-ZÁÊÇÕ][a-záêçõ\s]+)\s*-\s*([A-Z]{2})',
            r'Unidade:\s*([^-]+)\s*-\s*([^-]+)\s*-\s*([A-Z]{2})',
            r'Local:\s*([^,]+),?\s*([A-Z]{2})?',
            r'Região\s*(?:de|da)?\s*([A-ZÁÊÇÕ][a-záêçõ\s]+)',
            r'([A-ZÁÊÇÕ][a-záêçõ\s]+)/([A-Z]{2})'
        ]
        
        self.company_patterns = [
            r'EMPRESA[:\s]*([A-ZÁÊÇÕ][A-Za-záêçõ\s&.-]+)',
            r'([A-ZÁÊÇÕ][A-Za-záêçõ\s&.-]+)\s*(?:LTDA|S\.A\.|EIRELI)',
            r'Na\s+([A-ZÁÊÇÕ][A-Za-záêçõ\s&.-]+),',
            r'Hospital\s+([A-Za-záêçõ\s]+)',
            r'Colégio\s+([A-Za-záêçõ\s]+)',
            r'^([A-ZÁÊÇÕ][A-Za-záêçõ\s&.-]{3,30})\s*(?:Receber|Atendimento|Coordenar)'
        ]
        
        self.benefits_keywords = [
            'vale transporte', 'vale alimentação', 'vale refeição', 'plano de saúde',
            'plano odontológico', 'seguro de vida', 'auxílio creche', 'gympass',
            'participação nos lucros', 'décimo terceiro', 'férias', 'fgts',
            'convênio médico', 'ticket refeição', 'fretado', 'estacionamento'
        ]
        
        self.requirements_keywords = [
            'experiência', 'formação', 'curso', 'conhecimento', 'habilidade',
            'competência', 'requisito', 'necessário', 'obrigatório', 'desejável',
            'superior completo', 'ensino médio', 'técnico', 'graduação'
        ]

    def extract_salary_info(self, text: str) -> Tuple[Optional[float], Optional[float]]:
        """Extrai informações de salário do texto"""
        if not text:
            return None, None
            
        text_clean = text.lower().replace('.', '').replace(',', '.')
        
        for pattern in self.salary_patterns:
            match = re.search(pattern, text_clean, re.IGNORECASE)
            if match:
                try:
                    if len(match.groups()) == 2:
                        min_sal = float(match.group(1).replace('.', '').replace(',', '.'))
                        max_sal = float(match.group(2).replace('.', '').replace(',', '.'))
                        return min_sal, max_sal
                    else:
                        salary = float(match.group(1).replace('.', '').replace(',', '.'))
                        return salary, salary
                except (ValueError, AttributeError):
                    continue
        
        return None, None

    def extract_location_info(self, text: str) -> Tuple[str, str, str]:
        """Extrai informações de localização do texto"""
        if not text:
            return "", "", ""
            
        for pattern in self.location_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                groups = match.groups()
                if len(groups) >= 2:
                    city = groups[-2].strip() if len(groups) >= 2 else ""
                    state = groups[-1].strip() if len(groups) >= 1 else ""
                    region = self.state_regions.get(state, "")
                    return city, state, region
        
        return "", "", ""

    def extract_company_info(self, text: str) -> str:
        """Extrai nome da empresa do texto"""
        if not text:
            return ""
            
        for pattern in self.company_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                company = match.group(1).strip()
                if len(company) > 3 and not company.lower() in ['empresa', 'confidencial', 'por que']:
                    return company
        
        return ""

    def extract_benefits(self, text: str) -> List[str]:
        """Extrai benefícios do texto"""
        if not text:
            return []
            
        benefits = []
        text_lower = text.lower()
        
        for benefit in self.benefits_keywords:
            if benefit in text_lower:
                benefits.append(benefit.title())
        
        # Busca por padrões específicos
        benefit_patterns = [
            r'vale\s+([a-záêçõ]+)',
            r'auxílio\s+([a-záêçõ]+)',
            r'plano\s+([a-záêçõ\s]+)',
            r'convênio\s+([a-záêçõ]+)'
        ]
        
        for pattern in benefit_patterns:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                benefit_name = f"Vale {match.title()}" if 'vale' in pattern else f"Plano {match.title()}"
                if benefit_name not in benefits:
                    benefits.append(benefit_name)
        
        return list(set(benefits))

    def extract_requirements(self, text: str) -> Tuple[List[str], List[str]]:
        """Extrai requisitos obrigatórios e desejáveis"""
        if not text:
            return [], []
            
        must_requirements = []
        nice_requirements = []
        
        # Busca por seções específicas
        req_sections = re.split(r'(?:requisitos?|exigências?|necessário|obrigatório)[:.]?', text, flags=re.IGNORECASE)
        
        if len(req_sections) > 1:
            req_text = req_sections[1][:500]  # Limita o texto
            
            # Extrai requisitos por padrões
            req_patterns = [
                r'([A-Za-záêçõ\s]+(?:completo|superior|técnico|graduação))',
                r'experiência\s+(?:de\s+)?([\d]+)\s*(?:anos?|meses?)',
                r'conhecimento\s+em\s+([A-Za-záêçõ\s,]+)',
                r'formação\s+em\s+([A-Za-záêçõ\s]+)'
            ]
            
            for pattern in req_patterns:
                matches = re.findall(pattern, req_text, re.IGNORECASE)
                for match in matches:
                    if isinstance(match, str) and len(match.strip()) > 3:
                        must_requirements.append(match.strip())
        
        return list(set(must_requirements)), list(set(nice_requirements))

    def extract_responsibilities(self, text: str) -> List[str]:
        """Extrai responsabilidades do texto"""
        if not text:
            return []
            
        responsibilities = []
        
        # Busca por seções de responsabilidades
        resp_sections = re.split(r'(?:responsabilidades?|atividades?|funções?)[:.]?', text, flags=re.IGNORECASE)
        
        if len(resp_sections) > 1:
            resp_text = resp_sections[1][:1000]  # Limita o texto
            
            # Divide por pontos, vírgulas ou quebras de linha
            items = re.split(r'[;•\n]|(?:\.)\s*(?=[A-Z])', resp_text)
            
            for item in items:
                item = item.strip()
                if len(item) > 10 and not item.lower().startswith(('empresa', 'confidencial')):
                    responsibilities.append(item[:200])  # Limita tamanho
        
        return responsibilities[:10]  # Máximo 10 responsabilidades

    def determine_seniority(self, title: str, description: str) -> str:
        """Determina senioridade baseada no título e descrição"""
        text = f"{title} {description}".lower()
        
        seniority_map = {
            'estagiário': Seniority.ESTAGIARIO.value,
            'trainee': Seniority.TRAINEE.value,
            'júnior': Seniority.JUNIOR.value,
            'junior': Seniority.JUNIOR.value,
            'pleno': Seniority.PLENO.value,
            'sênior': Seniority.SENIOR.value,
            'senior': Seniority.SENIOR.value,
            'coordenador': Seniority.COORDENADOR.value,
            'gerente': Seniority.GERENTE.value,
            'diretor': Seniority.DIRETOR.value,
            'especialista': Seniority.ESPECIALISTA.value,
            'analista': Seniority.ANALISTA.value,
            'assistente': Seniority.ASSISTENTE.value,
            'auxiliar': Seniority.AUXILIAR.value,
            'técnico': Seniority.TECNICO.value
        }
        
        for keyword, level in seniority_map.items():
            if keyword in text:
                return level
        
        return Seniority.NAO_ESPECIFICADO.value

    def extract_tags(self, text: str, sector: str) -> List[str]:
        """Extrai tags relevantes do texto"""
        if not text:
            return []
            
        tags = []
        
        # Adiciona setor como tag principal
        if sector:
            tags.append(sector.upper())
        
        # Tags por área/setor
        area_keywords = {
            'VENDAS': ['venda', 'vendedor', 'comercial', 'cliente'],
            'MARKETING': ['marketing', 'publicidade', 'propaganda', 'digital'],
            'TECNOLOGIA': ['desenvolvedor', 'programador', 'sistema', 'software', 'ti'],
            'SAÚDE': ['médico', 'enfermeiro', 'hospital', 'clínica', 'saúde'],
            'EDUCAÇÃO': ['professor', 'educador', 'escola', 'ensino', 'pedagógico'],
            'SOCIAL': ['social', 'assistente social', 'projeto social', 'comunidade'],
            'ADMINISTRATIVO': ['administrativo', 'escritório', 'gestão', 'coordenação'],
            'OPERACIONAL': ['operador', 'técnico', 'manutenção', 'produção']
        }
        
        text_lower = text.lower()
        for tag, keywords in area_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                tags.append(tag)
        
        return list(set(tags))

    def process_description_segments(self, description: str) -> Dict[str, Any]:
        """Processa segmentos da descrição separados por |"""
        if not description:
            return {}
            
        segments = [seg.strip() for seg in description.split('|') if seg.strip()]
        
        consolidated_data = {
            'companies': [],
            'locations': [],
            'salaries': [],
            'benefits': [],
            'requirements': [],
            'responsibilities': [],
            'full_text': description
        }
        
        for segment in segments:
            if len(segment) < 10:  # Ignora segmentos muito pequenos
                continue
                
            # Extrai informações de cada segmento
            company = self.extract_company_info(segment)
            if company:
                consolidated_data['companies'].append(company)
            
            city, state, region = self.extract_location_info(segment)
            if city or state:
                consolidated_data['locations'].append({'city': city, 'state': state, 'region': region})
            
            min_sal, max_sal = self.extract_salary_info(segment)
            if min_sal or max_sal:
                consolidated_data['salaries'].append({'min': min_sal, 'max': max_sal})
            
            benefits = self.extract_benefits(segment)
            consolidated_data['benefits'].extend(benefits)
            
            must_req, nice_req = self.extract_requirements(segment)
            consolidated_data['requirements'].extend(must_req)
            
            responsibilities = self.extract_responsibilities(segment)
            consolidated_data['responsibilities'].extend(responsibilities)
        
        # Remove duplicatas
        consolidated_data['companies'] = list(set(consolidated_data['companies']))
        consolidated_data['benefits'] = list(set(consolidated_data['benefits']))
        consolidated_data['requirements'] = list(set(consolidated_data['requirements']))
        consolidated_data['responsibilities'] = list(set(consolidated_data['responsibilities']))
        
        return consolidated_data

    def normalize_job(self, row: pd.Series) -> JobData:
        """Normaliza uma linha de vaga para o formato estruturado"""
        try:
            # Dados básicos
            source_name = str(row.get('Título', '')).strip()
            source_url = str(row.get('URL', '')).strip()
            description = str(row.get('Descrição', '')).strip()
            sector = str(row.get('Setor', '')).strip()
            
            # Processa descrição completa
            desc_data = self.process_description_segments(description)
            
            # Extrai informações consolidadas
            company_name = desc_data['companies'][0] if desc_data['companies'] else ""
            
            # Localização (pega a primeira válida)
            location_city = ""
            location_state = ""
            location_region = ""
            if desc_data['locations']:
                loc = desc_data['locations'][0]
                location_city = loc['city']
                location_state = loc['state']
                location_region = loc['region']
            
            # Salário (pega o primeiro válido)
            salary_min = None
            salary_max = None
            if desc_data['salaries']:
                sal = desc_data['salaries'][0]
                salary_min = sal['min']
                salary_max = sal['max']
            
            # Determina senioridade
            seniority = self.determine_seniority(source_name, description)
            
            # Extrai tags
            tags = self.extract_tags(description, sector)
            
            # Calcula confiança baseada na quantidade de dados extraídos
            confidence = 0.3
            if company_name: confidence += 0.2
            if location_city: confidence += 0.2
            if salary_min: confidence += 0.2
            if desc_data['responsibilities']: confidence += 0.1
            
            return JobData(
                title=source_name,
                seniority=seniority,
                area=sector,
                company_name=company_name,
                industry="",
                employment_type=EmploymentType.CLT.value,
                work_schedule="Não especificado",
                modality=Modality.PRESENCIAL.value,
                location_city=location_city,
                location_state=location_state,
                location_region=location_region,
                salary_min=salary_min,
                salary_max=salary_max,
                salary_currency="BRL",
                salary_period="month",
                benefits=desc_data['benefits'][:10],
                rewards=[],
                requirements_must=desc_data['requirements'][:10],
                requirements_nice=[],
                education_level="Não especificado",
                responsibilities=desc_data['responsibilities'][:10],
                pcd=False,
                tags=tags,
                source_name=source_name,
                source_url=source_url,
                raw_excerpt=sector,
                confidence=min(confidence, 1.0),
                parsed_at=datetime.now().strftime('%Y-%m-%d')
            )
            
        except Exception as e:
            logger.error(f"Erro ao normalizar vaga: {e}")
            return self.create_default_job(row)

    def create_default_job(self, row: pd.Series) -> JobData:
        """Cria uma vaga padrão em caso de erro"""
        return JobData(
            title=str(row.get('Título', 'Vaga sem título')),
            seniority=Seniority.NAO_ESPECIFICADO.value,
            area="",
            company_name="",
            industry="",
            employment_type=EmploymentType.CLT.value,
            work_schedule="Não especificado",
            modality=Modality.PRESENCIAL.value,
            location_city="",
            location_state="",
            location_region="",
            salary_min=None,
            salary_max=None,
            salary_currency="BRL",
            salary_period="month",
            benefits=[],
            rewards=[],
            requirements_must=[],
            requirements_nice=[],
            education_level="Não especificado",
            responsibilities=[],
            pcd=False,
            tags=[],
            source_name=str(row.get('Título', '')),
            source_url=str(row.get('URL', '')),
            raw_excerpt=str(row.get('Setor', '')),
            confidence=0.1,
            parsed_at=datetime.now().strftime('%Y-%m-%d')
        )

    def remove_duplicates(self, jobs: List[JobData]) -> List[JobData]:
        """Remove vagas duplicadas baseado em hash do conteúdo"""
        seen_hashes = set()
        unique_jobs = []
        
        for job in jobs:
            # Cria hash baseado em título, empresa e localização
            content = f"{job.title}_{job.company_name}_{job.location_city}"
            job_hash = hashlib.md5(content.encode()).hexdigest()
            
            if job_hash not in seen_hashes:
                seen_hashes.add(job_hash)
                unique_jobs.append(job)
        
        return unique_jobs

    def generate_statistics(self, jobs: List[JobData]) -> None:
        """Gera estatísticas dos dados processados"""
        logger.info("\n📊 ESTATÍSTICAS DOS DADOS PROCESSADOS")
        logger.info("=" * 50)
        logger.info(f"📈 Total de vagas: {len(jobs)}")
        
        # Estatísticas de modalidade
        modalities = Counter([job.modality for job in jobs])
        logger.info("\n📊 Top 10 Modalidade:")
        for modality, count in modalities.most_common(10):
            percentage = (count / len(jobs)) * 100
            logger.info(f"   {modality}: {count} ({percentage:.1f}%)")
        
        # Estatísticas de empresas
        companies = Counter([job.company_name for job in jobs if job.company_name])
        logger.info("\n📊 Top 10 Empresas:")
        for company, count in companies.most_common(10):
            percentage = (count / len(jobs)) * 100
            logger.info(f"   {company}: {count} ({percentage:.1f}%)")
        
        # Estatísticas de tags
        all_tags = []
        for job in jobs:
            all_tags.extend(job.tags)
        tags_counter = Counter(all_tags)
        
        logger.info("\n🏷️ Top 15 Tags:")
        for tag, count in tags_counter.most_common(15):
            percentage = (count / len(jobs)) * 100
            logger.info(f"   {tag}: {count} ({percentage:.1f}%)")

    def process_csv(self, csv_path: str) -> None:
        """Processa arquivo CSV e gera JSON normalizado"""
        try:
            logger.info(f"📂 Carregando dados de {csv_path}")
            df = pd.read_csv(csv_path, encoding='utf-8')
            logger.info(f"✅ {len(df)} vagas carregadas")
            
            # Processar vagas
            jobs = []
            for i, (idx, row) in enumerate(df.iterrows()):
                if (i + 1) % 5000 == 0:
                    logger.info(f"🔄 Processadas {i + 1} vagas...")
                
                job = self.normalize_job(row)
                jobs.append(job)
            
            logger.info(f"✅ Total de vagas processadas: {len(jobs)}")
            
            # Remover duplicatas
            unique_jobs = self.remove_duplicates(jobs)
            logger.info(f"🔄 Vagas após remoção de duplicatas: {len(unique_jobs)}")
            
            # Gerar estatísticas
            self.generate_statistics(unique_jobs)
            
            # Salvar JSON
            output_file = 'vagas_normalizadas_avancado.json'
            logger.info(f"💾 Salvando {len(unique_jobs)} vagas em {output_file}")
            
            jobs_dict = [asdict(job) for job in unique_jobs]
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(jobs_dict, f, ensure_ascii=False, indent=2)
            
            logger.info("✅ Dados salvos com sucesso!")
            logger.info("\n🎉 Processo concluído com sucesso!")
            logger.info(f"📁 Arquivo gerado: {output_file}")
            logger.info(f"📊 Total de vagas normalizadas: {len(unique_jobs)}")
            
        except Exception as e:
            logger.error(f"❌ Erro durante o processamento: {e}")
            raise

def main():
    normalizer = AdvancedVagasNormalizer()
    normalizer.process_csv('vagas_todos_setores_1_pagina.csv')

if __name__ == "__main__":
    main()