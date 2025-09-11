import json
import random
from collections import defaultdict

# Descrições específicas por setor
SETOR_DESCRIPTIONS = {
    'ServicoSocial': [
        'Atuar no desenvolvimento de políticas sociais e programas de assistência',
        'Realizar acompanhamento psicossocial de famílias e indivíduos',
        'Elaborar relatórios sociais e pareceres técnicos especializados',
        'Coordenar projetos de inclusão social e desenvolvimento comunitário',
        'Implementar programas de proteção social e direitos humanos'
    ],
    'Telecomunicacoes': [
        'Desenvolver e manter infraestrutura de redes de telecomunicações',
        'Implementar soluções tecnológicas para comunicação digital',
        'Gerenciar sistemas de transmissão de dados e voz',
        'Otimizar performance de redes e conectividade',
        'Prestar suporte técnico em tecnologias de comunicação'
    ],
    'Comunicacao e marketing': [
        'Desenvolver estratégias de comunicação e marketing digital',
        'Criar campanhas publicitárias e conteúdo para mídias sociais',
        'Gerenciar relacionamento com clientes e stakeholders',
        'Analisar métricas de performance e ROI de campanhas',
        'Coordenar eventos e ações promocionais da marca'
    ],
    'arquitetura e design': [
        'Desenvolver projetos arquitetônicos e de design de interiores',
        'Criar soluções espaciais funcionais e esteticamente atrativas',
        'Elaborar plantas técnicas e especificações de materiais',
        'Coordenar execução de obras e acompanhar cronogramas',
        'Realizar estudos de viabilidade e sustentabilidade ambiental'
    ],
    'Educacao': [
        'Desenvolver metodologias pedagógicas e planos de ensino',
        'Ministrar aulas e orientar processos de aprendizagem',
        'Avaliar desempenho acadêmico e elaborar relatórios educacionais',
        'Coordenar projetos educacionais e atividades extracurriculares',
        'Implementar tecnologias educacionais e recursos didáticos'
    ],
    'Administracao': [
        'Gerenciar processos administrativos e operacionais da organização',
        'Desenvolver políticas e procedimentos organizacionais',
        'Coordenar equipes e otimizar fluxos de trabalho',
        'Analisar indicadores de performance e produtividade',
        'Implementar sistemas de gestão e controle de qualidade'
    ]
}

# Responsabilidades específicas por setor
SETOR_RESPONSABILIDADES = {
    'ServicoSocial': [
        'Realizar diagnósticos sociais e elaborar planos de intervenção',
        'Acompanhar famílias em situação de vulnerabilidade social',
        'Articular redes de proteção social e parcerias institucionais',
        'Desenvolver projetos de inclusão e cidadania',
        'Orientar sobre direitos sociais e acesso a benefícios'
    ],
    'Telecomunicacoes': [
        'Configurar e manter equipamentos de telecomunicações',
        'Monitorar qualidade de sinal e performance da rede',
        'Implementar protocolos de segurança em comunicações',
        'Realizar testes de conectividade e troubleshooting',
        'Documentar procedimentos técnicos e manutenções'
    ],
    'Comunicacao e marketing': [
        'Elaborar estratégias de posicionamento de marca',
        'Produzir conteúdo para diferentes canais de comunicação',
        'Gerenciar campanhas de marketing digital e tradicional',
        'Analisar comportamento do consumidor e tendências de mercado',
        'Coordenar relacionamento com agências e fornecedores'
    ],
    'arquitetura e design': [
        'Elaborar projetos executivos e detalhamentos técnicos',
        'Realizar levantamentos arquitetônicos e medições',
        'Coordenar compatibilização de projetos complementares',
        'Acompanhar execução de obras e fiscalizar qualidade',
        'Desenvolver estudos de impacto ambiental e sustentabilidade'
    ],
    'Educacao': [
        'Planejar e executar atividades pedagógicas diversificadas',
        'Avaliar aprendizagem e desenvolver estratégias de recuperação',
        'Participar de formações continuadas e capacitações',
        'Elaborar materiais didáticos e recursos educacionais',
        'Promover integração família-escola-comunidade'
    ],
    'Administracao': [
        'Coordenar rotinas administrativas e controles internos',
        'Elaborar relatórios gerenciais e análises de desempenho',
        'Gerenciar recursos humanos e processos de recrutamento',
        'Implementar melhorias nos processos organizacionais',
        'Controlar orçamentos e indicadores financeiros'
    ]
}

