import json
import random
from typing import Dict, List, Any

def load_jsonl(file_path: str) -> List[Dict[str, Any]]:
    """Carrega dados do arquivo JSONL"""
    jobs = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                jobs.append(json.loads(line.strip()))
    return jobs

def save_jsonl(jobs: List[Dict[str, Any]], file_path: str):
    """Salva dados no arquivo JSONL"""
    with open(file_path, 'w', encoding='utf-8') as f:
        for job in jobs:
            f.write(json.dumps(job, ensure_ascii=False) + '\n')

def generate_responsibilities_by_title(titulo: str, setor: str) -> List[str]:
    """Gera responsabilidades específicas baseadas no título da vaga"""
    
    # Dicionário de responsabilidades por palavras-chave do título
    responsibilities_map = {
        # Serviço Social
        'ajudante geral': [
            "Auxiliar nas atividades administrativas e operacionais do setor",
            "Organizar e manter limpo o ambiente de trabalho",
            "Apoiar a equipe em tarefas diversas conforme demanda",
            "Receber e conferir materiais e documentos"
        ],
        'coordenador': [
            "Coordenar e supervisionar equipes de trabalho",
            "Desenvolver estratégias e planos de ação para o setor",
            "Monitorar indicadores de desempenho e resultados",
            "Realizar reuniões periódicas com a equipe",
            "Elaborar relatórios gerenciais e de acompanhamento"
        ],
        'assistente social': [
            "Realizar atendimentos individuais e familiares",
            "Elaborar estudos sociais e pareceres técnicos",
            "Desenvolver projetos de intervenção social",
            "Articular com rede de serviços e políticas públicas",
            "Registrar atendimentos em sistema específico"
        ],
        'cuidador': [
            "Prestar cuidados básicos a pessoas em situação de vulnerabilidade",
            "Acompanhar atividades da vida diária dos assistidos",
            "Observar e relatar mudanças no estado dos cuidados",
            "Auxiliar em atividades de higiene e alimentação"
        ],
        'monitor': [
            "Acompanhar e orientar participantes em atividades específicas",
            "Desenvolver dinâmicas e atividades educativas",
            "Registrar frequência e participação dos usuários",
            "Zelar pela segurança durante as atividades"
        ],
        'mediador': [
            "Facilitar processos de comunicação e resolução de conflitos",
            "Conduzir sessões de mediação entre partes envolvidas",
            "Promover diálogo construtivo e busca por soluções",
            "Elaborar acordos e termos de compromisso"
        ],
        'educador': [
            "Planejar e executar atividades educativas e pedagógicas",
            "Acompanhar o desenvolvimento dos educandos",
            "Elaborar materiais didáticos e recursos educacionais",
            "Participar de formações e capacitações continuadas"
        ],
        
        # Telecomunicações
        'analista': [
            "Analisar sistemas e processos técnicos da área",
            "Elaborar documentação técnica e relatórios especializados",
            "Identificar melhorias e otimizações nos processos",
            "Prestar suporte técnico especializado",
            "Participar de projetos de implementação e melhoria"
        ],
        'tecnico': [
            "Executar manutenção preventiva e corretiva em equipamentos",
            "Realizar instalações e configurações técnicas",
            "Diagnosticar e solucionar problemas técnicos",
            "Registrar atividades em sistema de controle",
            "Seguir procedimentos de segurança estabelecidos"
        ],
        'fiscal': [
            "Fiscalizar cumprimento de normas e regulamentações",
            "Realizar inspeções técnicas em campo",
            "Elaborar relatórios de fiscalização e não conformidades",
            "Orientar sobre adequações necessárias",
            "Acompanhar processos de regularização"
        ],
        
        # Comunicação e Marketing
        'social media': [
            "Criar e gerenciar conteúdo para redes sociais",
            "Desenvolver estratégias de engajamento digital",
            "Monitorar métricas e performance das publicações",
            "Interagir com seguidores e responder comentários",
            "Produzir materiais visuais e audiovisuais"
        ],
        'auxiliar de festas': [
            "Auxiliar na organização e montagem de eventos",
            "Apoiar no atendimento aos convidados durante eventos",
            "Organizar materiais e equipamentos para festas",
            "Auxiliar na decoração e ambientação do local"
        ],
        'atendimento': [
            "Realizar atendimento ao cliente de forma cordial e eficiente",
            "Esclarecer dúvidas sobre produtos e serviços",
            "Registrar solicitações e reclamações dos clientes",
            "Encaminhar demandas para setores competentes"
        ],
        'comunicacao': [
            "Desenvolver estratégias de comunicação interna e externa",
            "Produzir conteúdo para diferentes canais de comunicação",
            "Gerenciar relacionamento com imprensa e mídia",
            "Coordenar campanhas publicitárias e promocionais"
        ],
        'marketing': [
            "Desenvolver estratégias de marketing e posicionamento",
            "Analisar mercado e comportamento do consumidor",
            "Criar campanhas promocionais e publicitárias",
            "Gerenciar orçamento de marketing e ROI",
            "Coordenar ações de trade marketing"
        ],
        'promotor': [
            "Promover produtos e serviços em pontos de venda",
            "Realizar demonstrações e degustações",
            "Negociar espaços e exposições nos estabelecimentos",
            "Coletar informações sobre concorrência e mercado"
        ],
        'locutor': [
            "Apresentar programas de rádio ou eventos",
            "Preparar roteiros e pautas para apresentações",
            "Conduzir entrevistas e debates",
            "Operar equipamentos de áudio quando necessário"
        ],
        'eventos': [
            "Planejar e coordenar eventos corporativos e sociais",
            "Gerenciar fornecedores e prestadores de serviços",
            "Acompanhar montagem e execução dos eventos",
            "Controlar orçamento e cronograma de atividades"
        ],
        'especialista': [
            "Desenvolver expertise técnica na área de atuação",
            "Prestar consultoria especializada interna e externa",
            "Participar de projetos estratégicos da empresa",
            "Capacitar equipes em conhecimentos específicos"
        ],
        
        # Arquitetura e Design
        'projetista': [
            "Desenvolver projetos técnicos conforme especificações",
            "Elaborar desenhos técnicos e plantas detalhadas",
            "Calcular materiais e dimensionamentos necessários",
            "Acompanhar execução e implementação dos projetos",
            "Revisar e atualizar projetos conforme necessidades"
        ],
        'designer': [
            "Criar identidade visual e materiais gráficos",
            "Desenvolver layouts para diferentes mídias",
            "Elaborar apresentações visuais e mockups",
            "Seguir manual de marca e diretrizes visuais",
            "Colaborar com equipes multidisciplinares"
        ],
        'desenhista': [
            "Elaborar desenhos técnicos e ilustrações",
            "Criar representações gráficas de projetos",
            "Utilizar softwares específicos de desenho",
            "Revisar e corrigir desenhos conforme orientações"
        ],
        'produtor': [
            "Coordenar produção de conteúdo ou eventos",
            "Gerenciar cronogramas e recursos disponíveis",
            "Articular com diferentes profissionais e fornecedores",
            "Acompanhar qualidade e prazos de entrega"
        ]
    }
    
    # Busca responsabilidades baseadas em palavras-chave do título
    titulo_lower = titulo.lower()
    selected_responsibilities = []
    
    for keyword, responsibilities in responsibilities_map.items():
        if keyword in titulo_lower:
            selected_responsibilities.extend(responsibilities)
            break
    
    # Se não encontrou correspondência específica, usa responsabilidades genéricas do setor
    if not selected_responsibilities:
        if 'social' in setor.lower():
            selected_responsibilities = [
                "Executar atividades relacionadas ao serviço social",
                "Atender demandas específicas da área de atuação",
                "Participar de reuniões e capacitações da equipe"
            ]
        elif 'comunicacao' in setor.lower() or 'marketing' in setor.lower():
            selected_responsibilities = [
                "Desenvolver estratégias de comunicação",
                "Criar conteúdo para diferentes canais",
                "Apoiar ações de marketing e divulgação"
            ]
        elif 'telecomunicacoes' in setor.lower():
            selected_responsibilities = [
                "Executar atividades técnicas de telecomunicações",
                "Manter equipamentos e sistemas funcionais",
                "Prestar suporte técnico especializado"
            ]
        elif 'arquitetura' in setor.lower() or 'design' in setor.lower():
            selected_responsibilities = [
                "Desenvolver projetos criativos e funcionais",
                "Elaborar soluções visuais e técnicas",
                "Acompanhar tendências da área"
            ]
        else:
            selected_responsibilities = [
                "Executar atividades específicas da função",
                "Cumprir metas e objetivos estabelecidos",
                "Manter qualidade nos serviços prestados"
            ]
    
    # Retorna uma seleção aleatória de 2-4 responsabilidades
    num_responsibilities = min(len(selected_responsibilities), random.randint(2, 4))
    return random.sample(selected_responsibilities, num_responsibilities)

