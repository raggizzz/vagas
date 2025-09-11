import json
import hashlib
from supabase import create_client, Client
import os
from typing import Dict, List, Optional, Set
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def connect_supabase() -> Client:
    """Conecta ao Supabase"""
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_KEY')
    
    if not url or not key:
        raise ValueError("SUPABASE_URL e SUPABASE_KEY devem estar definidas no arquivo .env")
    
    return create_client(url, key)

def clear_vagas_table(supabase: Client) -> bool:
    """Limpa a tabela vagas"""
    try:
        result = supabase.table('vagas').delete().neq('id', 0).execute()
        print(f"Tabela vagas limpa com sucesso")
        return True
    except Exception as e:
        print(f"Erro ao limpar tabela vagas: {e}")
        return False

def extract_proper_title(job_data: Dict) -> str:
    """Extrai um título adequado dos dados da vaga"""
    # Prioridade: fonte > primeiro segmento da descrição > fallback
    
    # 1. Tentar usar o campo 'fonte' das informações básicas
    fonte = job_data.get('informacoes_basicas', {}).get('fonte', '')
    if fonte and fonte != 'nan' and len(fonte.strip()) > 0:
        # Limpar o título se necessário
        title = fonte.strip()
        if not title.startswith('http'):
            return title
    
    # 2. Tentar extrair do primeiro segmento da descrição
    segmentos = job_data.get('descricao_completa', {}).get('segmentos_separados', [])
    if segmentos and len(segmentos) > 0:
        primeiro_segmento = segmentos[0].strip()
        # Procurar por padrões de título
        if 'Sumário:' in primeiro_segmento:
            # Extrair texto antes de 'Sumário:'
            parts = primeiro_segmento.split('Sumário:')
            if len(parts) > 0:
                potential_title = parts[0].strip()
                # Remover prefixos como "Unidade:"
                if 'Unidade:' in potential_title:
                    potential_title = potential_title.replace('Unidade:', '').strip()
                if potential_title:
                    return potential_title
        
        # Se não encontrar padrão específico, usar o primeiro segmento limitado
        if len(primeiro_segmento) > 10:
            return primeiro_segmento[:100] + '...' if len(primeiro_segmento) > 100 else primeiro_segmento
    
    # 3. Fallback para responsabilidades
    responsabilidades = job_data.get('responsabilidades', {}).get('lista_responsabilidades', [])
    if responsabilidades and len(responsabilidades) > 0:
        primeira_resp = responsabilidades[0].strip()
        return primeira_resp[:100] + '...' if len(primeira_resp) > 100 else primeira_resp
    
    # 4. Último fallback
    return "Vaga sem título específico"

def extract_location(job_data: Dict) -> str:
    """Extrai localização dos dados da vaga"""
    localizacao = job_data.get('localizacao', {})
    
    cidade = localizacao.get('cidade_extraida', '')
    estado = localizacao.get('estado_extraido', '')
    
    # Verificar se os valores não são None e converter para string
    if cidade is not None:
        cidade = str(cidade).strip()
    else:
        cidade = ''
        
    if estado is not None:
        estado = str(estado).strip()
    else:
        estado = ''
    
    if cidade and estado and cidade != 'nan' and estado != 'nan':
        return f"{cidade}, {estado}"
    elif cidade and cidade != 'nan':
        return cidade
    elif estado and estado != 'nan':
        return estado
    
    # Fallback: tentar extrair da localidade original
    localidade_original = localizacao.get('localidade_original', '')
    if localidade_original is not None:
        localidade_original = str(localidade_original).strip()
        if localidade_original and localidade_original != 'nan':
            return localidade_original
    
    # Tentar extrair da unidade
    unidade = localizacao.get('unidade', '')
    if unidade is not None:
        unidade = str(unidade).strip()
        if unidade and unidade != 'nan':
            return unidade
    
    return "Localização não especificada"

def extract_description(job_data: Dict) -> str:
    """Extrai descrição limpa da vaga"""
    # Usar segmentos separados para criar uma descrição mais limpa
    segmentos = job_data.get('descricao_completa', {}).get('segmentos_separados', [])
    
    if not segmentos:
        # Fallback para texto completo
        texto_completo = job_data.get('descricao_completa', {}).get('texto_completo', '')
        return texto_completo[:1000] + '...' if len(texto_completo) > 1000 else texto_completo
    
    # Filtrar segmentos relevantes (remover nomes de empresas isolados)
    segmentos_relevantes = []
    for segmento in segmentos:
        segmento = segmento.strip()
        # Pular segmentos muito curtos ou que são apenas nomes de empresas
        if len(segmento) > 20 and not segmento.isupper():
            segmentos_relevantes.append(segmento)
    
    if segmentos_relevantes:
        # Juntar os primeiros segmentos relevantes
        descricao = ' | '.join(segmentos_relevantes[:3])
        return descricao[:1000] + '...' if len(descricao) > 1000 else descricao
    
    # Se não houver segmentos relevantes, usar o primeiro segmento
    if segmentos:
        return segmentos[0][:1000] + '...' if len(segmentos[0]) > 1000 else segmentos[0]
    
    return "Descrição não disponível"

