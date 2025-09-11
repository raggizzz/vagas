import pandas as pd
import json
import re
from typing import Dict, List, Any
from datetime import datetime

def extract_salary_info(salary_text: str) -> Dict[str, Any]:
    """Extrai informações detalhadas do salário"""
    if not salary_text or salary_text.strip() == '':
        return {
            "tipo": "não_informado",
            "valor_minimo": None,
            "valor_maximo": None,
            "texto_original": salary_text
        }
    
    # Padrão para faixa salarial: "De R$ X a R$ Y"
    faixa_pattern = r'De R\$\s*([\d.,]+)\s*a R\$\s*([\d.,]+)'
    faixa_match = re.search(faixa_pattern, salary_text)
    
    if faixa_match:
        min_val = float(faixa_match.group(1).replace('.', '').replace(',', '.'))
        max_val = float(faixa_match.group(2).replace('.', '').replace(',', '.'))
        return {
            "tipo": "faixa",
            "valor_minimo": min_val,
            "valor_maximo": max_val,
            "texto_original": salary_text
        }
    
    # Padrão para valor único: "R$ X"
    valor_pattern = r'R\$\s*([\d.,]+)'
    valor_match = re.search(valor_pattern, salary_text)
    
    if valor_match:
        valor = float(valor_match.group(1).replace('.', '').replace(',', '.'))
        return {
            "tipo": "valor_fixo",
            "valor_minimo": valor,
            "valor_maximo": valor,
            "texto_original": salary_text
        }
    
    # Casos especiais
    if 'combinar' in salary_text.lower() or 'a combinar' in salary_text.lower():
        return {
            "tipo": "a_combinar",
            "valor_minimo": None,
            "valor_maximo": None,
            "texto_original": salary_text
        }
    
    return {
        "tipo": "outros",
        "valor_minimo": None,
        "valor_maximo": None,
        "texto_original": salary_text
    }

def extract_company_from_description(description: str) -> List[str]:
    """Extrai nomes de empresas da descrição"""
    if not description:
        return []
    
    companies = []
    segments = description.split('|')
    
    for segment in segments:
        segment = segment.strip()
        # Procura por padrões de empresa
        if any(keyword in segment.upper() for keyword in ['HOSPITAL', 'EMPRESA', 'COMERCIO', 'COLEGIO', 'INSTITUTO']):
            # Extrai o nome da empresa
            if 'HOSPITAL' in segment.upper():
                match = re.search(r'HOSPITAL[\s\w]+', segment.upper())
                if match:
                    companies.append(match.group().title())
            elif 'EMPRESA' in segment.upper():
                # Pega o texto após "EMPRESA"
                match = re.search(r'EMPRESA[\s\w-]+', segment.upper())
                if match:
                    companies.append(match.group().title())
            elif segment.strip() and len(segment.strip()) < 100:
                companies.append(segment.strip())
    
    return list(set(companies))  # Remove duplicatas

def extract_location_from_description(description: str) -> Dict[str, str]:
    """Extrai informações de localização da descrição"""
    if not description:
        return {"cidade": None, "estado": None, "unidade": None}
    
    # Procura por padrões de localização
    location_patterns = [
        r'Unidade:\s*([^-]+)\s*-\s*([^-]+)\s*-\s*(\w{2})',
        r'([A-Za-z\s]+)\s*-\s*(\w{2})\s*Jornada',
        r'([A-Za-z\s]+)\s*-\s*(\w{2})'
    ]
    
    for pattern in location_patterns:
        match = re.search(pattern, description)
        if match:
            if len(match.groups()) == 3:
                return {
                    "unidade": match.group(1).strip(),
                    "cidade": match.group(2).strip(),
                    "estado": match.group(3).strip()
                }
            elif len(match.groups()) == 2:
                return {
                    "unidade": None,
                    "cidade": match.group(1).strip(),
                    "estado": match.group(2).strip()
                }
    
    return {"cidade": None, "estado": None, "unidade": None}

