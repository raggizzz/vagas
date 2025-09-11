#!/usr/bin/env python3
"""
Processador de Skills de Vagas v4

Processa arquivo JSONL com descrições de vagas e gera estatísticas de skills por setor.
Usa taxonomias CSV para normalização e mapeamento.

Uso:
    python tag_skills_v4.py vagas.jsonl
    python tag_skills_v4.py vagas.jsonl --skills-csv skills_taxonomy.csv --sector-csv sector_map.csv
    python tag_skills_v4.py vagas.jsonl --workers 4 --chunksize 1000
    python tag_skills_v4.py vagas.jsonl --make-template
"""

import json
import csv
import re
import argparse
import unicodedata
from pathlib import Path
from collections import defaultdict, Counter
from multiprocessing import Pool, cpu_count
from typing import Dict, List, Set, Tuple, Optional, Any
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TextCleaner:
    """Classe para limpeza e normalização de texto"""
    
    def __init__(self):
        # Padrões para remoção
        self.noise_patterns = [
            r'https?://[^\s]+',  # URLs
            r'www\.[^\s]+',      # WWW links
            r'mostrar menos',
            r'compartilhar',
            r'clique aqui',
            r'saiba mais',
            r'entre em contato',
            r'envie seu currículo',
            r'cadastre-se',
            r'inscreva-se',
        ]
        
        # Seções a ignorar
        self.ignore_sections = [
            'benefícios', 'beneficios', 'benefits',
            'horário', 'horario', 'schedule',
            'local', 'localização', 'location',
            'salário', 'salario', 'salary', 'remuneração', 'remuneracao',
            'quem somos', 'sobre a empresa', 'about us',
            'contato', 'contact',
            'como se candidatar', 'how to apply'
        ]
        
        # Consultorias conhecidas para remoção
        self.consultancy_patterns = [
            r'catho\s*online',
            r'vagas\.com',
            r'indeed',
            r'linkedin',
            r'glassdoor',
            r'infojobs',
            r'trabalha brasil',
            r'sine',
        ]
    
    def normalize_text(self, text: str) -> str:
        """Normaliza texto: minúsculas, remove acentos, limpa caracteres especiais"""
        if not text:
            return ""
        
        # Converter para minúsculas
        text = text.lower()
        
        # Remover acentos
        text = unicodedata.normalize('NFD', text)
        text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
        
        # Trocar | por quebras de linha
        text = text.replace('|', '\n')
        
        # Limpar caracteres especiais, manter apenas letras, números, espaços e quebras
        text = re.sub(r'[^a-z0-9\s\n]', ' ', text)
        
        # Normalizar espaços
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n+', '\n', text)
        
        return text.strip()
    
    def remove_noise(self, text: str) -> str:
        """Remove ruídos do texto"""
        if not text:
            return ""
        
        # Remover padrões de ruído
        for pattern in self.noise_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        # Remover consultorias
        for pattern in self.consultancy_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        return text
    
    def extract_relevant_sections(self, text: str) -> str:
        """Extrai seções relevantes do texto"""
        if not text:
            return ""
        
        # Seções prioritárias
        priority_sections = [
            'requisitos', 'requirements',
            'atividades', 'activities',
            'atribuições', 'atribuicoes',
            'responsabilidades', 'responsibilities',
            'qualificações', 'qualificacoes', 'qualifications',
            'competências', 'competencias', 'skills',
            'habilidades', 'abilities',
            'experiência', 'experiencia', 'experience',
            'conhecimentos', 'knowledge'
        ]
        
        lines = text.split('\n')
        relevant_lines = []
        current_section_relevant = False
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Verificar se é início de seção relevante
            line_lower = line.lower()
            if any(section in line_lower for section in priority_sections):
                current_section_relevant = True
                relevant_lines.append(line)
                continue
            
            # Verificar se é início de seção a ignorar
            if any(ignore in line_lower for ignore in self.ignore_sections):
                current_section_relevant = False
                continue
            
            # Se estamos em seção relevante, adicionar linha
            if current_section_relevant:
                relevant_lines.append(line)
            # Se não estamos em seção específica, adicionar se parece relevante
            elif len(line) > 20 and not any(ignore in line_lower for ignore in self.ignore_sections):
                relevant_lines.append(line)
        
        return '\n'.join(relevant_lines)
    
    def clean_text(self, text: str) -> str:
        """Pipeline completo de limpeza"""
        if not text:
            return ""
        
        # 1. Remover ruídos
        text = self.remove_noise(text)
        
        # 2. Extrair seções relevantes
        text = self.extract_relevant_sections(text)
        
        # 3. Normalizar
        text = self.normalize_text(text)
        
        return text