def generate_skills_by_title(titulo: str, setor: str) -> List[str]:
    """Gera habilidades específicas baseadas no título da vaga"""
    
    skills_map = {
        # Serviço Social
        'ajudante geral': ["Organização", "Proatividade", "Trabalho em equipe", "Flexibilidade", "Atenção aos detalhes"],
        'coordenador': ["Liderança", "Gestão de equipes", "Planejamento estratégico", "Comunicação", "Tomada de decisão"],
        'assistente social': ["Escuta ativa", "Empatia", "Conhecimento em políticas públicas", "Elaboração de relatórios", "Ética profissional"],
        'cuidador': ["Paciência", "Cuidado", "Observação", "Responsabilidade", "Sensibilidade"],
        'monitor': ["Dinamismo", "Criatividade", "Controle de grupo", "Educação", "Adaptabilidade"],
        'mediador': ["Imparcialidade", "Comunicação assertiva", "Resolução de conflitos", "Negociação", "Diplomacia"],
        'educador': ["Didática", "Paciência", "Criatividade pedagógica", "Conhecimento educacional", "Motivação"],
        
        # Telecomunicações
        'analista': ["Análise crítica", "Conhecimento técnico", "Resolução de problemas", "Documentação", "Metodologia"],
        'tecnico': ["Conhecimento técnico", "Manutenção", "Diagnóstico", "Precisão", "Segurança no trabalho"],
        'fiscal': ["Atenção aos detalhes", "Conhecimento regulatório", "Imparcialidade", "Comunicação", "Organização"],
        
        # Comunicação e Marketing
        'social media': ["Criatividade digital", "Conhecimento em redes sociais", "Edição de conteúdo", "Análise de métricas", "Tendências digitais"],
        'auxiliar de festas': ["Organização de eventos", "Atendimento ao cliente", "Trabalho sob pressão", "Flexibilidade", "Proatividade"],
        'atendimento': ["Comunicação", "Paciência", "Resolução de problemas", "Empatia", "Organização"],
        'comunicacao': ["Redação", "Criatividade", "Relacionamento interpessoal", "Estratégia", "Multimídia"],
        'marketing': ["Estratégia de marketing", "Análise de mercado", "Criatividade", "Gestão de campanhas", "ROI"],
        'promotor': ["Vendas", "Persuasão", "Relacionamento", "Conhecimento de produto", "Negociação"],
        'locutor': ["Oratória", "Dicção", "Improvisação", "Conhecimento geral", "Carisma"],
        'eventos': ["Organização", "Gestão de projetos", "Negociação", "Multitarefa", "Relacionamento"],
        'especialista': ["Expertise técnica", "Consultoria", "Análise estratégica", "Liderança técnica", "Inovação"],
        
        # Arquitetura e Design
        'projetista': ["AutoCAD", "Desenho técnico", "Cálculos estruturais", "Normas técnicas", "Precisão"],
        'designer': ["Adobe Creative Suite", "Criatividade", "Senso estético", "Tendências visuais", "Comunicação visual"],
        'desenhista': ["Desenho técnico", "Softwares CAD", "Precisão", "Atenção aos detalhes", "Interpretação de projetos"],
        'produtor': ["Gestão de produção", "Coordenação", "Cronogramas", "Qualidade", "Relacionamento"]
    }
    
    # Busca habilidades baseadas em palavras-chave do título
    titulo_lower = titulo.lower()
    selected_skills = []
    
    for keyword, skills in skills_map.items():
        if keyword in titulo_lower:
            selected_skills.extend(skills)
            break
    
    # Se não encontrou correspondência específica, usa habilidades genéricas
    if not selected_skills:
        selected_skills = ["Comunicação", "Trabalho em equipe", "Responsabilidade", "Proatividade", "Organização"]
    
    # Retorna uma seleção aleatória de 3-5 habilidades
    num_skills = min(len(selected_skills), random.randint(3, 5))
    return random.sample(selected_skills, num_skills)