def extract_work_schedule_from_description(description: str) -> str:
    """Extrai informações de jornada de trabalho"""
    if not description:
        return "Não especificado"
    
    # Procura por padrões de jornada
    schedule_patterns = [
        r'Jornada de Trabalho:\s*([^|]+)',
        r'(\d+/hrs\s*mês)',
        r'(\d+\s*horas?\s*semanais?)',
        r'(\d+h\s*semanais?)'
    ]
    
    for pattern in schedule_patterns:
        match = re.search(pattern, description, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    
    return "Não especificado"

def extract_responsibilities_from_description(description: str) -> List[str]:
    """Extrai responsabilidades da descrição"""
    if not description:
        return []
    
    responsibilities = []
    segments = description.split('|')
    
    for segment in segments:
        segment = segment.strip()
        # Procura por segmentos que começam com palavras-chave de responsabilidades
        if any(keyword in segment.lower() for keyword in ['responsabilidades:', 'responsável por', 'atuar', 'desenvolver', 'coordenar', 'elaborar', 'realizar']):
            # Limpa e adiciona a responsabilidade
            clean_resp = re.sub(r'^responsabilidades?:\s*', '', segment, flags=re.IGNORECASE)
            if len(clean_resp.strip()) > 10:  # Filtra responsabilidades muito curtas
                responsibilities.append(clean_resp.strip())
        elif segment.startswith('""') and segment.endswith('""'):
            # Remove aspas duplas e adiciona
            clean_resp = segment.strip('"').strip()
            if len(clean_resp) > 10:
                responsibilities.append(clean_resp)
    
    return responsibilities

def extract_skills_from_description(description: str) -> List[str]:
    """Extrai habilidades técnicas da descrição"""
    if not description:
        return []
    
    # Lista expandida de tecnologias e habilidades
    tech_skills = [
        'Python', 'Java', 'JavaScript', 'React', 'Angular', 'Vue', 'Node.js',
        'SQL', 'MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'Docker', 'Kubernetes',
        'AWS', 'Azure', 'GCP', 'Git', 'GitHub', 'GitLab', 'Jenkins', 'CI/CD',
        'HTML', 'CSS', 'Bootstrap', 'Sass', 'TypeScript', 'PHP', 'Laravel',
        'Django', 'Flask', 'Spring', 'Hibernate', 'REST', 'API', 'GraphQL',
        'Microservices', 'Agile', 'Scrum', 'Kanban', 'TDD', 'BDD',
        'Machine Learning', 'AI', 'Data Science', 'Pandas', 'NumPy', 'Scikit-learn',
        'TensorFlow', 'PyTorch', 'Power BI', 'Tableau', 'Excel', 'VBA',
        'C#', 'C++', 'C', 'Go', 'Rust', 'Kotlin', 'Swift', 'Ruby', 'Perl',
        'Linux', 'Windows', 'MacOS', 'Bash', 'PowerShell', 'Terraform',
        'Ansible', 'Puppet', 'Chef', 'Vagrant', 'VMware', 'Hyper-V',
        'ABA', 'Social Media', 'Marketing', 'Vendas', 'Atendimento'
    ]
    
    found_skills = []
    description_lower = description.lower()
    
    for skill in tech_skills:
        if skill.lower() in description_lower:
            found_skills.append(skill)
    
    return list(set(found_skills))  # Remove duplicatas

def extract_requirements_from_description(description: str) -> Dict[str, Any]:
    """Extrai requisitos da descrição"""
    if not description:
        return {"experiencia": None, "formacao": None, "idiomas": [], "outros": []}
    
    desc_lower = description.lower()
    
    # Extração de experiência
    experiencia = None
    exp_patterns = [
        r'(\d+)\s*anos?\s*de\s*experiência',
        r'experiência\s*de\s*(\d+)\s*anos?',
        r'(\d+)\s*anos?\s*de\s*atuação',
        r'mínimo\s*de\s*(\d+)\s*anos?',
        r'recém\s*formad[ao]'
    ]
    
    for pattern in exp_patterns:
        match = re.search(pattern, desc_lower)
        if match:
            if 'recém' in pattern:
                experiencia = "Recém formado"
            else:
                experiencia = f"{match.group(1)} anos"
            break
    
    # Extração de formação
    formacao = None
    if any(word in desc_lower for word in ['superior', 'graduação', 'faculdade', 'universidade']):
        formacao = "Superior"
    elif any(word in desc_lower for word in ['técnico', 'tecnólogo']):
        formacao = "Técnico"
    elif any(word in desc_lower for word in ['ensino médio', 'segundo grau']):
        formacao = "Ensino Médio"
    elif any(word in desc_lower for word in ['curso', 'formação']):
        formacao = "Curso específico"
    
    # Extração de idiomas
    idiomas = []
    if 'inglês' in desc_lower:
        idiomas.append('Inglês')
    if 'espanhol' in desc_lower:
        idiomas.append('Espanhol')
    if 'francês' in desc_lower:
        idiomas.append('Francês')
    
    return {
        "experiencia": experiencia,
        "formacao": formacao,
        "idiomas": idiomas,
        "outros": []
    }

def clean_and_structure_data(csv_file: str) -> List[Dict[str, Any]]:
    """Limpa e estrutura os dados do CSV"""
    print(f"Carregando dados de {csv_file}...")
    df = pd.read_csv(csv_file)
    print(f"Total de registros carregados: {len(df)}")
    
    structured_jobs = []
    
    for idx, (index, row) in enumerate(df.iterrows()):
        if idx % 1000 == 0:
            print(f"Processando registro {idx + 1}/{len(df)}...")
        
        # Obtém dados básicos
        descricao_raw = str(row.get('Descrição', ''))
        requisitos_raw = str(row.get('Requisitos', ''))

        # Deduplica segmentos repetidos e cria texto combinado para análise
        def _dedup_segments(text: str) -> List[str]:
            if not text:
                return []
            segs = [s.strip().strip('"').strip("'") for s in text.split('|')]
            cleaned = []
            seen = set()
            for s in segs:
                norm = re.sub(r'\s+', ' ', s).strip().lower()
                if not norm or norm in seen:
                    continue
                seen.add(norm)
                cleaned.append(s.strip())
            return cleaned

        segs_desc = _dedup_segments(descricao_raw)
        segs_req = _dedup_segments(requisitos_raw)
        # Combina mantendo a ordem, sem duplicar itens já presentes em requisitos
        seen_req_norm = {re.sub(r'\s+', ' ', x).strip().lower() for x in segs_req}
        segmentos_combinados = segs_req + [s for s in segs_desc if re.sub(r'\s+', ' ', s).strip().lower() not in seen_req_norm]
        descricao_limpa = ' | '.join(segmentos_combinados).strip()
        
        # Seleciona pontos de requisitos mais relevantes e sem duplicação
        def _select_requisitos_points(segments: List[str]) -> List[str]:
            pontos: List[str] = []
            vistos = set()
            for s in segments:
                # remove prefixos comuns
                s_clean = re.sub(r'^(requisitos|exigências?|exigencias?|qualificações?|qualificacoes?|perfil|competências?:?|competencias?:?)\s*:\s*', '', s, flags=re.IGNORECASE)
                # critérios de seleção: bullets, ou presença de palavras-chave, e tamanho mínimo
                has_bullet = s.strip().startswith(('-', '•', '–'))
                has_kw = re.search(r'(requisit|qualific|experiênc|experienc|formação|formacao|conheciment|competênc|competenc|habilidad|idioma|perfil)', s, re.IGNORECASE) is not None
                if len(s_clean) < 15 or not (has_bullet or has_kw):
                    continue
                norm = re.sub(r'\s+', ' ', s_clean).strip().lower()
                if norm and norm not in vistos:
                    vistos.add(norm)
                    pontos.append(s_clean.strip().rstrip('.'))
            return pontos
        
        base_reqs = segs_req if segs_req else segmentos_combinados
        pontos_requisitos = _select_requisitos_points(base_reqs)
        if not pontos_requisitos:
            # fallback: pega segmentos mais informativos por tamanho
            pontos_requisitos = [s.strip().rstrip('.') for s in base_reqs if len(s) >= 25][:10]

        # Extrair setor da última coluna (após a vírgula final)
        # O setor está separado por vírgula no final da linha
        linha_completa = ','.join([str(val) for val in row])
        if ',' in linha_completa:
            partes = linha_completa.split(',')
            setor = partes[-1].strip() if len(partes) > 12 else ''
        else:
            setor = ''
            
        # Filtrar vagas sem setor definido
        if not setor or setor.lower() in ['', 'nan', 'null']:
            continue
        
        # Extrai informações estruturadas a partir da descrição limpa e combinada
        salary_info = extract_salary_info(str(row.get('Salário', '')))
        skills_from_desc = extract_skills_from_description(descricao_limpa)
        requirements = extract_requirements_from_description(descricao_limpa)
        companies = extract_company_from_description(descricao_limpa)
        location_info = extract_location_from_description(descricao_limpa)
        work_schedule = extract_work_schedule_from_description(descricao_limpa)
        responsibilities = extract_responsibilities_from_description(descricao_limpa)
        
        # Combina habilidades do campo específico com as extraídas da descrição
        habilidades_campo = str(row.get('Habilidades', '')).split(',') if pd.notna(row.get('Habilidades')) and row.get('Habilidades') else []
        habilidades_campo = [h.strip() for h in habilidades_campo if h.strip()]
        
        all_skills = list(set(habilidades_campo + skills_from_desc))
        
        # Determina a empresa principal
        empresa_principal = ''
        if companies:
            empresa_principal = companies[0]
        elif pd.notna(row.get('Empresa')) and str(row.get('Empresa')).strip():
            empresa_principal = str(row.get('Empresa')).strip()
        
        job_data = {
            "id": idx + 1,
            "informacoes_basicas": {
                "titulo": str(row.get('Título', '')).strip(),
                "empresa_principal": empresa_principal,
                "empresas_mencionadas": companies,
                "setor": setor,
                "area": str(row.get('Área', '')).strip() if pd.notna(row.get('Área')) else '',
                "fonte": str(row.get('Fonte', '')).strip(),
                "link": str(row.get('Link', '')).strip(),
                "publicada_em": str(row.get('Publicada em', '')).strip() if pd.notna(row.get('Publicada em')) else '',
                "modalidade": str(row.get('Modalidade', '')).strip() if pd.notna(row.get('Modalidade')) else 'Não especificado'
            },
            "localizacao": {
                "localidade_original": str(row.get('Localidade', '')).strip() if pd.notna(row.get('Localidade')) else '',
                "cidade_extraida": location_info.get('cidade'),
                "estado_extraido": location_info.get('estado'),
                "unidade": location_info.get('unidade')
            },
            "remuneracao": salary_info,
            "jornada_trabalho": {
                "jornada_extraida": work_schedule,
                "modalidade": str(row.get('Modalidade', '')).strip() if pd.notna(row.get('Modalidade')) else 'Presencial'
            },
            "requisitos": {
                "experiencia_necessaria": requirements["experiencia"],
                "formacao_minima": requirements["formacao"],
                "idiomas": requirements["idiomas"],
                "requisitos_texto_original": " | ".join(pontos_requisitos)
            },
            "responsabilidades": {
                "lista_responsabilidades": responsibilities,
                "total_responsabilidades": len(responsibilities)
            },
            "habilidades_e_competencias": {
                "habilidades_tecnicas": all_skills,
                "total_habilidades": len(all_skills),
                "habilidades_campo_original": habilidades_campo,
                "habilidades_extraidas_descricao": skills_from_desc
            },
            "descricao_completa": {
                "texto_completo": descricao_limpa,
                "segmentos_separados": segmentos_combinados,
                "total_segmentos": len(segmentos_combinados),
            }
        }
        
        structured_jobs.append(job_data)
    
    print(f"Processamento concluído! Total de vagas estruturadas: {len(structured_jobs)}")
    return structured_jobs

def save_structured_data(structured_data: List[Dict[str, Any]], output_file: str):
    """Salva os dados estruturados em JSON"""
    print(f"Salvando dados estruturados em {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(structured_data, f, ensure_ascii=False, indent=2)
    print(f"Dados salvos com sucesso!")

def generate_summary_report(structured_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Gera relatório resumo dos dados"""
    total_jobs = len(structured_data)
    
    # Análise salarial
    salarios_informados = [job for job in structured_data if job['remuneracao']['tipo'] != 'não_informado']
    salarios_faixa = [job for job in structured_data if job['remuneracao']['tipo'] == 'faixa']
    
    # Análise de habilidades
    all_skills = []
    for job in structured_data:
        all_skills.extend(job['habilidades_e_competencias']['habilidades_tecnicas'])
    
    skill_counts = {}
    for skill in all_skills:
        skill_counts[skill] = skill_counts.get(skill, 0) + 1
    
    top_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:15]
    
    # Análise de empresas
    empresas = [job['informacoes_basicas']['empresa_principal'] for job in structured_data if job['informacoes_basicas']['empresa_principal']]
    empresa_counts = {}
    for empresa in empresas:
        empresa_counts[empresa] = empresa_counts.get(empresa, 0) + 1
    
    # Análise de setores
    setores = [job['informacoes_basicas']['setor'] for job in structured_data if job['informacoes_basicas']['setor']]
    setor_counts = {}
    for setor in setores:
        setor_counts[setor] = setor_counts.get(setor, 0) + 1
    
    # Análise de localização
    estados = [job['localizacao']['estado_extraido'] for job in structured_data if job['localizacao']['estado_extraido']]
    estado_counts = {}
    for estado in estados:
        estado_counts[estado] = estado_counts.get(estado, 0) + 1
    
    return {
        "total_vagas": total_jobs,
        "analise_salarial": {
            "vagas_com_salario": len(salarios_informados),
            "vagas_com_faixa_salarial": len(salarios_faixa),
            "percentual_com_salario": round((len(salarios_informados) / total_jobs) * 100, 2) if total_jobs > 0 else 0
        },
        "analise_habilidades": {
            "total_habilidades_unicas": len(skill_counts),
            "top_15_habilidades": top_skills
        },
        "analise_empresas": {
            "total_empresas_unicas": len(empresa_counts),
            "empresas_com_mais_vagas": sorted(empresa_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        },
        "analise_setores": {
            "total_setores_unicos": len(setor_counts),
            "setores_com_mais_vagas": sorted(setor_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        },
        "analise_localizacao": {
            "total_estados_unicos": len(estado_counts),
            "estados_com_mais_vagas": sorted(estado_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        },
        "analise_descricoes": {
            "vagas_com_multiplos_segmentos": len([job for job in structured_data if job['descricao_completa']['total_segmentos'] > 1]),
            "vagas_com_responsabilidades_extraidas": len([job for job in structured_data if job['responsabilidades']['total_responsabilidades'] > 0]),
            "media_segmentos_por_vaga": round(sum([job['descricao_completa']['total_segmentos'] for job in structured_data]) / total_jobs, 2) if total_jobs > 0 else 0
        }
    }

if __name__ == "__main__":
    # Arquivo de entrada
    csv_file = "vagas_todos_setores_1_pagina.csv"
    
    # Arquivos de saída
    json_output = "vagas_todos_setores_estruturadas_completo.json"
    summary_output = "relatorio_vagas_todos_setores_completo.json"
    
    print(f"=== PROCESSADOR DE VAGAS COMPLETO ===")
    print(f"Arquivo de entrada: {csv_file}")
    print(f"Arquivo JSON de saída: {json_output}")
    print(f"Arquivo de relatório: {summary_output}")
    print("="*50)
    
    # Processa e estrutura os dados
    structured_data = clean_and_structure_data(csv_file)
    
    # Salva dados estruturados
    save_structured_data(structured_data, json_output)
    
    # Gera e salva relatório
    print("Gerando relatório resumo...")
    summary = generate_summary_report(structured_data)
    with open(summary_output, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(f"Relatório resumo salvo em: {summary_output}")
    
    print("\n=== RESUMO DO PROCESSAMENTO ===")
    print(f"📊 Total de vagas processadas: {summary['total_vagas']:,}")
    print(f"💰 Vagas com informação salarial: {summary['analise_salarial']['vagas_com_salario']:,} ({summary['analise_salarial']['percentual_com_salario']}%)")
    print(f"🛠️  Habilidades técnicas identificadas: {summary['analise_habilidades']['total_habilidades_unicas']:,}")
    print(f"🏢 Empresas únicas: {summary['analise_empresas']['total_empresas_unicas']:,}")
    print(f"🏭 Setores únicos: {summary['analise_setores']['total_setores_unicos']:,}")
    print(f"📍 Estados únicos: {summary['analise_localizacao']['total_estados_unicos']:,}")
    print(f"📝 Vagas com múltiplos segmentos: {summary['analise_descricoes']['vagas_com_multiplos_segmentos']:,}")
    print(f"✅ Vagas com responsabilidades extraídas: {summary['analise_descricoes']['vagas_com_responsabilidades_extraidas']:,}")
    
    print("\n🎯 Top 5 Setores:")
    for setor, count in summary['analise_setores']['setores_com_mais_vagas'][:5]:
        print(f"   {setor}: {count:,} vagas")
    
    print("\n🛠️  Top 5 Habilidades:")
    for skill, count in summary['analise_habilidades']['top_15_habilidades'][:5]:
        print(f"   {skill}: {count:,} menções")
    
    print("\n" + "="*50)
    print("✅ Processamento concluído com sucesso!")
    print(f"📁 Arquivo JSON: {json_output}")
    print(f"📊 Relatório: {summary_output}")