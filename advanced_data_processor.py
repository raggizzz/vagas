#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pipeline Avançado de Processamento de Dados de Vagas
Implementa: (1) Limpeza/Split, (2) Extração com Regras, (3) Normalização
"""

import pandas as pd
import json
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AdvancedJobProcessor:
    def __init__(self):
        # Dicionários de normalização
        self.seniority_mapping = {
            'junior': 'Júnior', 'jr': 'Júnior', 'iniciante': 'Júnior', 'trainee': 'Júnior',
            'pleno': 'Pleno', 'mid': 'Pleno', 'intermediário': 'Pleno', 'intermediario': 'Pleno',
            'senior': 'Sênior', 'sr': 'Sênior', 'experiente': 'Sênior', 'especialista': 'Sênior'
        }
        
        self.employment_type_mapping = {
            'clt': 'CLT', 'efetivo': 'CLT', 'carteira assinada': 'CLT',
            'pj': 'PJ', 'pessoa jurídica': 'PJ', 'pessoa juridica': 'PJ',
            'freelancer': 'Freelancer', 'autônomo': 'Freelancer', 'autonomo': 'Freelancer',
            'estágio': 'Estágio', 'estagio': 'Estágio', 'trainee': 'Trainee',
            'temporário': 'Temporário', 'temporario': 'Temporário'
        }
        
        self.modality_mapping = {
            'presencial': 'Presencial', 'on-site': 'Presencial',
            'remoto': 'Remoto', 'remote': 'Remoto', 'home office': 'Remoto',
            'híbrido': 'Híbrido', 'hibrido': 'Híbrido', 'hybrid': 'Híbrido'
        }
        
        self.education_mapping = {
            'fundamental': 'Fundamental', 'ensino fundamental': 'Fundamental',
            'médio': 'Médio/Técnico', 'medio': 'Médio/Técnico', 'ensino médio': 'Médio/Técnico',
            'técnico': 'Médio/Técnico', 'tecnico': 'Médio/Técnico',
            'superior': 'Superior', 'graduação': 'Superior', 'graduacao': 'Superior',
            'pós': 'Pós-graduação', 'pos': 'Pós-graduação', 'mestrado': 'Pós-graduação',
            'doutorado': 'Pós-graduação', 'mba': 'Pós-graduação'
        }
        
        # Padrões regex para extração
        self.salary_patterns = [
            r'R\$\s*([\d.,]+)\s*(?:a|até)\s*R\$\s*([\d.,]+)',
            r'De\s*R\$\s*([\d.,]+)\s*a\s*R\$\s*([\d.,]+)',
            r'R\$\s*([\d.,]+)',
            r'([\d.,]+)\s*(?:reais?|R\$)',
            r'Salário:\s*R\$\s*([\d.,]+)'
        ]
        
        self.benefit_patterns = [
            r'Vale\s+(\w+)(?:\s*R\$\s*([\d.,]+))?',
            r'(Seguro\s+de\s+Vida)',
            r'(Plano\s+de\s+Saúde)',
            r'(Plano\s+Odontológico)',
            r'(Auxílio\s+\w+)',
            r'(Participação\s+nos\s+Lucros)',
            r'(13º\s+salário)',
            r'(Férias\s+remuneradas)'
        ]

    def clean_and_split_text(self, text: str) -> Dict[str, str]:
        """Etapa 1: Limpeza e divisão do texto em seções"""
        if pd.isna(text) or not text:
            return {}
            
        # Limpar texto
        text = str(text).strip()
        text = re.sub(r'\s+', ' ', text)  # Normalizar espaços
        text = re.sub(r'[\r\n]+', ' ', text)  # Remover quebras de linha
        
        # Dividir em seções baseado em palavras-chave
        sections = {
            'header': '',
            'description': '',
            'requirements': '',
            'benefits': '',
            'company': '',
            'location': '',
            'salary': ''
        }
        
        # Identificar seções por palavras-chave
        text_lower = text.lower()
        
        # Extrair cabeçalho (primeiras linhas)
        lines = text.split('.')
        if lines:
            sections['header'] = lines[0].strip()
        
        # Buscar seções específicas
        if 'requisitos' in text_lower or 'exigências' in text_lower:
            req_match = re.search(r'(requisitos?|exigências?)([^.]*(?:\.[^.]*){0,3})', text_lower)
            if req_match:
                sections['requirements'] = req_match.group(2).strip()
        
        if 'benefícios' in text_lower or 'oferecemos' in text_lower:
            ben_match = re.search(r'(benefícios?|oferecemos)([^.]*(?:\.[^.]*){0,3})', text_lower)
            if ben_match:
                sections['benefits'] = ben_match.group(2).strip()
        
        # Resto como descrição
        sections['description'] = text
        
        return sections

    def extract_structured_fields(self, sections: Dict[str, str], raw_data: Dict) -> Dict[str, Any]:
        """Etapa 2: Extração estruturada de campos com regras claras"""
        extracted = {
            'title': self._extract_title(sections, raw_data),
            'seniority': self._extract_seniority(sections),
            'area': self._extract_area(sections),
            'company_name': self._extract_company(sections, raw_data),
            'industry': self._extract_industry(sections),
            'employment_type': self._extract_employment_type(sections),
            'work_schedule': self._extract_work_schedule(sections),
            'modality': self._extract_modality(sections),
            'location_city': self._extract_location_city(sections, raw_data),
            'location_state': self._extract_location_state(sections, raw_data),
            'location_region': self._extract_location_region(sections),
            'salary_min': None,
            'salary_max': None,
            'salary_currency': 'BRL',
            'salary_period': 'month',
            'benefits': self._extract_benefits(sections),
            'rewards': self._extract_rewards(sections),
            'requirements_must': self._extract_requirements_must(sections),
            'requirements_nice': self._extract_requirements_nice(sections),
            'education_level': self._extract_education_level(sections),
            'responsibilities': self._extract_responsibilities(sections),
            'pcd': self._extract_pcd(sections),
            'tags': self._extract_tags(sections),
            'source_name': 'Catho',
            'source_url': raw_data.get('link', ''),
            'raw_excerpt': self._create_raw_excerpt(sections, raw_data),
            'confidence': self._calculate_confidence(sections),
            'parsed_at': datetime.now().strftime('%Y-%m-%d')
        }
        
        # Extrair salário
        salary_min, salary_max = self._extract_salary(sections)
        extracted['salary_min'] = salary_min
        extracted['salary_max'] = salary_max
        
        return extracted

    def _extract_title(self, sections: Dict[str, str], raw_data: Dict) -> str:
        """Extrair título da vaga"""
        if 'titulo' in raw_data and raw_data['titulo']:
            return str(raw_data['titulo']).strip()
        
        header = sections.get('header', '')
        if header:
            # Limpar título
            title = re.sub(r'^(vaga|emprego|oportunidade)\s*:?\s*', '', header, flags=re.IGNORECASE)
            return title.strip()
        
        return 'Não informado'

    def _extract_seniority(self, sections: Dict[str, str]) -> str:
        """Extrair nível de senioridade"""
        text = ' '.join(sections.values()).lower()
        
        for key, value in self.seniority_mapping.items():
            if key in text:
                return value
        
        # Inferir por palavras-chave
        if any(word in text for word in ['iniciante', 'sem experiência', 'primeiro emprego']):
            return 'Júnior'
        elif any(word in text for word in ['experiência', 'anos de', 'conhecimento']):
            return 'Pleno'
        
        return 'Não informado'

    def _extract_area(self, sections: Dict[str, str]) -> str:
        """Extrair área de atuação"""
        text = ' '.join(sections.values()).lower()
        
        areas = {
            'manutenção': ['manutenção', 'manutenção predial', 'facilities'],
            'produção': ['produção', 'operação', 'fábrica'],
            'qualidade': ['qualidade', 'controle de qualidade'],
            'logística': ['logística', 'almoxarifado', 'estoque'],
            'vendas': ['vendas', 'comercial', 'atendimento'],
            'administrativo': ['administrativo', 'escritório', 'gestão']
        }
        
        for area, keywords in areas.items():
            if any(keyword in text for keyword in keywords):
                return area.title()
        
        return 'Geral'

    def _extract_company(self, sections: Dict[str, str], raw_data: Dict) -> str:
        """Extrair nome da empresa"""
        if 'empresa' in raw_data and raw_data['empresa']:
            company = str(raw_data['empresa']).strip()
            if company.lower() not in ['confidencial', 'não informado', '']:
                return company
        
        text = ' '.join(sections.values())
        company_match = re.search(r'empresa:?\s*([^\n.]+)', text, re.IGNORECASE)
        if company_match:
            return company_match.group(1).strip()
        
        return 'Confidencial'

    def _extract_industry(self, sections: Dict[str, str]) -> str:
        """Extrair setor/indústria"""
        text = ' '.join(sections.values()).lower()
        
        industries = {
            'industrial': ['industrial', 'fábrica', 'manufatura', 'produção'],
            'serviços': ['serviços', 'prestadora', 'consultoria'],
            'tecnologia': ['tecnologia', 'software', 'ti', 'desenvolvimento'],
            'saúde': ['saúde', 'hospital', 'clínica', 'médico'],
            'educação': ['educação', 'escola', 'universidade', 'ensino']
        }
        
        for industry, keywords in industries.items():
            if any(keyword in text for keyword in keywords):
                return industry.title()
        
        return 'Não informado'

    def _extract_employment_type(self, sections: Dict[str, str]) -> str:
        """Extrair tipo de contratação"""
        text = ' '.join(sections.values()).lower()
        
        for key, value in self.employment_type_mapping.items():
            if key in text:
                return value
        
        return 'CLT'  # Padrão

    def _extract_work_schedule(self, sections: Dict[str, str]) -> Optional[str]:
        """Extrair horário de trabalho"""
        text = ' '.join(sections.values())
        
        schedule_patterns = [
            r'(\d{1,2}h\s*às?\s*\d{1,2}h)',
            r'(\d{1,2}:\d{2}\s*às?\s*\d{1,2}:\d{2})',
            r'(segunda\s*a\s*sexta[^.]*)',
            r'(horário[^.]*)',
        ]
        
        for pattern in schedule_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None

    def _extract_modality(self, sections: Dict[str, str]) -> str:
        """Extrair modalidade de trabalho"""
        text = ' '.join(sections.values()).lower()
        
        for key, value in self.modality_mapping.items():
            if key in text:
                return value
        
        return 'Presencial'  # Padrão

    def _extract_location_city(self, sections: Dict[str, str], raw_data: Dict) -> str:
        """Extrair cidade"""
        if 'localizacao' in raw_data and raw_data['localizacao']:
            location = str(raw_data['localizacao'])
            city_match = re.search(r'([^,/]+)', location)
            if city_match:
                return city_match.group(1).strip()
        
        text = ' '.join(sections.values())
        cities = ['brasília', 'são paulo', 'rio de janeiro', 'belo horizonte', 'salvador']
        
        for city in cities:
            if city in text.lower():
                return city.title()
        
        return 'Não informado'

    def _extract_location_state(self, sections: Dict[str, str], raw_data: Dict) -> str:
        """Extrair estado"""
        if 'localizacao' in raw_data and raw_data['localizacao']:
            location = str(raw_data['localizacao'])
            state_match = re.search(r'/([A-Z]{2})', location)
            if state_match:
                return state_match.group(1)
        
        text = ' '.join(sections.values()).upper()
        states = ['DF', 'SP', 'RJ', 'MG', 'BA', 'PR', 'RS', 'SC']
        
        for state in states:
            if state in text:
                return state
        
        return 'Não informado'

    def _extract_location_region(self, sections: Dict[str, str]) -> Optional[str]:
        """Extrair região/bairro"""
        text = ' '.join(sections.values())
        
        region_patterns = [
            r'(asa\s+sul|asa\s+norte)',
            r'(centro|downtown)',
            r'(zona\s+\w+)',
            r'(bairro\s+[^,\n.]+)'
        ]
        
        for pattern in region_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip().title()
        
        return None

    def _extract_salary(self, sections: Dict[str, str]) -> Tuple[Optional[float], Optional[float]]:
        """Extrair faixa salarial"""
        text = ' '.join(sections.values())
        
        for pattern in self.salary_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if len(match.groups()) == 2:  # Faixa salarial
                    min_sal = self._parse_salary_value(match.group(1))
                    max_sal = self._parse_salary_value(match.group(2))
                    return min_sal, max_sal
                else:  # Salário único
                    salary = self._parse_salary_value(match.group(1))
                    return salary, salary
        
        return None, None

    def _parse_salary_value(self, value: str) -> Optional[float]:
        """Converter string de salário para float"""
        try:
            # Remover caracteres não numéricos exceto vírgula e ponto
            clean_value = re.sub(r'[^\d.,]', '', value)
            # Tratar vírgula como separador decimal
            clean_value = clean_value.replace('.', '').replace(',', '.')
            return float(clean_value)
        except:
            return None

    def _extract_benefits(self, sections: Dict[str, str]) -> List[str]:
        """Extrair benefícios"""
        text = ' '.join(sections.values())
        benefits = []
        
        for pattern in self.benefit_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                if len(match.groups()) == 2 and match.group(2):  # Com valor
                    benefit = f"{match.group(1)} (R$ {match.group(2)})"
                else:
                    benefit = match.group(1)
                
                if benefit not in benefits:
                    benefits.append(benefit)
        
        return benefits

    def _extract_rewards(self, sections: Dict[str, str]) -> List[str]:
        """Extrair recompensas/bonificações"""
        text = ' '.join(sections.values())
        rewards = []
        
        reward_patterns = [
            r'(prêmio\s+[^,\n.]+)',
            r'(bonificação\s+[^,\n.]+)',
            r'(participação\s+nos\s+lucros)',
            r'(plr)',
            r'(day\s+off\s+[^,\n.]+)',
            r'(plano\s+de\s+carreira)'
        ]
        
        for pattern in reward_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                reward = match.group(1).strip()
                if reward not in rewards:
                    rewards.append(reward)
        
        return rewards

    def _extract_requirements_must(self, sections: Dict[str, str]) -> List[str]:
        """Extrair requisitos obrigatórios"""
        req_text = sections.get('requirements', '') + ' ' + sections.get('description', '')
        requirements = []
        
        req_patterns = [
            r'ensino\s+(\w+)\s+completo',
            r'curso\s+([^,\n.]+)',
            r'experiência\s+([^,\n.]+)',
            r'conhecimento\s+([^,\n.]+)',
            r'certificado\s+([^,\n.]+)'
        ]
        
        for pattern in req_patterns:
            matches = re.finditer(pattern, req_text, re.IGNORECASE)
            for match in matches:
                req = match.group(0).strip()
                if req not in requirements:
                    requirements.append(req)
        
        return requirements

    def _extract_requirements_nice(self, sections: Dict[str, str]) -> List[str]:
        """Extrair requisitos desejáveis"""
        text = ' '.join(sections.values())
        nice_requirements = []
        
        nice_patterns = [
            r'desejável\s+([^,\n.]+)',
            r'diferencial\s+([^,\n.]+)',
            r'será\s+um\s+plus\s+([^,\n.]+)'
        ]
        
        for pattern in nice_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                req = match.group(1).strip()
                if req not in nice_requirements:
                    nice_requirements.append(req)
        
        return nice_requirements

    def _extract_education_level(self, sections: Dict[str, str]) -> str:
        """Extrair nível de escolaridade"""
        text = ' '.join(sections.values()).lower()
        
        for key, value in self.education_mapping.items():
            if key in text:
                return value
        
        return 'Não informado'

    def _extract_responsibilities(self, sections: Dict[str, str]) -> List[str]:
        """Extrair responsabilidades"""
        desc_text = sections.get('description', '')
        responsibilities = []
        
        resp_patterns = [
            r'realizar\s+([^,\n.]+)',
            r'executar\s+([^,\n.]+)',
            r'elaborar\s+([^,\n.]+)',
            r'responsável\s+por\s+([^,\n.]+)'
        ]
        
        for pattern in resp_patterns:
            matches = re.finditer(pattern, desc_text, re.IGNORECASE)
            for match in matches:
                resp = match.group(0).strip()
                if resp not in responsibilities:
                    responsibilities.append(resp)
        
        return responsibilities

    def _extract_pcd(self, sections: Dict[str, str]) -> bool:
        """Verificar se é vaga PCD"""
        text = ' '.join(sections.values()).lower()
        pcd_keywords = ['pcd', 'pessoa com deficiência', 'deficiente', 'inclusiva']
        
        return any(keyword in text for keyword in pcd_keywords)

    def _extract_tags(self, sections: Dict[str, str]) -> List[str]:
        """Extrair tags relevantes"""
        text = ' '.join(sections.values()).lower()
        tags = []
        
        tag_keywords = {
            'hidráulica': ['hidráulica', 'hidraulico'],
            'manutenção': ['manutenção', 'manutencao'],
            'chiller': ['chiller', 'resfriador'],
            'predial': ['predial', 'prédio'],
            'elétrica': ['elétrica', 'eletrica', 'eletricista'],
            'mecânica': ['mecânica', 'mecanica', 'mecânico']
        }
        
        for tag, keywords in tag_keywords.items():
            if any(keyword in text for keyword in keywords):
                tags.append(tag)
        
        return tags

    def _create_raw_excerpt(self, sections: Dict[str, str], raw_data: Dict) -> str:
        """Criar excerpt dos dados brutos"""
        parts = []
        
        if 'salario' in raw_data and raw_data['salario']:
            parts.append(f"Salário: {raw_data['salario']}")
        
        if 'localizacao' in raw_data and raw_data['localizacao']:
            parts.append(f"Local: {raw_data['localizacao']}")
        
        # Adicionar primeiras palavras da descrição
        desc = sections.get('description', '')
        if desc:
            words = desc.split()[:10]
            parts.append(' '.join(words) + '...')
        
        return ' | '.join(parts)

    def _calculate_confidence(self, sections: Dict[str, str]) -> float:
        """Calcular confiança da extração"""
        score = 0.5  # Base
        
        # Adicionar pontos por seções preenchidas
        if sections.get('header'):
            score += 0.1
        if sections.get('requirements'):
            score += 0.1
        if sections.get('benefits'):
            score += 0.1
        if len(sections.get('description', '')) > 100:
            score += 0.2
        
        return min(score, 1.0)

    def normalize_values(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Etapa 3: Normalização de valores"""
        normalized = extracted_data.copy()
        
        # Normalizar strings
        string_fields = ['title', 'company_name', 'location_city', 'area']
        for field in string_fields:
            if normalized.get(field):
                normalized[field] = self._normalize_string(normalized[field])
        
        # Normalizar listas
        list_fields = ['benefits', 'rewards', 'requirements_must', 'requirements_nice', 'responsibilities', 'tags']
        for field in list_fields:
            if normalized.get(field):
                normalized[field] = [self._normalize_string(item) for item in normalized[field]]
        
        # Validar e corrigir valores
        normalized = self._validate_and_correct(normalized)
        
        return normalized

    def _normalize_string(self, text: str) -> str:
        """Normalizar string individual"""
        if not text:
            return text
        
        # Capitalizar corretamente
        text = text.strip().title()
        
        # Correções específicas
        corrections = {
            'Clt': 'CLT',
            'Pj': 'PJ',
            'Df': 'DF',
            'Sp': 'SP',
            'Rj': 'RJ',
            'R$': 'R$'
        }
        
        for wrong, correct in corrections.items():
            text = text.replace(wrong, correct)
        
        return text

    def _validate_and_correct(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validar e corrigir dados"""
        # Validar salário
        if data.get('salary_min') and data.get('salary_max'):
            if data['salary_min'] > data['salary_max']:
                data['salary_min'], data['salary_max'] = data['salary_max'], data['salary_min']
        
        # Validar confiança
        if data.get('confidence', 0) > 1.0:
            data['confidence'] = 1.0
        elif data.get('confidence', 0) < 0.0:
            data['confidence'] = 0.0
        
        return data

    def process_csv(self, input_file: str, output_file: str) -> None:
        """Processar CSV completo"""
        logger.info(f"Iniciando processamento de {input_file}")
        
        # Carregar dados
        df = pd.read_csv(input_file)
        logger.info(f"Carregadas {len(df)} vagas")
        
        processed_jobs = []
        
        for idx, row in df.iterrows():
            try:
                # Etapa 1: Limpeza e divisão
                sections = self.clean_and_split_text(row.get('descricao', ''))
                
                # Etapa 2: Extração estruturada
                extracted = self.extract_structured_fields(sections, row.to_dict())
                
                # Etapa 3: Normalização
                normalized = self.normalize_values(extracted)
                
                processed_jobs.append(normalized)
                
                if (idx + 1) % 5 == 0:
                    logger.info(f"Processadas {idx + 1} vagas")
                    
            except Exception as e:
                logger.error(f"Erro ao processar vaga {idx}: {e}")
                continue
        
        # Salvar resultado
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(processed_jobs, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Processamento concluído. {len(processed_jobs)} vagas salvas em {output_file}")
        
        # Gerar estatísticas
        self._generate_stats(processed_jobs)

    def _generate_stats(self, jobs: List[Dict[str, Any]]) -> None:
        """Gerar estatísticas do processamento"""
        total = len(jobs)
        
        # Estatísticas de preenchimento
        with_salary = sum(1 for job in jobs if job.get('salary_min'))
        with_benefits = sum(1 for job in jobs if job.get('benefits'))
        with_requirements = sum(1 for job in jobs if job.get('requirements_must'))
        
        # Estatísticas de qualidade
        avg_confidence = sum(job.get('confidence', 0) for job in jobs) / total if total > 0 else 0
        
        logger.info(f"\n=== ESTATÍSTICAS DO PROCESSAMENTO ===")
        logger.info(f"Total de vagas processadas: {total}")
        logger.info(f"Vagas com salário: {with_salary} ({with_salary/total*100:.1f}%)")
        logger.info(f"Vagas com benefícios: {with_benefits} ({with_benefits/total*100:.1f}%)")
        logger.info(f"Vagas com requisitos: {with_requirements} ({with_requirements/total*100:.1f}%)")
        logger.info(f"Confiança média: {avg_confidence:.2f}")

if __name__ == "__main__":
    processor = AdvancedJobProcessor()
    
    input_file = "vagas_industrial_unico.csv"
    output_file = "vagas_industrial_estruturado_avancado.json"
    
    processor.process_csv(input_file, output_file)
    
    logger.info("Pipeline de processamento avançado concluído!")