import json
import re
from collections import defaultdict

def extract_diverse_description(job_data):
    """Extrai uma descrição mais diversificada da vaga"""
    # Campos que podem conter descrições
    description_fields = [
        'descricao_completa',
        'descricao',
        'requisitos',
        'atividades',
        'beneficios',
        'observacoes'
    ]
    
    descriptions = []
    
    for field in description_fields:
        if field in job_data and job_data[field]:
            desc = str(job_data[field]).strip()
            if desc and len(desc) > 20:  # Apenas descrições com conteúdo significativo
                descriptions.append(desc)
    
    if not descriptions:
        return "Descrição não disponível"
    
    # Escolher a descrição mais longa e informativa
    best_description = max(descriptions, key=len)
    
    # Limpar a descrição
    best_description = clean_description(best_description)
    
    return best_description

def clean_description(description):
    """Limpa e melhora a descrição"""
    # Remover padrões repetitivos comuns
    patterns_to_remove = [
        r'CANDIDATURA FÁCIL\s*',
        r'Empresa Confidencial\s*',
        r'Por que\?.*?muito ativo\s*',
        r'A combinar\s*',
        r'\d+\s*vaga[s]?:.*?\(\d+\)\s*',
        r'Publicada em \d{2}/\d{2}\s*',
        r'Atualizada em \d{2}/\d{2}\s*',
        r'De R\$.*?a R\$.*?\s*',
        r'Até R\$.*?\s*'
    ]
    
    cleaned = description
    for pattern in patterns_to_remove:
        cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
    
    # Remover espaços extras e quebras de linha
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    
    # Se a descrição ficou muito curta, tentar usar a original
    if len(cleaned) < 50 and len(description) > 50:
        return description.strip()
    
    return cleaned if cleaned else description.strip()

def extract_better_company(job_data):
    """Extrai nome da empresa de forma mais inteligente"""
    company_fields = ['empresa', 'company', 'empregador', 'contratante']
    
    for field in company_fields:
        if field in job_data and job_data[field]:
            company = str(job_data[field]).strip()
            
            # Evitar nomes genéricos
            generic_names = [
                'empresa confidencial',
                'confidencial',
                'não informado',
                'a definir',
                'empresa'
            ]
            
            if company.lower() not in generic_names and len(company) > 3:
                return company
    
    # Se não encontrou empresa específica, tentar extrair do título ou descrição
    if 'titulo' in job_data:
        titulo = str(job_data['titulo'])
        # Procurar por nomes de empresa no título
        empresa_match = re.search(r'([A-Z][a-zA-Z\s&]+(?:LTDA|S\.A\.|EIRELI|ME)?)', titulo)
        if empresa_match:
            return empresa_match.group(1).strip()
    
    return "Empresa não informada"

def process_jobs_for_diversity():
    """Processa as vagas para criar descrições mais diversificadas"""
    input_file = 'vagas_todos_setores_estruturadas_completo.jsonl'
    output_file = 'vagas_descricoes_diversificadas.jsonl'
    
    print(f"Processando {input_file} para criar descrições mais diversificadas...")
    
    processed_jobs = []
    sector_descriptions = defaultdict(set)
    
    with open(input_file, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            try:
                job_data = json.loads(line.strip())
                
                # Extrair dados melhorados
                new_description = extract_diverse_description(job_data)
                new_company = extract_better_company(job_data)
                
                # Verificar se a descrição já existe no setor
                setor = job_data.get('setor', 'Não informado')
                
                # Se a descrição já existe no setor, tentar uma alternativa
                if new_description in sector_descriptions[setor]:
                    # Tentar combinar múltiplos campos para criar uma descrição única
                    alternative_desc = create_alternative_description(job_data)
                    if alternative_desc and alternative_desc not in sector_descriptions[setor]:
                        new_description = alternative_desc
                
                sector_descriptions[setor].add(new_description)
                
                # Criar nova vaga com dados melhorados
                improved_job = {
                    'titulo': job_data.get('titulo', 'Título não informado'),
                    'empresa': new_company,
                    'setor': setor,
                    'localizacao': job_data.get('localizacao', 'Localização não informada'),
                    'descricao': new_description,
                    'salario': job_data.get('salario', 'A combinar'),
                    'tipo_contrato': job_data.get('tipo_contrato', 'Não informado'),
                    'nivel_experiencia': job_data.get('nivel_experiencia', 'Não informado'),
                    'data_publicacao': job_data.get('data_publicacao', 'Não informada')
                }
                
                processed_jobs.append(improved_job)
                
                if line_num % 50 == 0:
                    print(f"Processadas {line_num} vagas...")
                    
            except json.JSONDecodeError as e:
                print(f"Erro ao processar linha {line_num}: {e}")
                continue
    
    # Salvar vagas processadas
    with open(output_file, 'w', encoding='utf-8') as f:
        for job in processed_jobs:
            f.write(json.dumps(job, ensure_ascii=False) + '\n')
    
    print(f"\nProcessamento concluído!")
    print(f"Total de vagas processadas: {len(processed_jobs)}")
    print(f"Arquivo salvo: {output_file}")
    
    # Estatísticas de diversidade por setor
    print(f"\n=== ESTATÍSTICAS DE DIVERSIDADE ====")
    for setor, descriptions in sector_descriptions.items():
        total_jobs = sum(1 for job in processed_jobs if job['setor'] == setor)
        diversity_rate = len(descriptions) / total_jobs * 100 if total_jobs > 0 else 0
        print(f"{setor}: {len(descriptions)} descrições únicas de {total_jobs} vagas ({diversity_rate:.1f}% diversidade)")
    
    return processed_jobs

def create_alternative_description(job_data):
    """Cria uma descrição alternativa combinando múltiplos campos"""
    parts = []
    
    # Adicionar requisitos se disponível
    if 'requisitos' in job_data and job_data['requisitos']:
        req = str(job_data['requisitos']).strip()
        if len(req) > 20:
            parts.append(f"Requisitos: {req}")
    
    # Adicionar atividades se disponível
    if 'atividades' in job_data and job_data['atividades']:
        ativ = str(job_data['atividades']).strip()
        if len(ativ) > 20:
            parts.append(f"Atividades: {ativ}")
    
    # Adicionar benefícios se disponível
    if 'beneficios' in job_data and job_data['beneficios']:
        benef = str(job_data['beneficios']).strip()
        if len(benef) > 20:
            parts.append(f"Benefícios: {benef}")
    
    if parts:
        combined = ' | '.join(parts)
        return clean_description(combined)
    
    return None

if __name__ == "__main__":
    print("Iniciando processamento para criar descrições mais diversificadas...")
    processed_jobs = process_jobs_for_diversity()
    print("\n✅ Processamento concluído com sucesso!")