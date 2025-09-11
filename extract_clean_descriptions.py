import json
import re
from collections import defaultdict, Counter

def extract_text_from_complex_field(field_value):
    """Extrai texto limpo de campos complexos"""
    if isinstance(field_value, str):
        return field_value.strip()
    
    if isinstance(field_value, dict):
        # Se for um dicionário, procurar por campos de texto
        text_fields = ['texto_completo', 'descricao', 'requisitos_texto_original', 'texto', 'content']
        for field in text_fields:
            if field in field_value and field_value[field]:
                text = str(field_value[field])
                if len(text) > 50:  # Apenas textos significativos
                    return text.strip()
        
        # Se não encontrou, tentar concatenar valores de string
        text_parts = []
        for key, value in field_value.items():
            if isinstance(value, str) and len(value) > 20:
                text_parts.append(value)
        
        if text_parts:
            return ' | '.join(text_parts[:3])  # Limitar a 3 partes
    
    if isinstance(field_value, list):
        # Se for uma lista, pegar os primeiros elementos de texto
        text_parts = []
        for item in field_value[:3]:  # Limitar a 3 itens
            if isinstance(item, str) and len(item) > 20:
                text_parts.append(item)
        
        if text_parts:
            return ' | '.join(text_parts)
    
    return str(field_value)[:200] if field_value else "Descrição não disponível"

def clean_extracted_text(text):
    """Limpa o texto extraído removendo padrões repetitivos"""
    if not text or len(text) < 10:
        return "Descrição não disponível"
    
    # Remover padrões comuns de formatação
    patterns_to_remove = [
        r'CANDIDATURA FÁCIL\s*',
        r'Empresa Confidencial\s*',
        r'Por que\?.*?muito ativo\s*',
        r'A combinar\s*',
        r'\d+\s*vaga[s]?:.*?\(\d+\)\s*',
        r'Publicada em \d{2}/\d{2}\s*',
        r'Atualizada em \d{2}/\d{2}\s*',
        r'De R\$.*?a R\$.*?\s*',
        r'Até R\$.*?\s*',
        r'\{.*?\}',  # Remove objetos JSON
        r'\[.*?\]',  # Remove arrays
    ]
    
    cleaned = text
    for pattern in patterns_to_remove:
        cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
    
    # Limpar separadores múltiplos
    cleaned = re.sub(r'\s*\|\s*', ' | ', cleaned)
    cleaned = re.sub(r'\s+', ' ', cleaned)
    cleaned = cleaned.strip()
    
    # Se ficou muito curto, tentar usar partes do texto original
    if len(cleaned) < 30 and len(text) > 30:
        # Pegar a primeira parte significativa
        sentences = text.split('|')
        for sentence in sentences:
            clean_sentence = re.sub(r'[{}\[\]"\']', '', sentence).strip()
            if len(clean_sentence) > 30:
                return clean_sentence[:300]
    
    return cleaned[:300] if cleaned else "Descrição não disponível"