def generate_external_id(job_data: Dict) -> str:
    """Gera um ID externo único baseado no conteúdo da vaga"""
    # Usar múltiplos campos para garantir unicidade
    content_for_hash = (
        str(job_data.get('id', '')) +
        job_data.get('informacoes_basicas', {}).get('fonte', '') +
        job_data.get('informacoes_basicas', {}).get('empresa_principal', '') +
        job_data.get('localizacao', {}).get('cidade_extraida', '') +
        str(job_data.get('responsabilidades', {}).get('lista_responsabilidades', [])[:2])  # Primeiras 2 responsabilidades
    )
    
    return hashlib.md5(content_for_hash.encode()).hexdigest()[:16]

def extract_unique_company(job_data):
    """Extrai empresa de forma mais inteligente, evitando nomes genéricos"""
    import re
    
    # Primeiro, tentar extrair da unidade na descrição
    desc_completa = job_data.get('descricao_completa', {}).get('texto_completo', '')
    
    # Procurar por "Unidade:" na descrição
    unidade_match = re.search(r'Unidade:\s*([^-]+?)\s*-', desc_completa)
    if unidade_match:
        unidade = unidade_match.group(1).strip()
        if len(unidade) > 10 and not any(word in unidade.lower() for word in ['empresa', 'confidencial', 'reconhecida']):
            return unidade
    
    # Tentar extrair de segmentos específicos
    segmentos = job_data.get('descricao_completa', {}).get('segmentos_separados', [])
    for segmento in segmentos:
        if 'empresa:' in segmento.lower() or 'organização:' in segmento.lower():
            # Extrair nome após "Empresa:" ou "Organização:"
            empresa_match = re.search(r'(?:empresa|organização):\s*([^\n]+)', segmento, re.IGNORECASE)
            if empresa_match:
                empresa = empresa_match.group(1).strip()
                if len(empresa) > 5 and not any(word in empresa.lower() for word in ['confidencial', 'reconhecida']):
                    return empresa
    
    # Fallback para empresa_principal, mas limpar nomes genéricos
    empresa_original = job_data.get('informacoes_basicas', {}).get('empresa_principal', '')
    if empresa_original and not any(word in empresa_original.lower() for word in ['empresa reconhecida', 'empresa confidencial', 'empresa de']):
        return empresa_original
    
    return "Empresa não especificada"

def extract_unique_description(job_data):
    """Extrai descrição única para cada vaga, evitando textos padronizados"""
    import re
    
    segmentos = job_data.get('descricao_completa', {}).get('segmentos_separados', [])
    
    # Procurar por segmentos específicos da vaga
    descricao_parts = []
    
    for segmento in segmentos:
        segmento_lower = segmento.lower()
        
        # Pular segmentos genéricos/padronizados
        if any(skip_word in segmento_lower for skip_word in [
            'assessorar a coordenação',
            'sumário:',
            'unidade: hospital central',
            'jornada de trabalho: 150'
        ]):
            continue
            
        # Incluir segmentos específicos
        if any(include_word in segmento_lower for include_word in [
            'responsabilidades:',
            'atividades:',
            'requisitos:',
            'qualificações:',
            'experiência:',
            'formação:',
            'competências:',
            'habilidades:'
        ]):
            descricao_parts.append(segmento.strip())
    
    if descricao_parts:
        return ' '.join(descricao_parts)[:500]  # Limitar tamanho
    
    # Fallback: usar texto completo mas filtrar partes genéricas
    texto_completo = job_data.get('descricao_completa', {}).get('texto_completo', '')
    
    # Remover partes padronizadas
    texto_limpo = re.sub(r'Unidade: Hospital Central.*?Jornada de Trabalho: \d+/hrs mês\s*', '', texto_completo)
    texto_limpo = re.sub(r'Sumário: Assessorar a coordenação.*?(?=\n|$)', '', texto_limpo)
    
    return texto_limpo.strip()[:500] if texto_limpo.strip() else "Descrição não especificada"

def extract_proper_sector(job_data):
    """Extrai setor de forma mais precisa"""
    # Primeiro tentar do campo setor
    setor = job_data.get('informacoes_basicas', {}).get('setor', '')
    
    # Se o setor for muito genérico, tentar extrair da descrição
    if setor in ['ServicoSocial', 'Telecomunicacoes'] and len(setor) < 15:
        # Procurar por indicações de setor na descrição
        titulo = job_data.get('informacoes_basicas', {}).get('fonte', '')
        
        # Mapear títulos para setores mais específicos
        titulo_lower = titulo.lower()
        if any(word in titulo_lower for word in ['enfermeiro', 'médico', 'saúde', 'hospital']):
            return 'Saúde'
        elif any(word in titulo_lower for word in ['assistente social', 'coordenador social']):
            return 'Serviço Social'
        elif any(word in titulo_lower for word in ['vendas', 'comercial', 'vendedor']):
            return 'Comercial e Vendas'
        elif any(word in titulo_lower for word in ['administrativo', 'admin', 'secretário']):
            return 'Administração'
        elif any(word in titulo_lower for word in ['técnico', 'engenheiro', 'tecnologia']):
            return 'Técnica/Engenharia'
    
    return setor if setor else "Setor não especificado"