def generate_description(titulo: str, responsabilidades: List[str], habilidades: List[str]) -> str:
    """Gera descrição completa única para cada vaga"""
    
    # Templates de descrição variados
    templates = [
        f"Oportunidade para {titulo.lower()} com foco em {responsabilidades[0].lower()}. Buscamos profissional com {', '.join(habilidades[:2]).lower()} para integrar nossa equipe.",
        f"Vaga de {titulo.lower()} para profissional que deseje {responsabilidades[0].lower()}. Valorizamos {' e '.join(habilidades[:2]).lower()} no desenvolvimento das atividades.",
        f"Estamos contratando {titulo.lower()} para {responsabilidades[0].lower()}. Requisitos essenciais: {', '.join(habilidades[:3]).lower()}.",
        f"Posição de {titulo.lower()} com responsabilidade de {responsabilidades[0].lower()}. Oferecemos ambiente colaborativo para profissionais com {' e '.join(habilidades[:2]).lower()}.",
        f"Procuramos {titulo.lower()} para {responsabilidades[0].lower()}. Ideal para profissionais com experiência em {', '.join(habilidades[:2]).lower()}."
    ]
    
    # Seleciona template aleatório
    template = random.choice(templates)
    
    return template

def process_jobs(input_file: str, output_file: str):
    """Processa todas as vagas gerando conteúdo único"""
    
    print(f"Carregando vagas de {input_file}...")
    jobs = load_jsonl(input_file)
    
    print(f"Processando {len(jobs)} vagas...")
    
    processed_jobs = []
    stats = {
        'total_processed': 0,
        'unique_responsibilities': set(),
        'unique_skills': set(),
        'unique_descriptions': set()
    }
    
    for job in jobs:
        # Extrai informações básicas
        titulo = job['informacoes_basicas']['titulo_vaga']
        setor = job['informacoes_basicas']['setor']
        
        # Gera conteúdo único
        new_responsibilities = generate_responsibilities_by_title(titulo, setor)
        new_skills = generate_skills_by_title(titulo, setor)
        new_description = generate_description(titulo, new_responsibilities, new_skills)
        
        # Atualiza o job
        job['responsabilidades'] = new_responsibilities
        job['habilidades_requeridas'] = new_skills
        job['descricao_completa'] = {
            'texto_completo': f"Vaga: {titulo} | Responsabilidades: {'; '.join(new_responsibilities)} | Descrição: {new_description}"
        }
        
        # Atualiza estatísticas
        stats['unique_responsibilities'].update(new_responsibilities)
        stats['unique_skills'].update(new_skills)
        stats['unique_descriptions'].add(new_description)
        stats['total_processed'] += 1
        
        processed_jobs.append(job)
    
    # Salva arquivo processado
    print(f"Salvando vagas processadas em {output_file}...")
    save_jsonl(processed_jobs, output_file)
    
    # Gera relatório
    report = {
        'total_vagas_processadas': stats['total_processed'],
        'responsabilidades_unicas': len(stats['unique_responsibilities']),
        'habilidades_unicas': len(stats['unique_skills']),
        'descricoes_unicas': len(stats['unique_descriptions']),
        'percentual_unicidade_descricoes': (len(stats['unique_descriptions']) / stats['total_processed']) * 100,
        'amostra_responsabilidades': list(stats['unique_responsibilities'])[:20],
        'amostra_habilidades': list(stats['unique_skills'])[:20],
        'amostra_descricoes': list(stats['unique_descriptions'])[:10]
    }
    
    with open('relatorio_unicidade_completa.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n=== RELATÓRIO DE PROCESSAMENTO ===")
    print(f"Total de vagas processadas: {report['total_vagas_processadas']}")
    print(f"Responsabilidades únicas geradas: {report['responsabilidades_unicas']}")
    print(f"Habilidades únicas geradas: {report['habilidades_unicas']}")
    print(f"Descrições únicas geradas: {report['descricoes_unicas']}")
    print(f"Percentual de unicidade das descrições: {report['percentual_unicidade_descricoes']:.1f}%")
    print(f"\nRelatório detalhado salvo em: relatorio_unicidade_completa.json")
    print(f"Arquivo final salvo em: {output_file}")

if __name__ == "__main__":
    input_file = "vagas_separadas_final.jsonl"
    output_file = "vagas_unicas_completas.jsonl"
    
    process_jobs(input_file, output_file)