import json
import os
from dotenv import load_dotenv

def create_specific_description(job):
    """Cria uma descrição específica baseada no título e outras informações da vaga"""
    titulo = job.get('informacoes_basicas', {}).get('fonte', '')
    empresa = job.get('informacoes_basicas', {}).get('empresa_principal', '')
    cidade = job.get('localizacao', {}).get('cidade_extraida', '')
    estado = job.get('localizacao', {}).get('estado_extraido', '')
    unidade = job.get('localizacao', {}).get('unidade', '')
    jornada = job.get('jornada_trabalho', {}).get('jornada_extraida', '')
    experiencia = job.get('requisitos', {}).get('experiencia_necessaria', '')
    formacao = job.get('requisitos', {}).get('formacao_minima', '')
    
    # Mapeia títulos para descrições específicas
    descriptions_map = {
        'Ajudante Geral': f"Vaga para Ajudante Geral na área de Serviço Social. Responsável por auxiliar nas atividades gerais de apoio aos serviços sociais, incluindo organização de materiais, apoio administrativo e suporte às equipes técnicas. Local: {unidade or cidade}/{estado}. Jornada: {jornada}. Experiência: {experiencia}. Formação: {formacao}.",
        
        'Coordenador(a) de projeto social': f"Coordenador(a) de Projeto Social responsável por planejar, implementar e monitorar projetos sociais alinhados à missão da organização. Gerenciar equipes e parcerias com outras instituições e comunidades. Elaborar relatórios e acompanhar indicadores de impacto social. Local: {unidade or cidade}/{estado}. Jornada: {jornada}.",
        
        'Cuidador Social': f"Cuidador Social para atuar no acompanhamento e cuidado de pessoas em situação de vulnerabilidade social. Desenvolver atividades de apoio psicossocial, orientação familiar e promoção da autonomia dos assistidos. Local: {unidade or cidade}/{estado}. Experiência: {experiencia}.",
        
        'Monitor de inclusão': f"Monitor de Inclusão para atuar no programa Escola Aberta com foco na integração e inclusão de pessoas com deficiência nas oficinas oferecidas. Adaptar atividades pedagógicas e promover a participação ativa de todos os participantes. Local: {unidade or cidade}/{estado}.",
        
        'Mediador': f"Mediador Social responsável por facilitar o diálogo e apoiar a resolução de conflitos de forma construtiva. Contribuir para o desenvolvimento socioemocional dos usuários dos serviços. Promover a comunicação efetiva entre diferentes grupos. Local: {unidade or cidade}/{estado}.",
        
        'Assistente Social Media': f"Assistente de Social Media com perfil videomaker para área social. Profissional criativo, ágil e com visão estratégica para registrar, editar e publicar conteúdos em tempo real relacionados aos projetos sociais da organização. Local: {unidade or cidade}/{estado}.",
        
        'CLT IMEDIATO- AT - ACOMPANHANTE TERAPÊUTICO': f"Acompanhante Terapêutico para atendimento de crianças com autismo. Realizar atendimento terapêutico especializado, aplicar técnicas ABA (Applied Behavior Analysis). Pode ser profissional recém-formado da área da saúde. Local: {unidade or cidade}/{estado}.",
        
        'Coordenador de Projeto Social': f"Coordenador de Projeto Social responsável por coordenar equipe responsável pela execução do programa de acolhimento de crianças e adolescentes. Elaborar e acompanhar planejamento estratégico das ações. Realizar gestão de recursos e parcerias. Local: {unidade or cidade}/{estado}.",
        
        'Educador (a) Social': f"Educador(a) Social com responsabilidade de identificar necessidades e demandas dos assistidos, desenvolvendo atividades culturais, laborativas, recreativas e ressocializadoras. Promover a inclusão social e o desenvolvimento de habilidades. Local: {unidade or cidade}/{estado}."
    }
    
    # Para Assistente Social, cria descrições específicas baseadas no nível
    if 'Assistente Social' in titulo:
        if 'Sr' in titulo or 'UTI' in titulo:
            return f"Assistente Social Sênior para UTI. Profissional experiente para representar a instituição em reuniões e instâncias externas, acompanhar e orientar procedimentos internos junto às lideranças, desenvolver ações estratégicas na área hospitalar. Local: {unidade or cidade}/{estado}. Especialização em ambiente hospitalar."
        elif 'Pl' in titulo:
            return f"Assistente Social Pleno para UTI. Realizar atendimento e acompanhamento de famílias e indivíduos em situação de vulnerabilidade no ambiente hospitalar. Auxiliar no encaminhamento para serviços públicos e programas sociais. Local: {unidade or cidade}/{estado}."
        else:
            return f"Assistente Social para entrevistar por telefone e em visita, quando necessário, a família do paciente em avaliação, prestando esclarecimentos sobre a assistência domiciliar. Realizar avaliação socioeconômica e elaborar planos de intervenção. Local: {unidade or cidade}/{estado}. Experiência: {experiencia}."
    
    # Usa o mapeamento específico ou cria uma descrição genérica
    if titulo in descriptions_map:
        return descriptions_map[titulo]
    else:
        return f"Profissional de {titulo} na área de Serviço Social. Atuar em atividades específicas da função em {unidade or cidade}/{estado}. Jornada: {jornada}. Experiência necessária: {experiencia}. Formação: {formacao}."