class SkillsMapper:
    """Classe para mapeamento de skills usando taxonomia"""
    
    def __init__(self, skills_csv_path: Optional[str] = None):
        self.skills_taxonomy = defaultdict(dict)  # {sector: {skill: [aliases]}}
        self.all_skills = set()
        
        if skills_csv_path and Path(skills_csv_path).exists():
            self.load_skills_taxonomy(skills_csv_path)
    
    def load_skills_taxonomy(self, csv_path: str):
        """Carrega taxonomia de skills do CSV"""
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    sector = row['sector'].strip()
                    skill = row['skill'].strip()
                    alias = row['alias'].strip().lower()
                    
                    if sector not in self.skills_taxonomy:
                        self.skills_taxonomy[sector] = defaultdict(list)
                    
                    self.skills_taxonomy[sector][skill].append(alias)
                    self.all_skills.add(skill)
            
            logger.info(f"Carregada taxonomia com {len(self.all_skills)} skills para {len(self.skills_taxonomy)} setores")
        except Exception as e:
            logger.error(f"Erro ao carregar taxonomia de skills: {e}")
    
    def find_skills(self, text: str, sector: str) -> List[str]:
        """Encontra skills no texto para um setor específico"""
        if not text or sector not in self.skills_taxonomy:
            return []
        
        text_lower = text.lower()
        found_skills = []
        
        for skill, aliases in self.skills_taxonomy[sector].items():
            for alias in aliases:
                if alias in text_lower:
                    found_skills.append(skill)
                    break  # Encontrou pelo menos um alias, não precisa verificar outros
        
        return list(set(found_skills))  # Remove duplicatas

class SectorResolver:
    """Classe para resolução e normalização de setores"""
    
    def __init__(self, sector_csv_path: Optional[str] = None):
        self.sector_map = {}  # {raw_sector: normalized_sector}
        self.sector_aliases = defaultdict(list)  # {normalized_sector: [aliases]}
        
        if sector_csv_path and Path(sector_csv_path).exists():
            self.load_sector_map(sector_csv_path)
    
    def load_sector_map(self, csv_path: str):
        """Carrega mapeamento de setores do CSV"""
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    raw_sector = row['raw_sector'].strip()
                    normalized_sector = row['normalized_sector'].strip()
                    alias = row['alias'].strip().lower()
                    
                    self.sector_map[raw_sector] = normalized_sector
                    self.sector_aliases[normalized_sector].append(alias)
            
            logger.info(f"Carregado mapeamento para {len(self.sector_map)} setores")
        except Exception as e:
            logger.error(f"Erro ao carregar mapeamento de setores: {e}")
    
    def resolve_sector(self, vaga_data: Dict) -> str:
        """Resolve o setor da vaga"""
        # Tentar pegar do campo setor
        sector = None
        try:
            sector = vaga_data.get('informacoes_basicas', {}).get('setor', '')
        except:
            pass
        
        if sector and sector.strip():
            # Normalizar usando mapa se disponível
            sector = sector.strip()
            if sector in self.sector_map:
                return self.sector_map[sector]
            return sector
        
        # Inferir por palavras-chave no texto
        text_parts = []
        try:
            # Coletar texto relevante
            info_basicas = vaga_data.get('informacoes_basicas', {})
            text_parts.append(str(info_basicas.get('titulo', '')))
            text_parts.append(str(info_basicas.get('empresa_principal', '')))
            
            desc_completa = vaga_data.get('descricao_completa', {})
            text_parts.append(str(desc_completa.get('texto_completo', '')))
            
            requisitos = vaga_data.get('requisitos', {})
            text_parts.append(str(requisitos.get('requisitos_texto_original', '')))
        except:
            pass
        
        full_text = ' '.join(text_parts).lower()
        
        # Buscar por aliases de setores
        for normalized_sector, aliases in self.sector_aliases.items():
            for alias in aliases:
                if alias in full_text:
                    return normalized_sector
        
        return 'Outros'

