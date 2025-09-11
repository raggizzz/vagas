import pandas as pd
import json
import re
from typing import Dict, List, Any

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

def extract_skills_from_description(description: str) -> List[str]:
    """Extrai habilidades técnicas da descrição"""
    if not description:
        return []
    
    # Lista de tecnologias e habilidades comuns
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
        'Ansible', 'Puppet', 'Chef', 'Vagrant', 'VMware', 'Hyper-V'
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
        r'mínimo\s*de\s*(\d+)\s*anos?'
    ]
    
    for pattern in exp_patterns:
        match = re.search(pattern, desc_lower)
        if match:
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
    df = pd.read_csv(csv_file)
    
    structured_jobs = []
    
    for index, row in df.iterrows():
        # Extrai informações estruturadas
        salary_info = extract_salary_info(str(row.get('salario', '')))
        skills_from_desc = extract_skills_from_description(str(row.get('descricao', '')))
        requirements = extract_requirements_from_description(str(row.get('descricao', '')))
        
        # Combina habilidades do campo específico com as extraídas da descrição
        habilidades_campo = str(row.get('habilidades', '')).split(',') if row.get('habilidades') else []
        habilidades_campo = [h.strip() for h in habilidades_campo if h.strip()]
        
        all_skills = list(set(habilidades_campo + skills_from_desc))
        
        job_data = {
            "id": index + 1,
            "informacoes_basicas": {
                "titulo": str(row.get('titulo', '')).strip(),
                "empresa": str(row.get('empresa', '')).strip(),
                "setor": str(row.get('setor', '')).strip(),
                "localidade": str(row.get('localidade', '')).strip(),
                "modalidade": str(row.get('modalidade', '')).strip(),
                "publicada_em": str(row.get('publicada_em', '')).strip(),
                "link": str(row.get('link', '')).strip()
            },
            "remuneracao": salary_info,
            "requisitos": {
                "experiencia_necessaria": requirements["experiencia"],
                "formacao_minima": requirements["formacao"],
                "idiomas": requirements["idiomas"],
                "requisitos_texto_original": str(row.get('requisitos', '')).strip()
            },
            "habilidades_e_competencias": {
                "habilidades_tecnicas": all_skills,
                "total_habilidades": len(all_skills)
            },
            "descricao_completa": {
                "texto_completo": str(row.get('descricao', '')).strip(),
                "tamanho_caracteres": len(str(row.get('descricao', '')).strip()),
                "tem_detalhes_expandidos": len(str(row.get('descricao', '')).strip()) > 200
            },
            "metadados": {
                "extraido_em": "2024-01-09",
                "fonte": "Catho",
                "versao_scraper": "2.0"
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
        skill_counts[skill] = skill_counts.get(skill, 0) + 1
    
    top_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    
    # Análise de empresas
    empresas = [job['informacoes_basicas']['empresa'] for job in structured_data]
    empresa_counts = {}
    for empresa in empresas:
        empresa_counts[empresa] = empresa_counts.get(empresa, 0) + 1
    
    return {
        "total_vagas": total_jobs,
        "analise_salarial": {
            "vagas_com_salario": len(salarios_informados),
            "vagas_com_faixa_salarial": len(salarios_faixa),
            "percentual_com_salario": round((len(salarios_informados) / total_jobs) * 100, 2)
        },
        "analise_habilidades": {
            "total_habilidades_unicas": len(skill_counts),
            "top_10_habilidades": top_skills
        },
        "analise_empresas": {
            "total_empresas_unicas": len(empresa_counts),
            "empresas_com_mais_vagas": sorted(empresa_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        }
    }

if __name__ == "__main__":
    # Arquivo de entrada
    csv_file = "vagas_industrial_unico.csv"
    
    # Arquivos de saída
    json_output = "vagas_industrial_estruturadas.json"
    summary_output = "relatorio_vagas_industrial.json"
    
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