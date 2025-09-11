import json
import random
from collections import defaultdict

# Listas de empresas diversificadas por setor
EMPRESAS_POR_SETOR = {
    "ServicoSocial": [
        "Instituto de Assistência Social",
        "Fundação Bem-Estar Social",
        "Centro de Apoio Comunitário",
        "ONG Esperança",
        "Associação Vida Nova",
        "Instituto Cidadania Ativa",
        "Fundação Solidariedade",
        "Centro Social Integrado"
    ],
    "Comunicacao e marketing": [
        "Agência Criativa Digital",
        "Marketing Solutions",
        "Comunicação Estratégica",
        "Brand Studio",
        "Digital Marketing Pro",
        "Agência Inovação",
        "Creative Media",
        "Estratégia & Comunicação"
    ],
    "Telecomunicacoes": [
        "TechConnect",
        "Telecom Solutions",
        "Rede Digital",
        "Conecta Tecnologia",
        "Sistemas Integrados",
        "TeleTech Brasil",
        "Comunicações Avançadas",
        "Network Pro"
    ],
    "arquitetura e design": [
        "Arquitetura Moderna",
        "Design & Construção",
        "Estúdio Arquitetônico",
        "Projetos Inovadores",
        "Arquitetura Sustentável",
        "Design Studio",
        "Construção Inteligente",
        "Espaços Criativos"
    ],
    "Educacao": [
        "Instituto Educacional",
        "Centro de Ensino",
        "Escola Inovadora",
        "Educação Transformadora",
        "Academia do Saber",
        "Instituto de Aprendizagem",
        "Centro Pedagógico",
        "Educação Integral"
    ],
    "Administracao": [
        "Gestão Empresarial",
        "Administração Eficiente",
        "Consultoria Organizacional",
        "Soluções Administrativas",
        "Gestão Estratégica",
        "Administração Moderna",
        "Consultoria Empresarial",
        "Gestão & Resultados"
    ]
}

# Cidades e estados diversificados
CIDADES_ESTADOS = [
    {"cidade": "São Paulo", "estado": "SP"},
    {"cidade": "Rio de Janeiro", "estado": "RJ"},
    {"cidade": "Belo Horizonte", "estado": "MG"},
    {"cidade": "Brasília", "estado": "DF"},
    {"cidade": "Salvador", "estado": "BA"},
    {"cidade": "Fortaleza", "estado": "CE"},
    {"cidade": "Recife", "estado": "PE"},
    {"cidade": "Porto Alegre", "estado": "RS"},
    {"cidade": "Curitiba", "estado": "PR"},
    {"cidade": "Goiânia", "estado": "GO"},
    {"cidade": "Manaus", "estado": "AM"},
    {"cidade": "Belém", "estado": "PA"},
    {"cidade": "Vitória", "estado": "ES"},
    {"cidade": "Florianópolis", "estado": "SC"},
    {"cidade": "Campo Grande", "estado": "MS"},
    {"cidade": "João Pessoa", "estado": "PB"},
    {"cidade": "Aracaju", "estado": "SE"},
    {"cidade": "Teresina", "estado": "PI"},
    {"cidade": "Cuiabá", "estado": "MT"},
    {"cidade": "Maceió", "estado": "AL"}
]

def diversificar_empresas_localizacoes(arquivo_entrada, arquivo_saida):
    """
    Diversifica empresas e localizações das vagas
    """
    vagas_processadas = []
    empresas_usadas_por_setor = defaultdict(set)
    localizacoes_usadas = set()
    
    with open(arquivo_entrada, 'r', encoding='utf-8') as f:
        for linha in f:
            vaga = json.loads(linha.strip())
            
            # Diversificar empresa
            setor = vaga['informacoes_basicas']['setor']
            if setor in EMPRESAS_POR_SETOR:
                empresas_disponiveis = [
                    emp for emp in EMPRESAS_POR_SETOR[setor] 
                    if emp not in empresas_usadas_por_setor[setor]
                ]
                
                if not empresas_disponiveis:
                    # Reset se todas foram usadas
                    empresas_usadas_por_setor[setor].clear()
                    empresas_disponiveis = EMPRESAS_POR_SETOR[setor]
                
                nova_empresa = random.choice(empresas_disponiveis)
                empresas_usadas_por_setor[setor].add(nova_empresa)
                vaga['informacoes_basicas']['empresa_principal'] = nova_empresa
            
            # Diversificar localização
            localizacoes_disponiveis = [
                loc for loc in CIDADES_ESTADOS 
                if f"{loc['cidade']}-{loc['estado']}" not in localizacoes_usadas
            ]
            
            if not localizacoes_disponiveis:
                # Reset se todas foram usadas
                localizacoes_usadas.clear()
                localizacoes_disponiveis = CIDADES_ESTADOS
            
            nova_localizacao = random.choice(localizacoes_disponiveis)
            localizacoes_usadas.add(f"{nova_localizacao['cidade']}-{nova_localizacao['estado']}")
            
            vaga['localizacao']['cidade'] = nova_localizacao['cidade']
            vaga['localizacao']['estado'] = nova_localizacao['estado']
            vaga['localizacao']['localidade_completa'] = f"{nova_localizacao['cidade']}, {nova_localizacao['estado']}"
            
            vagas_processadas.append(vaga)
    
    # Salvar arquivo diversificado
    with open(arquivo_saida, 'w', encoding='utf-8') as f:
        for vaga in vagas_processadas:
            f.write(json.dumps(vaga, ensure_ascii=False) + '\n')
    
    # Gerar relatório
    relatorio = {
        "total_vagas_processadas": len(vagas_processadas),
        "empresas_por_setor": {
            setor: len(empresas) for setor, empresas in empresas_usadas_por_setor.items()
        },
        "total_localizacoes_usadas": len(localizacoes_usadas),
        "diversificacao_completa": True
    }
    
    with open('relatorio_diversificacao.json', 'w', encoding='utf-8') as f:
        json.dump(relatorio, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Diversificação concluída!")
    print(f"📊 {len(vagas_processadas)} vagas processadas")
    print(f"🏢 Empresas diversificadas por setor")
    print(f"📍 {len(localizacoes_usadas)} localizações diferentes utilizadas")
    print(f"💾 Arquivo salvo: {arquivo_saida}")
    print(f"📋 Relatório salvo: relatorio_diversificacao.json")

if __name__ == "__main__":
    diversificar_empresas_localizacoes(
        'vagas_setores_especificos.jsonl',
        'vagas_diversificadas_final.jsonl'
    )