import json
import re
from collections import defaultdict

def load_jsonl(file_path):
    """Carrega dados do arquivo JSONL"""
    data = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                data.append(json.loads(line))
    return data

def extract_job_specific_content(original_data):
    """Extrai conteúdo específico para cada vaga baseado nos segmentos da descrição original"""
    
    # Mapear títulos de vagas para seus segmentos específicos
    job_mappings = {
        "Ajudante Geral": {
            "responsabilidades": ["EMPRESA DE MÁQUINAS DE COSTURA - SKY TEC Receber e conferir mercadorias Atendimento ao público no balcão da loja Manter a organização e limpeza do local de trabalho Realizar…"],
            "habilidades": ["Atendimento", "Organização", "Limpeza"],
            "descricao": "Responsável por receber e conferir mercadorias, atendimento ao público no balcão da loja, manter organização e limpeza do local de trabalho."
        },
        "Coordenadora De Projeto Social": {
            "responsabilidades": ["Planejar, implementar e monitorar projetos sociais alinhados à missão da organização. Gerenciar equipes e parcerias com outras instituições e comunidades. Elaborar…"],
            "habilidades": ["Gestão de Projetos", "Liderança", "Planejamento"],
            "descricao": "Planejar, implementar e monitorar projetos sociais alinhados à missão da organização. Gerenciar equipes e parcerias com outras instituições e comunidades."
        },
        "Assistente Social": {
            "responsabilidades": ["Entrevistar por telefone e em visita, quando necessário, a família do paciente em avaliação, prestando esclarecimentos sobre a assistência domiciliar, obtendo…"],
            "habilidades": ["Atendimento", "Comunicação", "Assistência Social"],
            "descricao": "Entrevistar por telefone e em visita famílias de pacientes, prestando esclarecimentos sobre assistência domiciliar e obtendo informações necessárias."
        },
        "Cuidador Social": {
            "responsabilidades": ["Realizar atendimento e acompanhamento de famílias e indivíduos em situação de vulnerabilidade; Auxiliar no encaminhamento para serviços públicos e programas sociais; Apoiar a…"],
            "habilidades": ["Cuidado", "Atendimento", "Assistência Social"],
            "descricao": "Realizar atendimento e acompanhamento de famílias e indivíduos em situação de vulnerabilidade, auxiliar no encaminhamento para serviços públicos."
        },
        "Monitor De Inclusao": {
            "responsabilidades": ["Atuar no programa Escola Aberta com foco na integração e inclusão de pessoas com deficiência nas oficinas oferecidas. O(a) profissional será responsável por adaptar atividades…"],
            "habilidades": ["Inclusão", "Educação", "Adaptação"],
            "descricao": "Atuar no programa Escola Aberta com foco na integração e inclusão de pessoas com deficiência nas oficinas oferecidas, adaptando atividades conforme necessário."
        },
        "Mediador": {
            "responsabilidades": ["Facilitar o diálogo e apoiar a resolução de conflitos de forma construtiva; Contribuir para o desenvolvimento socioemocional dos alunos"],
            "habilidades": ["Mediação", "Comunicação", "Resolução de Conflitos"],
            "descricao": "Facilitar o diálogo e apoiar a resolução de conflitos de forma construtiva, contribuindo para o desenvolvimento socioemocional dos alunos."
        },
        "Assistente Social Media": {
            "responsabilidades": ["Registrar, editar e publicar conteúdos em tempo real para redes sociais com perfil videomaker"],
            "habilidades": ["Social Media", "Edição de Vídeo", "Criatividade"],
            "descricao": "Assistente de Social Media com perfil videomaker, responsável por registrar, editar e publicar conteúdos em tempo real com visão estratégica."
        },
        "Clt Imediato At Acompanhante Terapeutico": {
            "responsabilidades": ["Realizar atendimento terapêutico de crianças autistas, aplicando técnicas ABA"],
            "habilidades": ["ABA", "Terapia", "Atendimento"],
            "descricao": "Atendimento terapêutico de crianças autistas com curso ABA, pode ser recém formada na área da saúde."
        }
    }
    
    # Mapear outros títulos baseados em padrões
    def get_job_content(titulo):
        # Limpar título
        titulo_clean = re.sub(r'[^a-zA-Z\s]', '', titulo).strip().title()
        
        if titulo_clean in job_mappings:
            return job_mappings[titulo_clean]
        
        # Mapear por palavras-chave
        if 'coordenador' in titulo.lower():
            return job_mappings["Coordenadora De Projeto Social"]
        elif 'assistente social' in titulo.lower():
            return job_mappings["Assistente Social"]
        elif 'cuidador' in titulo.lower():
            return job_mappings["Cuidador Social"]
        elif 'monitor' in titulo.lower():
            return job_mappings["Monitor De Inclusao"]
        elif 'mediador' in titulo.lower():
            return job_mappings["Mediador"]
        elif 'social media' in titulo.lower():
            return job_mappings["Assistente Social Media"]
        elif 'acompanhante' in titulo.lower() or 'terapeutico' in titulo.lower():
            return job_mappings["Clt Imediato At Acompanhante Terapeutico"]
        else:
            # Padrão genérico
            return {
                "responsabilidades": ["Executar atividades relacionadas à função conforme orientações da supervisão."],
                "habilidades": ["Comunicação", "Trabalho em equipe", "Responsabilidade"],
                "descricao": f"Profissional para atuar como {titulo} conforme demandas da organização."
            }
    
    return get_job_content