def fix_servico_social_descriptions():
    """Corrige as descrições do setor ServicoSocial"""
    jobs = []
    servico_social_jobs = []
    
    # Carrega todos os dados
    with open('vagas_todos_setores_estruturadas_completo.jsonl', 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                job = json.loads(line)
                jobs.append(job)
                
                # Separa as vagas do setor ServicoSocial
                if job.get('informacoes_basicas', {}).get('setor', '') == 'ServicoSocial':
                    servico_social_jobs.append(job)
    
    print(f"Total de vagas carregadas: {len(jobs)}")
    print(f"Vagas do setor ServicoSocial encontradas: {len(servico_social_jobs)}")
    
    # Corrige as descrições das vagas do ServicoSocial
    fixed_count = 0
    for job in jobs:
        if job.get('informacoes_basicas', {}).get('setor', '') == 'ServicoSocial':
            # Cria nova descrição específica
            new_description = create_specific_description(job)
            
            # Atualiza a descrição completa
            if 'descricao_completa' not in job:
                job['descricao_completa'] = {}
            
            job['descricao_completa']['texto_completo'] = new_description
            job['descricao_completa']['segmentos_separados'] = [new_description]
            job['descricao_completa']['total_segmentos'] = 1
            
            fixed_count += 1
            print(f"Corrigida vaga ID {job.get('id')}: {job.get('informacoes_basicas', {}).get('fonte', '')}")
    
    # Salva o arquivo corrigido
    output_file = 'vagas_todos_setores_estruturadas_corrigidas.jsonl'
    with open(output_file, 'w', encoding='utf-8') as f:
        for job in jobs:
            f.write(json.dumps(job, ensure_ascii=False) + '\n')
    
    print(f"\n✅ Correção concluída!")
    print(f"Vagas corrigidas: {fixed_count}")
    print(f"Arquivo salvo como: {output_file}")
    
    # Verifica a diversidade após correção
    print(f"\n=== VERIFICAÇÃO PÓS-CORREÇÃO ===")
    servico_social_descriptions = []
    for job in jobs:
        if job.get('informacoes_basicas', {}).get('setor', '') == 'ServicoSocial':
            desc = job.get('descricao_completa', {}).get('texto_completo', '')
            servico_social_descriptions.append(desc)
    
    unique_descriptions = len(set(servico_social_descriptions))
    total_descriptions = len(servico_social_descriptions)
    diversity_rate = (unique_descriptions / total_descriptions) * 100 if total_descriptions > 0 else 0
    
    print(f"Setor ServicoSocial após correção:")
    print(f"  - Total de vagas: {total_descriptions}")
    print(f"  - Descrições únicas: {unique_descriptions}")
    print(f"  - Taxa de diversidade: {diversity_rate:.1f}%")
    
    # Mostra algumas descrições corrigidas
    print(f"\n=== EXEMPLOS DE DESCRIÇÕES CORRIGIDAS ===")
    for i, job in enumerate([j for j in jobs if j.get('informacoes_basicas', {}).get('setor', '') == 'ServicoSocial'][:5]):
        titulo = job.get('informacoes_basicas', {}).get('fonte', '')
        desc = job.get('descricao_completa', {}).get('texto_completo', '')
        print(f"\n{i+1}. {titulo}:")
        print(f"   {desc[:150]}...")

def main():
    load_dotenv()
    fix_servico_social_descriptions()

if __name__ == "__main__":
    main()