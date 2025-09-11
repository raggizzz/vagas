#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para reorganizar completamente o arquivo JSONL com estrutura limpa
"""

import json
import re
from collections import defaultdict
from typing import Dict, List, Any

def clean_text(text: str) -> str:
    """Limpa e normaliza texto"""
    if not text or text == 'nan':
        return ''
    
    # Remove caracteres especiais e normaliza
    text = str(text).strip()
    text = re.sub(r'\s+', ' ', text)  # Remove espaços múltiplos
    text = re.sub(r'[\r\n]+', ' ', text)  # Remove quebras de linha
    
    return text

def extract_company_name(empresa_text: str) -> str:
    """Extrai nome da empresa principal"""
    if not empresa_text or empresa_text == 'nan':
        return ''
    
    # Remove URLs e textos desnecessários
    empresa = clean_text(empresa_text)
    
    # Padrões para limpar
    patterns_to_remove = [
        r'https?://[^\s]+',
        r'Receber [Ee] [Cc]onferir.*',
        r'CANDIDATURA FÁCIL',
        r'Por [Qq]ue\?',
        r'EMPRESA DE.*SKY TEC.*'
    ]
    
    for pattern in patterns_to_remove:
        empresa = re.sub(pattern, '', empresa, flags=re.IGNORECASE)
    
    # Pega apenas a primeira parte antes de vírgulas ou traços
    empresa = empresa.split(',')[0].split('-')[0].strip()
    
    return empresa[:100]  # Limita tamanho

def extract_job_title(titulo_text: str) -> str:
    """Extrai título da vaga"""
    if not titulo_text or titulo_text == 'nan':
        return ''
    
    # Se for URL, extrai o título da URL
    if 'catho.com.br/vagas/' in titulo_text:
        match = re.search(r'/vagas/([^/]+)/', titulo_text)
        if match:
            title = match.group(1).replace('-', ' ').title()
            return clean_text(title)
    
    return clean_text(titulo_text)

def extract_location(location_data: Dict) -> Dict[str, str]:
    """Extrai informações de localização"""
    cidade = clean_text(location_data.get('cidade_extraida', ''))
    estado = clean_text(location_data.get('estado_extraido', ''))
    
    # Limpa cidades inválidas
    invalid_cities = ['s', 'o ar', 'HDI', 'mantendo', 'e', 'Lider de Logistica']
    if cidade in invalid_cities or len(cidade) <= 2:
        cidade = ''
    
    return {
        'cidade': cidade,
        'estado': estado,
        'regiao': clean_text(location_data.get('regiao', '')),
        'localidade_completa': clean_text(location_data.get('localidade_original', ''))
    }

def extract_responsibilities(resp_data: Dict) -> List[str]:
    """Extrai responsabilidades limpas"""
    responsibilities = []
    
    if 'lista_responsabilidades' in resp_data:
        for resp in resp_data['lista_responsabilidades']:
            cleaned = clean_text(resp)
            if cleaned and len(cleaned) > 20:  # Filtra responsabilidades muito curtas
                # Remove textos que não são responsabilidades
                if not any(x in cleaned.upper() for x in ['SKY TEC', 'HOSPITAL ALBERT', 'COLEGIO BRASIL']):
                    responsibilities.append(cleaned[:500])  # Limita tamanho
    
    return responsibilities[:5]  # Máximo 5 responsabilidades

def extract_skills(skills_data: Dict) -> List[str]:
    """Extrai habilidades técnicas"""
    skills = []
    
    if 'habilidades_tecnicas' in skills_data:
        for skill in skills_data['habilidades_tecnicas']:
            cleaned = clean_text(skill)
            if cleaned and len(cleaned) > 1:
                skills.append(cleaned)
    
    return list(set(skills))[:10]  # Remove duplicatas e limita

def create_clean_description(original_data: Dict) -> str:
    """Cria descrição limpa baseada nos dados"""
    parts = []
    
    # Adiciona informações básicas
    titulo = extract_job_title(original_data.get('informacoes_basicas', {}).get('titulo', ''))
    if titulo:
        parts.append(f"Vaga: {titulo}")
    
    # Adiciona responsabilidades
    responsibilities = extract_responsibilities(original_data.get('responsabilidades', {}))
    if responsibilities:
        parts.append("Responsabilidades: " + '; '.join(responsibilities[:3]))
    
    # Adiciona requisitos se disponível
    requisitos = original_data.get('requisitos', {}).get('requisitos_texto_original', '')
    if requisitos and requisitos != 'nan' and len(clean_text(requisitos)) > 50:
        parts.append(f"Requisitos: {clean_text(requisitos)[:300]}")
    
    return ' | '.join(parts)

def reorganize_job_data(job_data: Dict) -> Dict[str, Any]:
    """Reorganiza dados de uma vaga"""
    info_basicas = job_data.get('informacoes_basicas', {})
    localizacao = job_data.get('localizacao', {})
    
    # Estrutura limpa
    clean_job = {
        'id': job_data.get('id'),
        'informacoes_basicas': {
            'setor': clean_text(info_basicas.get('setor', '')),
            'empresa_principal': extract_company_name(info_basicas.get('empresa_principal', '')),
            'titulo_vaga': extract_job_title(info_basicas.get('titulo', '')),
            'modalidade': clean_text(info_basicas.get('modalidade', 'Não especificado')),
            'fonte': clean_text(info_basicas.get('fonte', '')),
            'area': clean_text(info_basicas.get('area', ''))
        },
        'localizacao': extract_location(localizacao),
        'requisitos': {
            'experiencia_necessaria': clean_text(job_data.get('requisitos', {}).get('experiencia_necessaria', '')),
            'formacao_minima': clean_text(job_data.get('requisitos', {}).get('formacao_minima', '')),
            'idiomas': job_data.get('requisitos', {}).get('idiomas', [])
        },
        'responsabilidades': extract_responsibilities(job_data.get('responsabilidades', {})),
        'habilidades_requeridas': extract_skills(job_data.get('habilidades_e_competencias', {})),
        'remuneracao': {
            'tipo': clean_text(job_data.get('remuneracao', {}).get('tipo', '')),
            'valor_minimo': job_data.get('remuneracao', {}).get('valor_minimo'),
            'valor_maximo': job_data.get('remuneracao', {}).get('valor_maximo')
        },
        'descricao_completa': {
            'texto_completo': create_clean_description(job_data)
        }
    }
    
    return clean_job

def load_and_reorganize(input_file: str, output_file: str):
    """Carrega e reorganiza arquivo JSONL"""
    print(f"Carregando dados de: {input_file}")
    
    jobs = []
    with open(input_file, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            if line.strip():
                try:
                    job_data = json.loads(line)
                    jobs.append(job_data)
                except json.JSONDecodeError as e:
                    print(f"Erro na linha {line_num}: {e}")
    
    print(f"Total de vagas carregadas: {len(jobs)}")
    
    # Reorganiza dados
    print("Reorganizando dados...")
    clean_jobs = []
    
    for i, job in enumerate(jobs, 1):
        try:
            clean_job = reorganize_job_data(job)
            
            # Valida dados essenciais
            if (clean_job['informacoes_basicas']['setor'] and 
                clean_job['descricao_completa']['texto_completo']):
                clean_job['id'] = i  # Reordena IDs
                clean_jobs.append(clean_job)
            else:
                print(f"Vaga {job.get('id', i)} descartada por falta de dados essenciais")
                
        except Exception as e:
            print(f"Erro ao processar vaga {job.get('id', i)}: {e}")
    
    print(f"Total de vagas reorganizadas: {len(clean_jobs)}")
    
    # Salva dados reorganizados
    print(f"Salvando dados reorganizados em: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        for job in clean_jobs:
            f.write(json.dumps(job, ensure_ascii=False) + '\n')
    
    # Gera relatório
    generate_report(clean_jobs)
    
    return clean_jobs

def generate_report(jobs: List[Dict]):
    """Gera relatório dos dados reorganizados"""
    print("\n=== RELATÓRIO DE REORGANIZAÇÃO ===")
    
    # Estatísticas por setor
    setores = defaultdict(int)
    empresas = defaultdict(int)
    cidades = defaultdict(int)
    
    vagas_com_empresa = 0
    vagas_com_cidade = 0
    vagas_com_responsabilidades = 0
    vagas_com_habilidades = 0
    
    for job in jobs:
        setor = job['informacoes_basicas']['setor']
        empresa = job['informacoes_basicas']['empresa_principal']
        cidade = job['localizacao']['cidade']
        
        setores[setor] += 1
        
        if empresa:
            empresas[empresa] += 1
            vagas_com_empresa += 1
        
        if cidade:
            cidades[cidade] += 1
            vagas_com_cidade += 1
        
        if job['responsabilidades']:
            vagas_com_responsabilidades += 1
        
        if job['habilidades_requeridas']:
            vagas_com_habilidades += 1
    
    print(f"Total de vagas: {len(jobs)}")
    print(f"Vagas com empresa: {vagas_com_empresa} ({vagas_com_empresa/len(jobs)*100:.1f}%)")
    print(f"Vagas com cidade: {vagas_com_cidade} ({vagas_com_cidade/len(jobs)*100:.1f}%)")
    print(f"Vagas com responsabilidades: {vagas_com_responsabilidades} ({vagas_com_responsabilidades/len(jobs)*100:.1f}%)")
    print(f"Vagas com habilidades: {vagas_com_habilidades} ({vagas_com_habilidades/len(jobs)*100:.1f}%)")
    
    print(f"\n=== TOP 10 SETORES ===")
    for setor, count in sorted(setores.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"{setor}: {count} vagas")
    
    print(f"\n=== TOP 10 EMPRESAS ===")
    for empresa, count in sorted(empresas.items(), key=lambda x: x[1], reverse=True)[:10]:
        if empresa:  # Só mostra empresas não vazias
            print(f"{empresa}: {count} vagas")
    
    print(f"\n=== TOP 10 CIDADES ===")
    for cidade, count in sorted(cidades.items(), key=lambda x: x[1], reverse=True)[:10]:
        if cidade:  # Só mostra cidades não vazias
            print(f"{cidade}: {count} vagas")
    
    # Salva relatório
    report = {
        'total_vagas': len(jobs),
        'estatisticas': {
            'com_empresa': vagas_com_empresa,
            'com_cidade': vagas_com_cidade,
            'com_responsabilidades': vagas_com_responsabilidades,
            'com_habilidades': vagas_com_habilidades
        },
        'setores': dict(setores),
        'top_empresas': dict(sorted(empresas.items(), key=lambda x: x[1], reverse=True)[:20]),
        'top_cidades': dict(sorted(cidades.items(), key=lambda x: x[1], reverse=True)[:20])
    }
    
    with open('relatorio_reorganizacao.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Relatório salvo em: relatorio_reorganizacao.json")

def main():
    input_file = 'vagas_todos_setores_sem_duplicatas.jsonl'
    output_file = 'vagas_reorganizadas_completo.jsonl'
    
    print("=== REORGANIZAÇÃO COMPLETA DO ARQUIVO JSONL ===")
    
    # Reorganiza dados
    clean_jobs = load_and_reorganize(input_file, output_file)
    
    print(f"\n🎉 Reorganização concluída!")
    print(f"Arquivo original: {input_file}")
    print(f"Arquivo reorganizado: {output_file}")
    print(f"Total de vagas processadas: {len(clean_jobs)}")

if __name__ == "__main__":
    main()