# Habilidades específicas por setor
SETOR_HABILIDADES = {
    'ServicoSocial': [
        'Escuta ativa', 'Empatia', 'Mediação de conflitos', 'Conhecimento em políticas públicas',
        'Elaboração de relatórios sociais', 'Trabalho interdisciplinar', 'Ética profissional'
    ],
    'Telecomunicacoes': [
        'Conhecimento em redes', 'Protocolos de comunicação', 'Troubleshooting',
        'Configuração de equipamentos', 'Análise de performance', 'Segurança da informação'
    ],
    'Comunicacao e marketing': [
        'Marketing digital', 'Criatividade', 'Análise de dados', 'Gestão de mídias sociais',
        'Copywriting', 'Branding', 'Relacionamento interpessoal'
    ],
    'arquitetura e design': [
        'AutoCAD', 'SketchUp', 'Criatividade espacial', 'Conhecimento em materiais',
        'Sustentabilidade', 'Gestão de projetos', 'Visão estética'
    ],
    'Educacao': [
        'Didática', 'Metodologias ativas', 'Avaliação educacional', 'Tecnologias educacionais',
        'Gestão de sala de aula', 'Inclusão', 'Formação continuada'
    ],
    'Administracao': [
        'Gestão de processos', 'Liderança', 'Análise de dados', 'Planejamento estratégico',
        'Controle financeiro', 'Negociação', 'Tomada de decisão'
    ]
}

def generate_sector_specific_content(vaga):
    """Gera conteúdo específico baseado no setor da vaga"""
    setor = vaga['informacoes_basicas']['setor']
    titulo = vaga['informacoes_basicas']['titulo_vaga']
    
    # Seleciona descrições específicas do setor
    if setor in SETOR_DESCRIPTIONS:
        descricoes_setor = SETOR_DESCRIPTIONS[setor]
        responsabilidades_setor = SETOR_RESPONSABILIDADES[setor]
        habilidades_setor = SETOR_HABILIDADES[setor]
        
        # Seleciona aleatoriamente itens específicos do setor
        descricao_especifica = random.choice(descricoes_setor)
        responsabilidades_especificas = random.sample(responsabilidades_setor, min(3, len(responsabilidades_setor)))
        habilidades_especificas = random.sample(habilidades_setor, min(4, len(habilidades_setor)))
        
        # Atualiza a vaga com conteúdo específico
        vaga['responsabilidades'] = responsabilidades_especificas
        vaga['habilidades_requeridas'] = habilidades_especificas
        
        # Cria descrição completa específica do setor
        responsabilidades_texto = '; '.join(responsabilidades_especificas)
        habilidades_texto = ', '.join(habilidades_especificas)
        
        descricao_completa = f"Vaga: {titulo} | Setor: {setor} | Responsabilidades: {responsabilidades_texto} | Descrição: {descricao_especifica} Requisitos essenciais: {habilidades_texto}."
        
        vaga['descricao_completa']['texto_completo'] = descricao_completa
    
    return vaga

def main():
    # Carrega o arquivo atual
    with open('vagas_unicas_completas.jsonl', 'r', encoding='utf-8') as f:
        vagas = [json.loads(line) for line in f]
    
    print(f"Processando {len(vagas)} vagas...")
    
    # Estatísticas por setor
    setores_count = defaultdict(int)
    vagas_processadas = []
    
    for vaga in vagas:
        setor = vaga['informacoes_basicas']['setor']
        setores_count[setor] += 1
        
        # Gera conteúdo específico do setor
        vaga_processada = generate_sector_specific_content(vaga)
        vagas_processadas.append(vaga_processada)
    
    # Salva o arquivo com descrições específicas por setor
    with open('vagas_setores_especificos.jsonl', 'w', encoding='utf-8') as f:
        for vaga in vagas_processadas:
            f.write(json.dumps(vaga, ensure_ascii=False) + '\n')
    
    # Gera relatório
    relatorio = {
        'total_vagas_processadas': len(vagas_processadas),
        'setores_processados': dict(setores_count),
        'descricoes_por_setor': {setor: len(descricoes) for setor, descricoes in SETOR_DESCRIPTIONS.items()},
        'responsabilidades_por_setor': {setor: len(resp) for setor, resp in SETOR_RESPONSABILIDADES.items()},
        'habilidades_por_setor': {setor: len(hab) for setor, hab in SETOR_HABILIDADES.items()}
    }
    
    with open('relatorio_setores_especificos.json', 'w', encoding='utf-8') as f:
        json.dump(relatorio, f, ensure_ascii=False, indent=2)
    
    print("\n=== RELATÓRIO DE PROCESSAMENTO ===")
    print(f"Total de vagas processadas: {relatorio['total_vagas_processadas']}")
    print("\nVagas por setor:")
    for setor, count in relatorio['setores_processados'].items():
        print(f"  {setor}: {count} vagas")
    
    print("\nConteúdo específico criado por setor:")
    for setor in SETOR_DESCRIPTIONS.keys():
        desc_count = relatorio['descricoes_por_setor'].get(setor, 0)
        resp_count = relatorio['responsabilidades_por_setor'].get(setor, 0)
        hab_count = relatorio['habilidades_por_setor'].get(setor, 0)
        print(f"  {setor}: {desc_count} descrições, {resp_count} responsabilidades, {hab_count} habilidades")
    
    print(f"\nArquivos gerados:")
    print(f"  - vagas_setores_especificos.jsonl")
    print(f"  - relatorio_setores_especificos.json")

if __name__ == "__main__":
    main()