def map_job_to_vagas_format(job_data: Dict) -> Dict:
    """Mapeia dados da vaga para o formato da tabela vagas"""
    return {
        'external_id': generate_external_id(job_data),
        'titulo': extract_proper_title(job_data),
        'empresa': extract_unique_company(job_data),
        'setor': extract_proper_sector(job_data),
        'localizacao': extract_location(job_data),
        'salario_min': job_data.get('remuneracao', {}).get('valor_minimo'),
        'salario_max': job_data.get('remuneracao', {}).get('valor_maximo'),
        'descricao': extract_unique_description(job_data),
        'modalidade_trabalho': job_data.get('jornada_trabalho', {}).get('modalidade', 'Não especificado')
    }

def load_jobs_from_jsonl(file_path: str) -> List[Dict]:
    """Carrega vagas do arquivo JSONL"""
    jobs = []
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line_num, line in enumerate(file, 1):
                try:
                    job_data = json.loads(line.strip())
                    jobs.append(job_data)
                except json.JSONDecodeError as e:
                    print(f"Erro ao decodificar JSON na linha {line_num}: {e}")
                    continue
        print(f"Carregadas {len(jobs)} vagas do arquivo {file_path}")
    except FileNotFoundError:
        print(f"Arquivo {file_path} não encontrado")
    except Exception as e:
        print(f"Erro ao carregar arquivo {file_path}: {e}")
    
    return jobs

def upload_jobs_in_batches(supabase: Client, jobs: List[Dict], batch_size: int = 100) -> tuple:
    """Faz upload das vagas em lotes"""
    total_jobs = len(jobs)
    uploaded_count = 0
    failed_count = 0
    duplicates_skipped = 0
    
    # Conjunto para rastrear IDs externos já processados
    processed_external_ids: Set[str] = set()
    
    for i in range(0, total_jobs, batch_size):
        batch = jobs[i:i + batch_size]
        batch_data = []
        
        # Processar cada vaga no lote
        for job in batch:
            try:
                vaga_data = map_job_to_vagas_format(job)
                
                # Verificar duplicatas
                if vaga_data['external_id'] in processed_external_ids:
                    duplicates_skipped += 1
                    continue
                
                processed_external_ids.add(vaga_data['external_id'])
                batch_data.append(vaga_data)
                
            except Exception as e:
                print(f"Erro ao processar vaga: {e}")
                failed_count += 1
                continue
        
        # Upload do lote
        if batch_data:
            try:
                result = supabase.table('vagas').insert(batch_data).execute()
                uploaded_count += len(batch_data)
                print(f"Lote {i//batch_size + 1}: {len(batch_data)} vagas enviadas com sucesso")
            except Exception as e:
                print(f"Erro no lote {i//batch_size + 1}: {e}")
                # Tentar upload individual para identificar problemas específicos
                for individual_job in batch_data:
                    try:
                        supabase.table('vagas').insert([individual_job]).execute()
                        uploaded_count += 1
                    except Exception as individual_error:
                        print(f"Erro individual para vaga {individual_job.get('external_id', 'unknown')}: {individual_error}")
                        failed_count += 1
    
    return uploaded_count, failed_count, duplicates_skipped

def verify_upload(supabase: Client) -> int:
    """Verifica quantas vagas foram inseridas"""
    try:
        result = supabase.table('vagas').select('id', count='exact').execute()
        count = result.count if hasattr(result, 'count') else len(result.data)
        print(f"Total de vagas na tabela: {count}")
        return count
    except Exception as e:
        print(f"Erro ao verificar upload: {e}")
        return 0

def main():
    """Função principal"""
    print("=== Processamento Melhorado de Vagas ===")
    
    # Conectar ao Supabase
    supabase = connect_supabase()
    print("Conectado ao Supabase")
    
    # Limpar tabela
    if not clear_vagas_table(supabase):
        print("Falha ao limpar tabela. Abortando.")
        return
    
    # Carregar vagas
    file_path = "vagas_todos_setores_estruturadas_completo.jsonl"
    jobs = load_jobs_from_jsonl(file_path)
    
    if not jobs:
        print("Nenhuma vaga carregada. Abortando.")
        return
    
    print(f"Processando {len(jobs)} vagas...")
    
    # Upload em lotes
    uploaded, failed, duplicates = upload_jobs_in_batches(supabase, jobs)
    
    # Verificar resultado
    final_count = verify_upload(supabase)
    
    # Relatório final
    print("\n=== RELATÓRIO FINAL ===")
    print(f"Vagas processadas: {len(jobs)}")
    print(f"Vagas enviadas com sucesso: {uploaded}")
    print(f"Vagas com falha: {failed}")
    print(f"Duplicatas ignoradas: {duplicates}")
    print(f"Total na tabela: {final_count}")
    
if __name__ == "__main__":
    main()