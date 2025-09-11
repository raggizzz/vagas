import json
import re
from typing import List, Dict, Any
import hashlib

def extract_individual_jobs(jsonl_file: str, output_file: str):
    """
    Extrai vagas individuais do JSONL agregado, separando cada vaga
    com sua empresa e descrição correspondente.
    """
    
    normalized_jobs = []
    job_counter = 1
    
    with open(jsonl_file, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            try:
                data = json.loads(line.strip())
                
                # Extrair informações básicas
                setor = data.get('informacoes_basicas', {}).get('setor', '')
                empresas_mencionadas = data.get('informacoes_basicas', {}).get('empresas_mencionadas', [])
                
                # Extrair segmentos separados do texto completo
                segmentos = data.get('descricao_completa', {}).get('segmentos_separados', [])
                
                # Filtrar segmentos que são descrições de vagas (não empresas ou setores)
                descricoes_vagas = []
                for segmento in segmentos:
                    # Pular segmentos que são apenas nomes de empresas ou setores
                    if (len(segmento.strip()) > 50 and  # Descrições têm mais de 50 caracteres
                        not segmento.strip().isupper() and  # Não são apenas maiúsculas
                        segmento != setor):  # Não é o nome do setor
                        descricoes_vagas.append(segmento.strip())
                
                # Criar vagas individuais
                num_vagas = max(len(empresas_mencionadas), len(descricoes_vagas))
                
                for i in range(num_vagas):
                    # Mapear empresa (circular se necessário)
                    empresa = empresas_mencionadas[i % len(empresas_mencionadas)] if empresas_mencionadas else "Empresa não especificada"
                    
                    # Mapear descrição (circular se necessário)
                    descricao = descricoes_vagas[i % len(descricoes_vagas)] if descricoes_vagas else "Descrição não disponível"
                    
                    # Extrair título da vaga da descrição
                    titulo_match = re.search(r'Vaga:\s*([^\n]+)', descricao)
                    if not titulo_match:
                        titulo_match = re.search(r'^([^\n]{10,80})', descricao)
                    
                    titulo = titulo_match.group(1).strip() if titulo_match else f"Vaga {job_counter}"
                    
                    # Extrair localização
                    cidade = data.get('localizacao', {}).get('cidade_extraida', '')
                    estado = data.get('localizacao', {}).get('estado_extraido', '')
                    localizacao = f"{cidade}, {estado}" if cidade and estado else "Localização não especificada"
                    
                    # Extrair salário
                    salario_min = data.get('remuneracao', {}).get('valor_minimo')
                    salario_max = data.get('remuneracao', {}).get('valor_maximo')
                    
                    # Extrair modalidade de trabalho
                    modalidade = data.get('jornada_trabalho', {}).get('modalidade', 'Não especificado')
                    
                    # Gerar external_id único
                    external_id_source = f"{empresa}_{titulo}_{setor}_{i}"
                    external_id = hashlib.md5(external_id_source.encode('utf-8')).hexdigest()[:16]
                    
                    # Criar vaga normalizada
                    vaga_normalizada = {
                        "external_id": external_id,
                        "title": titulo,
                        "company_name": empresa,
                        "sector": setor,
                        "location": localizacao,
                        "salary_min": salario_min,
                        "salary_max": salario_max,
                        "description": descricao,
                        "work_type": modalidade,
                        "original_id": data.get('id'),
                        "source_line": line_num
                    }
                    
                    normalized_jobs.append(vaga_normalizada)
                    job_counter += 1
                    
            except json.JSONDecodeError as e:
                print(f"Erro ao processar linha {line_num}: {e}")
                continue
            except Exception as e:
                print(f"Erro inesperado na linha {line_num}: {e}")
                continue
    
    # Salvar vagas normalizadas
    with open(output_file, 'w', encoding='utf-8') as f:
        for job in normalized_jobs:
            f.write(json.dumps(job, ensure_ascii=False) + '\n')
    
    print(f"\n=== RELATÓRIO DE NORMALIZAÇÃO ===")
    print(f"Total de vagas normalizadas: {len(normalized_jobs)}")
    print(f"Arquivo salvo: {output_file}")
    
    # Estatísticas por setor
    setores = {}
    for job in normalized_jobs:
        setor = job['sector']
        setores[setor] = setores.get(setor, 0) + 1
    
    print(f"\nVagas por setor:")
    for setor, count in sorted(setores.items()):
        print(f"  {setor}: {count} vagas")
    
    return normalized_jobs

def preview_normalized_jobs(jobs: List[Dict], limit: int = 5):
    """
    Mostra uma prévia das vagas normalizadas
    """
    print(f"\n=== PRÉVIA DAS PRIMEIRAS {limit} VAGAS NORMALIZADAS ===")
    
    for i, job in enumerate(jobs[:limit]):
        print(f"\nVaga {i+1}:")
        print(f"  ID: {job['external_id']}")
        print(f"  Título: {job['title'][:80]}...")
        print(f"  Empresa: {job['company_name']}")
        print(f"  Setor: {job['sector']}")
        print(f"  Localização: {job['location']}")
        print(f"  Descrição: {job['description'][:100]}...")

if __name__ == "__main__":
    input_file = "vagas_todos_setores_estruturadas_completo.jsonl"
    output_file = "vagas_normalizadas_individuais.jsonl"
    
    print("Iniciando normalização das vagas...")
    
    # Extrair e normalizar vagas
    jobs = extract_individual_jobs(input_file, output_file)
    
    # Mostrar prévia
    preview_normalized_jobs(jobs)
    
    print(f"\nNormalização concluída! Arquivo salvo: {output_file}")