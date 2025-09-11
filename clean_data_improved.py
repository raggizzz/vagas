import pandas as pd
import json
import re
from typing import Dict, List, Any

def clean_nan_values(value):
    """Remove valores nan e limpa strings"""
    if pd.isna(value) or str(value).lower() == 'nan' or str(value).strip() == '':
        return None
    return str(value).strip()

def extract_salary_info(salary_text: str) -> Dict[str, Any]:
    """Extrai informações detalhadas do salário"""
    if not salary_text or salary_text.strip() == '' or salary_text.lower() == 'nan':
        return {
            "tipo": "não_informado",
            "valor_minimo": None,
            "valor_maximo": None,
            "texto_original": None
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

def extract_skills_from_description(description: str) -> List[str]:
    """Extrai habilidades técnicas da descrição"""
    if not description or description.lower() == 'nan':
        return []
    
    # Lista de tecnologias e habilidades comuns para área industrial
    tech_skills = [
        # Programação e TI
        'Python', 'Java', 'JavaScript', 'C#', 'C++', 'C', 'SQL', 'Excel', 'VBA',
        'AutoCAD', 'SolidWorks', 'CATIA', 'Inventor', 'Fusion 360',
        
        # Sistemas industriais
        'SAP', 'ERP', 'MES', 'SCADA', 'PLC', 'CLP', 'HMI', 'DCS',
        'Siemens', 'Allen Bradley', 'Schneider', 'WEG', 'ABB',
        
        # Manutenção e engenharia
        'Manutenção Preventiva', 'Manutenção Corretiva', 'TPM', 'RCM',
        'Soldagem', 'Usinagem', 'Tornearia', 'Fresagem', 'Caldeiraria',
        'Hidráulica', 'Pneumática', 'Elétrica', 'Eletrônica', 'Instrumentação',
        
        # Qualidade e processos
        'ISO 9001', 'ISO 14001', 'OHSAS 18001', 'Lean Manufacturing', 'Six Sigma',
        '5S', 'Kaizen', 'PDCA', 'FMEA', 'CEP', 'SPC',
        
        # Segurança
        'NR-10', 'NR-12', 'NR-13', 'NR-33', 'NR-35', 'CIPA', 'SIPAT',
        
        # Outros
        'Power BI', 'Tableau', 'Minitab', 'MATLAB', 'LabVIEW'
    ]
    
    found_skills = []
    description_lower = description.lower()
    
    for skill in tech_skills:
        if skill.lower() in description_lower:
            found_skills.append(skill)
    
    return list(set(found_skills))  # Remove duplicatas

def extract_requirements_from_description(description: str) -> Dict[str, Any]:
    """Extrai requisitos da descrição"""
    if not description or description.lower() == 'nan':
        return {"experiencia": None, "formacao": None, "idiomas": [], "certificacoes": []}
    
    desc_lower = description.lower()
    
    # Extração de experiência
    experiencia = None
    exp_patterns = [
        r'(\d+)\s*anos?\s*de\s*experiência',
        r'experiência\s*de\s*(\d+)\s*anos?',
        r'(\d+)\s*anos?\s*de\s*atuação',
        r'mínimo\s*de\s*(\d+)\s*anos?',
        r'(\d+)\s*anos?\s*na\s*área'
    ]
    
    for pattern in exp_patterns:
        match = re.search(pattern, desc_lower)
        if match:
            experiencia = f"{match.group(1)} anos"
            break
    
    # Extração de formação
    formacao = None
    if any(word in desc_lower for word in ['superior completo', 'graduação', 'faculdade', 'universidade', 'bacharel']):
        formacao = "Superior Completo"
    elif any(word in desc_lower for word in ['superior em andamento', 'cursando superior']):
        formacao = "Superior em Andamento"
    elif any(word in desc_lower for word in ['técnico', 'tecnólogo']):
        formacao = "Técnico"
    elif any(word in desc_lower for word in ['ensino médio', 'segundo grau', 'nível médio']):
        formacao = "Ensino Médio"
    
    # Extração de idiomas
    idiomas = []
    if 'inglês' in desc_lower:
        idiomas.append('Inglês')
    if 'espanhol' in desc_lower:
        idiomas.append('Espanhol')
    if 'francês' in desc_lower:
        idiomas.append('Francês')
    
    # Extração de certificações
    certificacoes = []
    cert_patterns = [
        r'nr[\s-]*(\d+)', r'cnh\s*[a-e]', r'crea', r'crc', r'crq',
        r'iso\s*\d+', r'ohsas\s*\d+', r'green\s*belt', r'black\s*belt'
    ]
    
    for pattern in cert_patterns:
        matches = re.findall(pattern, desc_lower)
        for match in matches:
            if pattern.startswith('nr'):
                certificacoes.append(f'NR-{match}')
            else:
                certificacoes.append(match.upper())
    
    return {
        "experiencia": experiencia,
        "formacao": formacao,
        "idiomas": idiomas,
        "certificacoes": list(set(certificacoes))
    }

def extract_company_info(description: str) -> Dict[str, Any]:
    """Extrai informações sobre a empresa da descrição"""
    if not description or description.lower() == 'nan':
        return {"setor_detalhado": None, "porte": None, "beneficios": []}
    
    desc_lower = description.lower()
    
    # Benefícios comuns
    beneficios = []
    beneficios_patterns = [
        'vale transporte', 'vale alimentação', 'vale refeição', 'plano de saúde',
        'plano odontológico', 'seguro de vida', 'participação nos lucros',
        'auxílio creche', 'gympass', 'convênio médico', 'cesta básica'
    ]
    
    for beneficio in beneficios_patterns:
        if beneficio in desc_lower:
            beneficios.append(beneficio.title())
    
    # Porte da empresa
    porte = None
    if any(word in desc_lower for word in ['multinacional', 'grande porte']):
        porte = "Grande"
    elif any(word in desc_lower for word in ['médio porte', 'média empresa']):
        porte = "Médio"
    elif any(word in desc_lower for word in ['pequeno porte', 'pequena empresa', 'startup']):
        porte = "Pequeno"
    
    return {
        "porte": porte,
        "beneficios": beneficios
    }

def clean_and_structure_data(csv_file: str) -> List[Dict[str, Any]]:
    """Limpa e estrutura os dados do CSV"""
    df = pd.read_csv(csv_file)
    
    structured_jobs = []
    
    for index, row in df.iterrows():
        # Limpa valores nan
        titulo = clean_nan_values(row.get('titulo'))
        empresa = clean_nan_values(row.get('empresa'))
        localidade = clean_nan_values(row.get('localidade'))
        modalidade = clean_nan_values(row.get('modalidade'))
        salario = clean_nan_values(row.get('salario'))
        habilidades = clean_nan_values(row.get('habilidades'))
        requisitos = clean_nan_values(row.get('requisitos'))
        descricao = clean_nan_values(row.get('descricao'))
        publicada_em = clean_nan_values(row.get('publicada_em'))
        setor = clean_nan_values(row.get('setor'))
        link = clean_nan_values(row.get('link'))
        
        # Extrai informações estruturadas
        salary_info = extract_salary_info(salario)
        skills_from_desc = extract_skills_from_description(descricao)
        requirements = extract_requirements_from_description(descricao)
        company_info = extract_company_info(descricao)
        
        # Combina habilidades do campo específico com as extraídas da descrição
        habilidades_campo = []
        if habilidades:
            habilidades_campo = [h.strip() for h in habilidades.split(',') if h.strip()]
        
        all_skills = list(set(habilidades_campo + skills_from_desc))
        
        job_data = {
            "id": index + 1,
            "informacoes_basicas": {
                "titulo": titulo,
                "empresa": empresa,
                "setor": setor,
                "localidade": localidade,
                "modalidade": modalidade,
                "publicada_em": publicada_em,
                "link": link
            },
            "remuneracao": salary_info,
            "requisitos": {
                "experiencia_necessaria": requirements["experiencia"],
                "formacao_minima": requirements["formacao"],
                "idiomas": requirements["idiomas"],
                "certificacoes": requirements["certificacoes"],
                "requisitos_texto_original": requisitos
            },
            "habilidades_e_competencias": {
                "habilidades_tecnicas": all_skills,
                "total_habilidades": len(all_skills)
            },
            "empresa_info": {
                "porte": company_info["porte"],
                "beneficios": company_info["beneficios"]
            },
            "descricao_completa": {
                "texto_completo": descricao,
                "tamanho_caracteres": len(descricao) if descricao else 0,
                "tem_detalhes_expandidos": len(descricao) > 200 if descricao else False
            },
            "metadados": {
                "extraido_em": "2024-01-09",
                "fonte": "Catho",
                "versao_scraper": "2.1"
            }
        }
        
        structured_jobs.append(job_data)
    
    return structured_jobs

def save_structured_data(structured_data: List[Dict[str, Any]], output_file: str):
    """Salva os dados estruturados em JSON"""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(structured_data, f, ensure_ascii=False, indent=2)

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
        if skill:  # Ignora valores None
            skill_counts[skill] = skill_counts.get(skill, 0) + 1
    
    top_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    
    # Análise de empresas
    empresas = [job['informacoes_basicas']['empresa'] for job in structured_data if job['informacoes_basicas']['empresa']]
    empresa_counts = {}
    for empresa in empresas:
        empresa_counts[empresa] = empresa_counts.get(empresa, 0) + 1
    
    # Análise de formação
    formacoes = [job['requisitos']['formacao_minima'] for job in structured_data if job['requisitos']['formacao_minima']]
    formacao_counts = {}
    for formacao in formacoes:
        formacao_counts[formacao] = formacao_counts.get(formacao, 0) + 1
    
    # Análise de benefícios
    all_beneficios = []
    for job in structured_data:
        all_beneficios.extend(job['empresa_info']['beneficios'])
    
    beneficio_counts = {}
    for beneficio in all_beneficios:
        beneficio_counts[beneficio] = beneficio_counts.get(beneficio, 0) + 1
    
    return {
        "total_vagas": total_jobs,
        "analise_salarial": {
            "vagas_com_salario": len(salarios_informados),
            "vagas_com_faixa_salarial": len(salarios_faixa),
            "percentual_com_salario": round((len(salarios_informados) / total_jobs) * 100, 2) if total_jobs > 0 else 0
        },
        "analise_habilidades": {
            "total_habilidades_unicas": len(skill_counts),
            "top_10_habilidades": top_skills
        },
        "analise_empresas": {
            "total_empresas_unicas": len(empresa_counts),
            "empresas_com_mais_vagas": sorted(empresa_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        },
        "analise_formacao": {
            "distribuicao_formacao": sorted(formacao_counts.items(), key=lambda x: x[1], reverse=True)
        },
        "analise_beneficios": {
            "beneficios_mais_oferecidos": sorted(beneficio_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        }
    }

if __name__ == "__main__":
    # Arquivo de entrada
    csv_file = "vagas_industrial_unico.csv"
    
    # Arquivos de saída
    json_output = "vagas_industrial_limpo.json"
    summary_output = "relatorio_vagas_industrial_limpo.json"
    
    print(f"Processando dados do arquivo: {csv_file}")
    
    # Processa e estrutura os dados
    structured_data = clean_and_structure_data(csv_file)
    
    # Salva dados estruturados
    save_structured_data(structured_data, json_output)
    print(f"Dados estruturados salvos em: {json_output}")
    
    # Gera e salva relatório
    summary = generate_summary_report(structured_data)
    with open(summary_output, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(f"Relatório resumo salvo em: {summary_output}")
    
    print(f"\nResumo do processamento:")
    print(f"- Total de vagas processadas: {summary['total_vagas']}")
    print(f"- Vagas com informação salarial: {summary['analise_salarial']['vagas_com_salario']}")
    print(f"- Habilidades técnicas identificadas: {summary['analise_habilidades']['total_habilidades_unicas']}")
    print(f"- Empresas únicas: {summary['analise_empresas']['total_empresas_unicas']}")
    print(f"- Benefícios identificados: {len(summary['analise_beneficios']['beneficios_mais_oferecidos'])}")