class VagaProcessor:
    """Processador principal de vagas"""
    
    def __init__(self, skills_csv: Optional[str] = None, sector_csv: Optional[str] = None):
        self.text_cleaner = TextCleaner()
        self.skills_mapper = SkillsMapper(skills_csv)
        self.sector_resolver = SectorResolver(sector_csv)
        self.stats = defaultdict(lambda: defaultdict(int))  # {sector: {skill: count}}
        self.sector_totals = defaultdict(int)  # {sector: total_vagas}
    
    def extract_text_from_vaga(self, vaga_data: Dict) -> str:
        """Extrai todo o texto útil da vaga"""
        text_parts = []
        
        try:
            # Descrição completa
            desc_completa = vaga_data.get('descricao_completa', {})
            if desc_completa.get('texto_completo'):
                text_parts.append(desc_completa['texto_completo'])
            
            # Segmentos separados
            if desc_completa.get('segmentos_separados'):
                for segmento in desc_completa['segmentos_separados']:
                    if isinstance(segmento, str):
                        text_parts.append(segmento)
            
            # Requisitos
            requisitos = vaga_data.get('requisitos', {})
            if requisitos.get('requisitos_texto_original'):
                text_parts.append(requisitos['requisitos_texto_original'])
            
            # Responsabilidades
            responsabilidades = vaga_data.get('responsabilidades', {})
            if responsabilidades.get('lista_responsabilidades'):
                for resp in responsabilidades['lista_responsabilidades']:
                    if isinstance(resp, str):
                        text_parts.append(resp)
            
            # Habilidades e competências
            habilidades = vaga_data.get('habilidades_e_competencias', {})
            for key, value in habilidades.items():
                if isinstance(value, str):
                    text_parts.append(value)
                elif isinstance(value, list):
                    text_parts.extend([str(v) for v in value if v])
        
        except Exception as e:
            logger.warning(f"Erro ao extrair texto da vaga: {e}")
        
        return ' '.join(text_parts)
    
    def process_vaga(self, vaga_data: Dict) -> Dict:
        """Processa uma vaga individual"""
        try:
            # Extrair texto
            raw_text = self.extract_text_from_vaga(vaga_data)
            
            # Limpar texto
            clean_text = self.text_cleaner.clean_text(raw_text)
            
            # Resolver setor
            sector = self.sector_resolver.resolve_sector(vaga_data)
            
            # Mapear skills
            skills = self.skills_mapper.find_skills(clean_text, sector)
            
            # Atualizar estatísticas
            self.sector_totals[sector] += 1
            for skill in skills:
                self.stats[sector][skill] += 1
            
            # Retornar vaga processada
            result = vaga_data.copy()
            result['setor_resolvido'] = sector
            result['skills_mapeadas'] = skills
            
            return result
        
        except Exception as e:
            logger.warning(f"Erro ao processar vaga: {e}")
            return None

def process_chunk(args):
    """Processa um chunk de vagas (para multiprocessing)"""
    lines, skills_csv, sector_csv = args
    processor = VagaProcessor(skills_csv, sector_csv)
    results = []
    
    for line in lines:
        try:
            vaga_data = json.loads(line.strip())
            processed = processor.process_vaga(vaga_data)
            if processed:
                results.append(processed)
        except json.JSONDecodeError:
            continue
        except Exception as e:
            logger.warning(f"Erro ao processar linha: {e}")
            continue
    
    return results, processor.stats, processor.sector_totals