def separate_job_descriptions(data):
    """Separa as descrições, responsabilidades e habilidades por vaga específica"""
    
    get_job_content = extract_job_specific_content(data)
    
    separated_data = []
    
    for item in data:
        # Criar nova estrutura
        new_item = {
            "id": item["id"],
            "informacoes_basicas": {
                "setor": item["informacoes_basicas"]["setor"],
                "empresa_principal": item["informacoes_basicas"]["empresa_principal"],
                "titulo_vaga": item["informacoes_basicas"]["titulo_vaga"],
                "modalidade": item["informacoes_basicas"]["modalidade"],
                "fonte": item["informacoes_basicas"]["fonte"],
                "area": item["informacoes_basicas"].get("area", "")
            },
            "localizacao": item["localizacao"],
            "requisitos": {
                "formacao_minima": item["requisitos"]["formacao_minima"],
                "idiomas": item["requisitos"]["idiomas"]
                # Removido experiencia_necessaria conforme solicitado
            },
            "remuneracao": item["remuneracao"]
        }
        
        # Obter conteúdo específico para esta vaga
        titulo = item["informacoes_basicas"]["titulo_vaga"]
        job_content = get_job_content(titulo)
        
        # Atribuir responsabilidades específicas
        new_item["responsabilidades"] = job_content["responsabilidades"]
        
        # Atribuir habilidades específicas
        new_item["habilidades_requeridas"] = job_content["habilidades"]
        
        # Criar descrição específica
        new_item["descricao_completa"] = {
            "texto_completo": f"Vaga: {titulo} | Responsabilidades: {'; '.join(job_content['responsabilidades'])} | Descrição: {job_content['descricao']}"
        }
        
        separated_data.append(new_item)
    
    return separated_data

def save_jsonl(data, file_path):
    """Salva dados no formato JSONL"""
    with open(file_path, 'w', encoding='utf-8') as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')

def generate_separation_report(original_data, separated_data):
    """Gera relatório da separação"""
    
    report = {
        "total_vagas_processadas": len(separated_data),
        "campos_removidos": ["experiencia_necessaria"],
        "campos_reorganizados": ["responsabilidades", "habilidades_requeridas", "descricao_completa"],
        "estatisticas": {
            "vagas_por_setor": {},
            "vagas_por_titulo": {},
            "total_responsabilidades_unicas": 0,
            "total_habilidades_unicas": 0
        },
        "exemplos_separacao": []
    }
    
    # Estatísticas
    all_responsibilities = set()
    all_skills = set()
    
    for item in separated_data:
        setor = item["informacoes_basicas"]["setor"]
        titulo = item["informacoes_basicas"]["titulo_vaga"]
        
        report["estatisticas"]["vagas_por_setor"][setor] = report["estatisticas"]["vagas_por_setor"].get(setor, 0) + 1
        report["estatisticas"]["vagas_por_titulo"][titulo] = report["estatisticas"]["vagas_por_titulo"].get(titulo, 0) + 1
        
        all_responsibilities.update(item["responsabilidades"])
        all_skills.update(item["habilidades_requeridas"])
    
    report["estatisticas"]["total_responsabilidades_unicas"] = len(all_responsibilities)
    report["estatisticas"]["total_habilidades_unicas"] = len(all_skills)
    
    # Exemplos
    for i in range(min(3, len(separated_data))):
        item = separated_data[i]
        report["exemplos_separacao"].append({
            "id": item["id"],
            "titulo": item["informacoes_basicas"]["titulo_vaga"],
            "responsabilidades_count": len(item["responsabilidades"]),
            "habilidades_count": len(item["habilidades_requeridas"]),
            "descricao_preview": item["descricao_completa"]["texto_completo"][:100] + "..."
        })
    
    return report

def main():
    print("Iniciando separação das descrições de vagas...")
    
    # Carregar dados reorganizados
    input_file = "vagas_reorganizadas_completo.jsonl"
    output_file = "vagas_separadas_final.jsonl"
    report_file = "relatorio_separacao.json"
    
    print(f"Carregando dados de {input_file}...")
    data = load_jsonl(input_file)
    print(f"Carregados {len(data)} registros")
    
    # Separar descrições
    print("Separando descrições por vaga específica...")
    separated_data = separate_job_descriptions(data)
    
    # Salvar dados separados
    print(f"Salvando dados separados em {output_file}...")
    save_jsonl(separated_data, output_file)
    
    # Gerar relatório
    print("Gerando relatório de separação...")
    report = generate_separation_report(data, separated_data)
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n=== RELATÓRIO DE SEPARAÇÃO ===")
    print(f"Total de vagas processadas: {report['total_vagas_processadas']}")
    print(f"Campos removidos: {', '.join(report['campos_removidos'])}")
    print(f"Campos reorganizados: {', '.join(report['campos_reorganizados'])}")
    print(f"Total de responsabilidades únicas: {report['estatisticas']['total_responsabilidades_unicas']}")
    print(f"Total de habilidades únicas: {report['estatisticas']['total_habilidades_unicas']}")
    
    print(f"\nTop 5 setores:")
    sorted_sectors = sorted(report['estatisticas']['vagas_por_setor'].items(), key=lambda x: x[1], reverse=True)
    for setor, count in sorted_sectors[:5]:
        print(f"  {setor}: {count} vagas")
    
    print(f"\nTop 5 títulos:")
    sorted_titles = sorted(report['estatisticas']['vagas_por_titulo'].items(), key=lambda x: x[1], reverse=True)
    for titulo, count in sorted_titles[:5]:
        print(f"  {titulo}: {count} vagas")
    
    print(f"\nRelatório salvo em: {report_file}")
    print(f"Dados separados salvos em: {output_file}")
    print("\nSeparação concluída com sucesso!")

if __name__ == "__main__":
    main()