def extract_individual_descriptions():
    """Extrai descrições individuais de cada segmento das vagas"""
    input_file = 'vagas_todos_setores_estruturadas_completo.jsonl'
    output_file = 'vagas_descricoes_individuais.jsonl'
    
    print(f"Extraindo descrições individuais de {input_file}...")
    
    individual_jobs = []
    sector_descriptions = defaultdict(set)
    
    with open(input_file, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            try:
                job_data = json.loads(line.strip())
                
                # Extrair informações básicas
                base_info = {
                    'setor': job_data.get('setor', 'Não informado'),
                    'localizacao': extract_location(job_data.get('localizacao', {})),
                    'salario': job_data.get('salario', 'A combinar'),
                    'tipo_contrato': job_data.get('tipo_contrato', 'Não informado')
                }
                
                # Verificar se há segmentos separados na descrição
                descricao_field = job_data.get('descricao', {})
                
                if isinstance(descricao_field, dict) and 'segmentos_separados' in descricao_field:
                    # Processar cada segmento como uma vaga separada
                    segments = descricao_field['segmentos_separados']
                    
                    for i, segment in enumerate(segments):
                        if isinstance(segment, str) and len(segment.strip()) > 30:
                            clean_desc = clean_extracted_text(segment)
                            
                            # Verificar se já existe no setor
                            if clean_desc not in sector_descriptions[base_info['setor']]:
                                sector_descriptions[base_info['setor']].add(clean_desc)
                                
                                # Extrair título e empresa do segmento
                                titulo, empresa = extract_title_and_company(segment)
                                
                                individual_job = {
                                    'titulo': titulo,
                                    'empresa': empresa,
                                    'setor': base_info['setor'],
                                    'localizacao': base_info['localizacao'],
                                    'descricao': clean_desc,
                                    'salario': base_info['salario'],
                                    'tipo_contrato': base_info['tipo_contrato'],
                                    'nivel_experiencia': 'Não informado',
                                    'data_publicacao': 'Não informada'
                                }
                                
                                individual_jobs.append(individual_job)
                else:
                    # Processar como vaga única
                    clean_desc = extract_text_from_complex_field(descricao_field)
                    clean_desc = clean_extracted_text(clean_desc)
                    
                    if clean_desc not in sector_descriptions[base_info['setor']]:
                        sector_descriptions[base_info['setor']].add(clean_desc)
                        
                        titulo, empresa = extract_title_and_company_from_job(job_data)
                        
                        individual_job = {
                            'titulo': titulo,
                            'empresa': empresa,
                            'setor': base_info['setor'],
                            'localizacao': base_info['localizacao'],
                            'descricao': clean_desc,
                            'salario': base_info['salario'],
                            'tipo_contrato': base_info['tipo_contrato'],
                            'nivel_experiencia': 'Não informado',
                            'data_publicacao': 'Não informada'
                        }
                        
                        individual_jobs.append(individual_job)
                
                if line_num % 50 == 0:
                    print(f"Processadas {line_num} vagas originais, geradas {len(individual_jobs)} vagas individuais...")
                    
            except json.JSONDecodeError as e:
                print(f"Erro ao processar linha {line_num}: {e}")
                continue
    
    # Salvar vagas individuais
    with open(output_file, 'w', encoding='utf-8') as f:
        for job in individual_jobs:
            f.write(json.dumps(job, ensure_ascii=False) + '\n')
    
    print(f"\nExtração concluída!")
    print(f"Vagas originais processadas: {line_num}")
    print(f"Vagas individuais geradas: {len(individual_jobs)}")
    print(f"Arquivo salvo: {output_file}")
    
    # Estatísticas por setor
    print(f"\n=== ESTATÍSTICAS POR SETOR ====")
    for setor, descriptions in sector_descriptions.items():
        total_jobs = sum(1 for job in individual_jobs if job['setor'] == setor)
        diversity_rate = len(descriptions) / total_jobs * 100 if total_jobs > 0 else 0
        print(f"{setor}: {total_jobs} vagas, {len(descriptions)} descrições únicas ({diversity_rate:.1f}% diversidade)")
    
    return individual_jobs

def extract_location(location_data):
    """Extrai localização de forma limpa"""
    if isinstance(location_data, dict):
        cidade = location_data.get('cidade_extraida', '')
        estado = location_data.get('estado_extraido', '')
        if cidade and estado:
            return f"{cidade}, {estado}"
        elif cidade:
            return cidade
        elif estado:
            return estado
    
    if isinstance(location_data, str):
        return location_data
    
    return "Localização não informada"

def extract_title_and_company(segment_text):
    """Extrai título e empresa de um segmento de texto"""
    # Procurar por padrões de empresa
    company_patterns = [
        r'([A-Z][A-Z\s&]+(?:LTDA|S\.A\.|EIRELI|ME|HOSPITAL|CLINICA|EMPRESA))',
        r'Unidade:\s*([^-]+)',
        r'EMPRESA[^:]*:\s*([^\n]+)',
    ]
    
    empresa = "Empresa não informada"
    for pattern in company_patterns:
        match = re.search(pattern, segment_text, re.IGNORECASE)
        if match:
            empresa = match.group(1).strip()
            break
    
    # Extrair título (primeiras palavras significativas)
    words = segment_text.split()
    title_words = []
    for word in words[:10]:  # Primeiras 10 palavras
        clean_word = re.sub(r'[^a-zA-ZÀ-ÿ\s]', '', word)
        if len(clean_word) > 2 and clean_word.lower() not in ['unidade', 'hospital', 'empresa']:
            title_words.append(clean_word)
        if len(title_words) >= 3:
            break
    
    titulo = ' '.join(title_words) if title_words else "Título não informado"
    
    return titulo, empresa

def extract_title_and_company_from_job(job_data):
    """Extrai título e empresa dos dados da vaga"""
    titulo = job_data.get('titulo', 'Título não informado')
    empresa = job_data.get('empresa', 'Empresa não informada')
    
    if titulo == 'Título não informado' or not titulo:
        # Tentar extrair do campo descrição
        desc = job_data.get('descricao', {})
        if isinstance(desc, dict) and 'texto_completo' in desc:
            titulo, _ = extract_title_and_company(str(desc['texto_completo']))
    
    return titulo, empresa

if __name__ == "__main__":
    print("Iniciando extração de descrições individuais...")
    individual_jobs = extract_individual_descriptions()
    print("\n✅ Extração concluída com sucesso!")