def create_templates(input_file: str):
    """Cria templates de CSV baseados nos dados do arquivo"""
    logger.info("Criando templates...")
    
    sectors_found = set()
    skills_found = defaultdict(set)
    
    # Ler arquivo para encontrar setores e possíveis skills
    with open(input_file, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            if line_num % 1000 == 0:
                logger.info(f"Processando linha {line_num} para template...")
            
            try:
                vaga_data = json.loads(line.strip())
                
                # Extrair setor
                sector = vaga_data.get('informacoes_basicas', {}).get('setor', 'Outros')
                if sector:
                    sectors_found.add(sector.strip())
                
                # Extrair possíveis skills do texto
                processor = VagaProcessor()
                text = processor.extract_text_from_vaga(vaga_data)
                clean_text = processor.text_cleaner.clean_text(text)
                
                # Palavras que podem ser skills (heurística simples)
                words = clean_text.split()
                for word in words:
                    if len(word) > 3 and word.isalpha():
                        skills_found[sector].add(word)
            
            except:
                continue
    
    # Criar sector_map_template.csv
    with open('sector_map_template.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['raw_sector', 'normalized_sector', 'alias'])
        
        for sector in sorted(sectors_found):
            normalized = sector.replace('/', '_').replace(' ', '_')
            alias = sector.lower()
            writer.writerow([sector, normalized, alias])
    
    # Criar skills_taxonomy_template.csv
    with open('skills_taxonomy_template.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['sector', 'skill', 'alias'])
        
        for sector in sorted(sectors_found):
            # Adicionar algumas skills comuns como exemplo
            common_skills = ['comunicacao', 'excel', 'word', 'powerpoint', 'ingles', 'espanhol']
            for skill in common_skills:
                writer.writerow([sector, skill, skill])
    
    logger.info("Templates criados: sector_map_template.csv e skills_taxonomy_template.csv")

def main():
    parser = argparse.ArgumentParser(description='Processador de Skills de Vagas v4')
    parser.add_argument('input_file', help='Arquivo JSONL de entrada')
    parser.add_argument('--skills-csv', help='Arquivo CSV com taxonomia de skills')
    parser.add_argument('--sector-csv', help='Arquivo CSV com mapeamento de setores')
    parser.add_argument('--workers', type=int, default=1, help='Número de workers para processamento paralelo')
    parser.add_argument('--chunksize', type=int, default=1000, help='Tamanho do chunk para processamento')
    parser.add_argument('--make-template', action='store_true', help='Criar templates de CSV')
    
    args = parser.parse_args()
    
    if args.make_template:
        create_templates(args.input_file)
        return
    
    logger.info(f"Iniciando processamento de {args.input_file}")
    
    # Ler arquivo e processar
    all_stats = defaultdict(lambda: defaultdict(int))
    all_sector_totals = defaultdict(int)
    processed_vagas = []
    
    if args.workers > 1:
        # Processamento paralelo
        logger.info(f"Usando {args.workers} workers")
        
        # Ler arquivo em chunks
        chunks = []
        current_chunk = []
        
        with open(args.input_file, 'r', encoding='utf-8') as f:
            for line in f:
                current_chunk.append(line)
                if len(current_chunk) >= args.chunksize:
                    chunks.append((current_chunk, args.skills_csv, args.sector_csv))
                    current_chunk = []
        
        if current_chunk:
            chunks.append((current_chunk, args.skills_csv, args.sector_csv))
        
        # Processar chunks em paralelo
        with Pool(args.workers) as pool:
            results = pool.map(process_chunk, chunks)
        
        # Consolidar resultados
        for chunk_results, chunk_stats, chunk_totals in results:
            processed_vagas.extend(chunk_results)
            
            for sector, skills in chunk_stats.items():
                for skill, count in skills.items():
                    all_stats[sector][skill] += count
            
            for sector, total in chunk_totals.items():
                all_sector_totals[sector] += total
    
    else:
        # Processamento sequencial
        processor = VagaProcessor(args.skills_csv, args.sector_csv)
        
        with open(args.input_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                if line_num % 1000 == 0:
                    logger.info(f"Processadas {line_num} linhas")
                
                try:
                    vaga_data = json.loads(line.strip())
                    processed = processor.process_vaga(vaga_data)
                    if processed:
                        processed_vagas.append(processed)
                except:
                    continue
        
        all_stats = processor.stats
        all_sector_totals = processor.sector_totals
    
    # Gerar arquivos de saída
    logger.info("Gerando arquivos de saída...")
    
    # 1. vagas_tagged.jsonl
    with open('vagas_tagged.jsonl', 'w', encoding='utf-8') as f:
        for vaga in processed_vagas:
            f.write(json.dumps(vaga, ensure_ascii=False) + '\n')
    
    # 2. skills_agg.csv
    with open('skills_agg.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['setor', 'skill', 'contagem', 'total_setor', 'percentual'])
        
        for sector in sorted(all_stats.keys()):
            total_sector = all_sector_totals[sector]
            for skill, count in sorted(all_stats[sector].items()):
                percentage = (count / total_sector * 100) if total_sector > 0 else 0
                writer.writerow([sector, skill, count, total_sector, f"{percentage:.2f}%"])
    
    # 3. coverage_report.csv
    with open('coverage_report.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['setor', 'total_vagas', 'skills_encontradas', 'top3_skills'])
        
        for sector in sorted(all_sector_totals.keys()):
            total_vagas = all_sector_totals[sector]
            skills_count = len(all_stats[sector])
            
            # Top 3 skills
            top_skills = sorted(all_stats[sector].items(), key=lambda x: x[1], reverse=True)[:3]
            top3_str = ', '.join([f"{skill}({count})" for skill, count in top_skills])
            
            writer.writerow([sector, total_vagas, skills_count, top3_str])
    
    logger.info(f"Processamento concluído!")
    logger.info(f"Vagas processadas: {len(processed_vagas)}")
    logger.info(f"Setores encontrados: {len(all_sector_totals)}")
    logger.info(f"Arquivos gerados: vagas_tagged.jsonl, skills_agg.csv, coverage_report.csv")

if __name__ == '__main__':
    main()