# 🚀 Exemplos Práticos da API de Vagas e Skills

Este documento contém exemplos práticos de como usar a API `api_vagas_skills.py` com todos os parâmetros disponíveis da tabela `vagas` (25 colunas) e funcionalidades do Supabase.

## 📋 Índice

1. [Dashboard Frontend Completo (JavaScript)](#dashboard-frontend-completo)
2. [Análise de Mercado Avançada (Python)](#análise-de-mercado-avançada)
3. [Sistema de Recomendação com Filtros](#sistema-de-recomendação-com-filtros)
4. [Monitoramento e Analytics](#monitoramento-e-analytics)
5. [Integração com Todas as Colunas](#integração-com-todas-as-colunas)
6. [Performance e Otimização](#performance-e-otimização)

## Casos de Uso Comuns

### 1. Dashboard Frontend Completo (JavaScript)

#### Cliente API com Todos os Parâmetros

```javascript
class VagasAPIComplete {
    constructor(baseURL = 'http://localhost:8000') {
        this.baseURL = baseURL;
    }

    // Busca avançada com todos os filtros disponíveis
    async buscarVagasAvancado(filtros = {}) {
        const params = new URLSearchParams();
        
        // Filtros básicos
        if (filtros.setor) params.append('setor', filtros.setor);
        if (filtros.modalidade) params.append('modalidade', filtros.modalidade);
        if (filtros.estado) params.append('estado', filtros.estado);
        if (filtros.cidade) params.append('cidade', filtros.cidade);
        if (filtros.regiao) params.append('regiao', filtros.regiao);
        
        // Filtros de emprego
        if (filtros.nivel_experiencia) params.append('nivel_experiencia', filtros.nivel_experiencia);
        if (filtros.tipo_contrato) params.append('tipo_contrato', filtros.tipo_contrato);
        if (filtros.empresa) params.append('empresa', filtros.empresa);
        if (filtros.salario_min) params.append('salario_min', filtros.salario_min);
        if (filtros.salario_max) params.append('salario_max', filtros.salario_max);
        
        // Filtros de conteúdo
        if (filtros.skills) params.append('skills', filtros.skills.join(','));
        if (filtros.beneficios) params.append('beneficios', filtros.beneficios);
        if (filtros.responsabilidades) params.append('responsabilidades', filtros.responsabilidades);
        if (filtros.search) params.append('search', filtros.search);
        
        // Filtros de data
        if (filtros.data_inicio) params.append('data_inicio', filtros.data_inicio);
        if (filtros.data_fim) params.append('data_fim', filtros.data_fim);
        if (filtros.versao_dados) params.append('versao_dados', filtros.versao_dados);
        
        // Paginação e ordenação
        if (filtros.page) params.append('page', filtros.page);
        if (filtros.limit) params.append('limit', filtros.limit);
        if (filtros.order_by) params.append('order_by', filtros.order_by);
        if (filtros.order_direction) params.append('order_direction', filtros.order_direction);
        
        const response = await fetch(`${this.baseURL}/jobs-filtered?${params}`);
        return await response.json();
    }

    // Busca com todas as 25 colunas
    async obterVagasCompletas(filtros = {}) {
        const params = new URLSearchParams();
        
        Object.keys(filtros).forEach(key => {
            if (filtros[key] !== undefined && filtros[key] !== null) {
                params.append(key, filtros[key]);
            }
        });
        
        const response = await fetch(`${this.baseURL}/jobs?${params}`);
        return await response.json();
    }

    // Estatísticas avançadas
    async obterEstatisticasCompletas() {
        const response = await fetch(`${this.baseURL}/stats`);
        return await response.json();
    }

    // Skills por setor
    async obterSkillsPorSetor(setor) {
        const response = await fetch(`${this.baseURL}/skills-by-sector?sector=${setor}`);
        return await response.json();
    }

    // Busca textual livre
    async buscarTextoLivre(query, filtros = {}) {
        const params = new URLSearchParams({ search: query });
        
        Object.keys(filtros).forEach(key => {
            if (filtros[key]) params.append(key, filtros[key]);
        });
        
        const response = await fetch(`${this.baseURL}/search?${params}`);
        return await response.json();
    }
}

// Exemplo de uso completo
const api = new VagasAPIComplete();

// Dashboard com filtros avançados
async function criarDashboardCompleto() {
    try {
        // Busca vagas com múltiplos filtros
        const vagasFiltradas = await api.buscarVagasAvancado({
            setor: 'Tecnologia',
            modalidade: 'Remoto',
            estado: 'SP',
            nivel_experiencia: 'Pleno',
            skills: ['Python', 'Django', 'PostgreSQL'],
            salario_min: 5000,
            salario_max: 15000,
            beneficios: 'plano de saúde',
            data_inicio: '2024-01-01',
            order_by: 'created_at',
            order_direction: 'desc',
            limit: 50
        });

        // Estatísticas do mercado
        const stats = await api.obterEstatisticasCompletas();
        
        // Skills mais demandadas em Tecnologia
        const skillsTech = await api.obterSkillsPorSetor('Tecnologia');
        
        // Busca textual
        const vagasPython = await api.buscarTextoLivre('python developer', {
            setor: 'Tecnologia',
            modalidade: 'Remoto'
        });

        // Renderizar dashboard
        renderizarDashboard({
            vagas: vagasFiltradas,
            estatisticas: stats,
            skillsSetor: skillsTech,
            buscaTextual: vagasPython
        });
        
    } catch (error) {
        console.error('Erro ao carregar dashboard:', error);
    }
}

// Função para renderizar dados completos
function renderizarVagaCompleta(vaga) {
    return `
        <div class="vaga-card">
            <h3>${vaga.titulo_vaga}</h3>
            <div class="empresa">${vaga.empresa_principal}</div>
            <div class="localizacao">
                ${vaga.cidade_extraida}, ${vaga.estado} (${vaga.regiao})
                <span class="modalidade">${vaga.modalidade}</span>
            </div>
            <div class="detalhes">
                <span class="setor">${vaga.setor}</span>
                <span class="experiencia">${vaga.nivel_experiencia}</span>
                <span class="contrato">${vaga.tipo_contrato}</span>
            </div>
            ${vaga.salario_informado ? `<div class="salario">${vaga.salario_informado}</div>` : ''}
            
            <div class="skills">
                ${vaga.habilidades_requeridas?.map(skill => 
                    `<span class="skill-tag">${skill}</span>`
                ).join('') || ''}
            </div>
            
            <div class="beneficios">
                ${vaga.beneficios?.map(beneficio => 
                    `<span class="beneficio">${beneficio}</span>`
                ).join('') || ''}
            </div>
            
            <div class="responsabilidades">
                <h4>Responsabilidades:</h4>
                <ul>
                    ${vaga.responsabilidades?.map(resp => 
                        `<li>${resp}</li>`
                    ).join('') || ''}
                </ul>
            </div>
            
            <div class="metadata">
                <small>Publicado em: ${new Date(vaga.created_at).toLocaleDateString()}</small>
                <small>Versão: ${vaga.versao_dados}</small>
            </div>
        </div>
    `;
}
```

### 2. Análise de Mercado Avançada (Python)

```python
import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import numpy as np

class VagasAnalyzerComplete:
    def __init__(self, base_url='http://localhost:8000'):
        self.base_url = base_url
    
    def buscar_vagas_completas(self, filtros=None, limit=1000):
        """Buscar vagas com todos os campos disponíveis"""
        params = {'limit': limit}
        if filtros:
            params.update(filtros)
        
        response = requests.get(f'{self.base_url}/jobs', params=params)
        return response.json()
    
    def buscar_vagas_filtradas(self, **kwargs):
        """Busca avançada com todos os parâmetros"""
        response = requests.get(f'{self.base_url}/jobs-filtered', params=kwargs)
        return response.json()
    
    def obter_estatisticas_completas(self):
        """Estatísticas detalhadas"""
        response = requests.get(f'{self.base_url}/stats')
        return response.json()
    
    def obter_skills_por_setor(self, setor):
        """Skills específicas por setor"""
        response = requests.get(f'{self.base_url}/skills-by-sector', 
                              params={'sector': setor})
        return response.json()
    
    def analise_mercado_completa(self):
        """Análise completa usando todas as 25 colunas"""
        print("🔍 Iniciando análise completa do mercado...")
        
        # Buscar dados completos
        vagas = self.buscar_vagas_completas(limit=5000)
        stats = self.obter_estatisticas_completas()
        
        # Converter para DataFrame com todas as colunas
        df = pd.DataFrame(vagas)
        
        print(f"📊 Dataset carregado: {len(df)} vagas com {len(df.columns)} colunas")
        print(f"Colunas disponíveis: {list(df.columns)}")
        
        # Análises por categoria
        self.analise_geografica(df)
        self.analise_temporal(df)
        self.analise_salarial(df)
        self.analise_skills_beneficios(df)
        self.analise_empresas_setores(df)
        
        return df
    
    def analise_geografica(self, df):
        """Análise geográfica detalhada"""
        print("\n🗺️  ANÁLISE GEOGRÁFICA")
        print("=" * 50)
        
        # Distribuição por região
        if 'regiao' in df.columns:
            print("Distribuição por Região:")
            print(df['regiao'].value_counts())
        
        # Top estados
        print("\nTop 10 Estados:")
        print(df['estado'].value_counts().head(10))
        
        # Cidades com mais vagas
        print("\nTop 10 Cidades:")
        print(df['cidade_extraida'].value_counts().head(10))
        
        # Modalidade por região
        if 'regiao' in df.columns and 'modalidade' in df.columns:
            modalidade_regiao = pd.crosstab(df['regiao'], df['modalidade'])
            print("\nModalidade por Região:")
            print(modalidade_regiao)
    
    def analise_temporal(self, df):
        """Análise temporal das vagas"""
        print("\n📅 ANÁLISE TEMPORAL")
        print("=" * 50)
        
        # Converter datas
        df['created_at'] = pd.to_datetime(df['created_at'])
        df['data_upload'] = pd.to_datetime(df['data_upload'])
        
        # Vagas por mês
        df['mes_criacao'] = df['created_at'].dt.to_period('M')
        vagas_por_mes = df['mes_criacao'].value_counts().sort_index()
        print("Vagas criadas por mês:")
        print(vagas_por_mes.tail(6))
        
        # Versões de dados
        if 'versao_dados' in df.columns:
            print("\nDistribuição por versão dos dados:")
            print(df['versao_dados'].value_counts())
    
    def analise_salarial(self, df):
        """Análise salarial detalhada"""
        print("\n💰 ANÁLISE SALARIAL")
        print("=" * 50)
        
        # Vagas com salário informado
        vagas_com_salario = df[df['salario_informado'].notna()]
        print(f"Vagas com salário informado: {len(vagas_com_salario)} ({len(vagas_com_salario)/len(df)*100:.1f}%)")
        
        if len(vagas_com_salario) > 0:
            # Análise por setor
            salario_por_setor = vagas_com_salario.groupby('setor')['salario_informado'].agg(['count', 'mean', 'median'])
            print("\nSalários por setor:")
            print(salario_por_setor.sort_values('mean', ascending=False))
            
            # Análise por modalidade
            salario_por_modalidade = vagas_com_salario.groupby('modalidade')['salario_informado'].agg(['count', 'mean', 'median'])
            print("\nSalários por modalidade:")
            print(salario_por_modalidade)
    
    def analise_skills_beneficios(self, df):
        """Análise de skills e benefícios"""
        print("\n🛠️  ANÁLISE DE SKILLS E BENEFÍCIOS")
        print("=" * 50)
        
        # Skills mais demandadas
        if 'habilidades_requeridas' in df.columns:
            all_skills = []
            for skills in df['habilidades_requeridas'].dropna():
                if isinstance(skills, list):
                    all_skills.extend(skills)
                elif isinstance(skills, str):
                    all_skills.extend(skills.split(','))
            
            skills_count = pd.Series(all_skills).value_counts()
            print("Top 15 Skills mais demandadas:")
            print(skills_count.head(15))
        
        # Benefícios mais oferecidos
        if 'beneficios' in df.columns:
            all_benefits = []
            for benefits in df['beneficios'].dropna():
                if isinstance(benefits, list):
                    all_benefits.extend(benefits)
                elif isinstance(benefits, str):
                    all_benefits.extend(benefits.split(','))
            
            benefits_count = pd.Series(all_benefits).value_counts()
            print("\nTop 10 Benefícios mais oferecidos:")
            print(benefits_count.head(10))
    
    def analise_empresas_setores(self, df):
        """Análise de empresas e setores"""
        print("\n🏢 ANÁLISE DE EMPRESAS E SETORES")
        print("=" * 50)
        
        # Empresas que mais contratam
        print("Top 10 Empresas que mais contratam:")
        print(df['empresa_principal'].value_counts().head(10))
        
        # Distribuição por setor
        print("\nDistribuição por setor:")
        print(df['setor'].value_counts())
        
        # Nível de experiência por setor
        if 'nivel_experiencia' in df.columns:
            exp_setor = pd.crosstab(df['setor'], df['nivel_experiencia'])
            print("\nNível de experiência por setor:")
            print(exp_setor)
    
    def criar_visualizacoes_completas(self, df):
        """Visualizações usando todas as colunas"""
        fig, axes = plt.subplots(3, 2, figsize=(20, 18))
        
        # 1. Vagas por região e modalidade
        if 'regiao' in df.columns:
            modalidade_regiao = pd.crosstab(df['regiao'], df['modalidade'])
            modalidade_regiao.plot(kind='bar', ax=axes[0,0], stacked=True)
            axes[0,0].set_title('Modalidade por Região')
            axes[0,0].legend(title='Modalidade')
        
        # 2. Top 15 Skills
        if 'habilidades_requeridas' in df.columns:
            all_skills = []
            for skills in df['habilidades_requeridas'].dropna():
                if isinstance(skills, list):
                    all_skills.extend(skills)
            
            skills_count = pd.Series(all_skills).value_counts().head(15)
            skills_count.plot(kind='barh', ax=axes[0,1])
            axes[0,1].set_title('Top 15 Skills Mais Demandadas')
        
        # 3. Distribuição salarial por setor
        vagas_com_salario = df[df['salario_informado'].notna()]
        if len(vagas_com_salario) > 0:
            sns.boxplot(data=vagas_com_salario, x='setor', y='salario_informado', ax=axes[1,0])
            axes[1,0].set_title('Distribuição Salarial por Setor')
            axes[1,0].tick_params(axis='x', rotation=45)
        
        # 4. Vagas por mês
        df['mes_criacao'] = pd.to_datetime(df['created_at']).dt.to_period('M')
        vagas_por_mes = df['mes_criacao'].value_counts().sort_index()
        vagas_por_mes.plot(kind='line', ax=axes[1,1], marker='o')
        axes[1,1].set_title('Evolução de Vagas por Mês')
        
        # 5. Nível de experiência
        df['nivel_experiencia'].value_counts().plot(kind='pie', ax=axes[2,0], autopct='%1.1f%%')
        axes[2,0].set_title('Distribuição por Nível de Experiência')
        
        # 6. Top empresas
        top_empresas = df['empresa_principal'].value_counts().head(10)
        top_empresas.plot(kind='barh', ax=axes[2,1])
        axes[2,1].set_title('Top 10 Empresas que Mais Contratam')
        
        plt.tight_layout()
        plt.savefig('analise_completa_mercado.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def relatorio_setor_especifico(self, setor):
        """Relatório detalhado de um setor específico"""
        print(f"\n📋 RELATÓRIO DETALHADO - SETOR {setor.upper()}")
        print("=" * 60)
        
        # Buscar vagas do setor
        vagas_setor = self.buscar_vagas_filtradas(setor=setor, limit=1000)
        df_setor = pd.DataFrame(vagas_setor)
        
        if len(df_setor) == 0:
            print("Nenhuma vaga encontrada para este setor.")
            return
        
        print(f"Total de vagas no setor: {len(df_setor)}")
        
        # Análises específicas
        print(f"\nModalidades no setor {setor}:")
        print(df_setor['modalidade'].value_counts())
        
        print(f"\nNíveis de experiência no setor {setor}:")
        print(df_setor['nivel_experiencia'].value_counts())
        
        print(f"\nTop 10 cidades no setor {setor}:")
        print(df_setor['cidade_extraida'].value_counts().head(10))
        
        # Skills específicas do setor
        skills_setor = self.obter_skills_por_setor(setor)
        if skills_setor:
            print(f"\nTop skills no setor {setor}:")
            for skill in skills_setor[:10]:
                print(f"- {skill['skill']}: {skill['count']} vagas")
        
        return df_setor

# Exemplo de uso completo
if __name__ == "__main__":
    analyzer = VagasAnalyzerComplete()
    
    # Análise completa
    df_completo = analyzer.analise_mercado_completa()
    
    # Visualizações
    analyzer.criar_visualizacoes_completas(df_completo)
    
    # Relatórios específicos
    df_tech = analyzer.relatorio_setor_especifico('Tecnologia')
    df_saude = analyzer.relatorio_setor_especifico('Saúde')
    
## 6. Integração Completa com Todas as 25 Colunas

### Exemplo Completo de Uso da Tabela Vagas

```python
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
from typing import Dict, List, Optional

class VagasCompleteIntegration:
    """
    Classe para integração completa com a API de Vagas
    Utiliza todas as 25 colunas da tabela vagas
    """
    
    def __init__(self, api_url="http://localhost:8000"):
        self.api_url = api_url
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'VagasIntegration/1.0'
        })
        
        # Mapeamento das 25 colunas da tabela vagas
        self.colunas_vagas = [
            'id', 'setor', 'empresa_principal', 'titulo_vaga', 'modalidade',
            'nivel_experiencia', 'tipo_contrato', 'salario_informado', 'beneficios',
            'estado', 'cidade_extraida', 'regiao', 'localizacao_completa',
            'texto_completo', 'responsabilidades', 'habilidades_requeridas',
            'data_upload', 'versao_dados', 'created_at', 'updated_at'
        ]
    
    def obter_amostra_completa(self, limite: int = 100) -> List[Dict]:
        """Obter amostra com todas as 25 colunas"""
        try:
            # Selecionar todas as colunas explicitamente
            colunas_select = ','.join(self.colunas_vagas)
            response = self.session.get(
                f"{self.api_url}/jobs",
                params={
                    'select': colunas_select,
                    'limit': limite,
                    'order': 'created_at.desc'
                }
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Erro ao obter amostra: {e}")
            return []
    
    def filtros_avancados_completos(self, **filtros) -> List[Dict]:
        """
        Demonstrar filtros avançados com todas as opções disponíveis
        
        Parâmetros disponíveis:
        - setor, modalidade, estado, cidade_extraida, regiao
        - nivel_experiencia, tipo_contrato, empresa_principal
        - salario_min, salario_max
        - habilidades_requeridas, beneficios, responsabilidades
        - data_upload_gte, data_upload_lte, versao_dados
        - search (busca textual)
        """
        try:
            # Construir parâmetros de consulta
            params = {}
            
            # Filtros básicos
            for campo in ['setor', 'modalidade', 'estado', 'cidade_extraida', 'regiao']:
                if campo in filtros:
                    params[campo] = f"eq.{filtros[campo]}"
            
            # Filtros de emprego
            for campo in ['nivel_experiencia', 'tipo_contrato', 'empresa_principal']:
                if campo in filtros:
                    params[campo] = f"eq.{filtros[campo]}"
            
            # Filtros de salário
            if 'salario_min' in filtros:
                params['salario_informado'] = f"gte.{filtros['salario_min']}"
            if 'salario_max' in filtros:
                if 'salario_informado' in params:
                    # Combinar filtros de salário
                    params['and'] = f"(salario_informado.gte.{filtros['salario_min']},salario_informado.lte.{filtros['salario_max']})"
                    del params['salario_informado']
                else:
                    params['salario_informado'] = f"lte.{filtros['salario_max']}"
            
            # Filtros de conteúdo (busca textual)
            if 'habilidades_requeridas' in filtros:
                params['habilidades_requeridas'] = f"ilike.*{filtros['habilidades_requeridas']}*"
            if 'beneficios' in filtros:
                params['beneficios'] = f"ilike.*{filtros['beneficios']}*"
            if 'responsabilidades' in filtros:
                params['responsabilidades'] = f"ilike.*{filtros['responsabilidades']}*"
            
            # Filtros de data
            if 'data_upload_gte' in filtros:
                params['data_upload'] = f"gte.{filtros['data_upload_gte']}"
            if 'data_upload_lte' in filtros:
                if 'data_upload' in params:
                    params['and'] = f"(data_upload.gte.{filtros['data_upload_gte']},data_upload.lte.{filtros['data_upload_lte']})"
                    del params['data_upload']
                else:
                    params['data_upload'] = f"lte.{filtros['data_upload_lte']}"
            
            if 'versao_dados' in filtros:
                params['versao_dados'] = f"eq.{filtros['versao_dados']}"
            
            # Busca textual global
            if 'search' in filtros:
                search_term = filtros['search']
                params['or'] = f"(titulo_vaga.ilike.*{search_term}*,texto_completo.ilike.*{search_term}*,habilidades_requeridas.ilike.*{search_term}*)"
            
            # Paginação e ordenação
            params['limit'] = filtros.get('limit', 100)
            params['offset'] = filtros.get('offset', 0)
            params['order'] = filtros.get('order', 'created_at.desc')
            
            response = self.session.get(f"{self.api_url}/jobs", params=params)
            response.raise_for_status()
            return response.json()
            
        except requests.RequestException as e:
            print(f"Erro na busca avançada: {e}")
            return []
    
    def analise_completa_dataset(self) -> Dict:
        """Análise completa do dataset utilizando todas as colunas"""
        print("🔍 Iniciando análise completa do dataset...")
        
        # Obter amostra grande para análise
        vagas = self.obter_amostra_completa(limite=5000)
        
        if not vagas:
            return {"erro": "Nenhum dado disponível"}
        
        df = pd.DataFrame(vagas)
        
        analise = {
            "resumo_geral": {
                "total_vagas": len(df),
                "colunas_disponiveis": list(df.columns),
                "periodo_dados": {
                    "data_mais_antiga": df['data_upload'].min() if 'data_upload' in df.columns else None,
                    "data_mais_recente": df['data_upload'].max() if 'data_upload' in df.columns else None
                }
            },
            "distribuicoes": {},
            "analise_salarial": {},
            "analise_geografica": {},
            "analise_temporal": {},
            "analise_skills": {},
            "qualidade_dados": {}
        }
        
        # Análise de distribuições
        for coluna in ['setor', 'modalidade', 'nivel_experiencia', 'tipo_contrato', 'regiao']:
            if coluna in df.columns:
                analise["distribuicoes"][coluna] = df[coluna].value_counts().to_dict()
        
        # Análise salarial
        if 'salario_informado' in df.columns:
            salarios_validos = pd.to_numeric(df['salario_informado'], errors='coerce').dropna()
            if len(salarios_validos) > 0:
                analise["analise_salarial"] = {
                    "total_com_salario": len(salarios_validos),
                    "percentual_com_salario": (len(salarios_validos) / len(df)) * 100,
                    "estatisticas": {
                        "media": float(salarios_validos.mean()),
                        "mediana": float(salarios_validos.median()),
                        "desvio_padrao": float(salarios_validos.std()),
                        "minimo": float(salarios_validos.min()),
                        "maximo": float(salarios_validos.max()),
                        "q25": float(salarios_validos.quantile(0.25)),
                        "q75": float(salarios_validos.quantile(0.75))
                    },
                    "distribuicao_faixas": {
                        "ate_3k": len(salarios_validos[salarios_validos <= 3000]),
                        "3k_a_6k": len(salarios_validos[(salarios_validos > 3000) & (salarios_validos <= 6000)]),
                        "6k_a_10k": len(salarios_validos[(salarios_validos > 6000) & (salarios_validos <= 10000)]),
                        "10k_a_15k": len(salarios_validos[(salarios_validos > 10000) & (salarios_validos <= 15000)]),
                        "acima_15k": len(salarios_validos[salarios_validos > 15000])
                    }
                }
        
        # Análise geográfica
        if all(col in df.columns for col in ['estado', 'cidade_extraida', 'regiao']):
            analise["analise_geografica"] = {
                "estados_top": df['estado'].value_counts().head(10).to_dict(),
                "cidades_top": df['cidade_extraida'].value_counts().head(15).to_dict(),
                "regioes": df['regiao'].value_counts().to_dict(),
                "distribuicao_modalidade_por_regiao": df.groupby('regiao')['modalidade'].value_counts().to_dict()
            }
        
        # Análise temporal
        if 'data_upload' in df.columns:
            df['data_upload_parsed'] = pd.to_datetime(df['data_upload'], errors='coerce')
            df_temporal = df.dropna(subset=['data_upload_parsed'])
            
            if len(df_temporal) > 0:
                df_temporal['mes_ano'] = df_temporal['data_upload_parsed'].dt.to_period('M')
                df_temporal['dia_semana'] = df_temporal['data_upload_parsed'].dt.day_name()
                
                analise["analise_temporal"] = {
                    "vagas_por_mes": df_temporal['mes_ano'].value_counts().sort_index().to_dict(),
                    "vagas_por_dia_semana": df_temporal['dia_semana'].value_counts().to_dict(),
                    "tendencia_ultimos_30_dias": len(df_temporal[
                        df_temporal['data_upload_parsed'] >= (datetime.now() - timedelta(days=30))
                    ])
                }
        
        # Análise de skills
        if 'habilidades_requeridas' in df.columns:
            skills_counter = {}
            for habilidades in df['habilidades_requeridas'].dropna():
                if isinstance(habilidades, str):
                    skills_list = [skill.strip() for skill in habilidades.split(',')]
                    for skill in skills_list:
                        if skill:
                            skills_counter[skill] = skills_counter.get(skill, 0) + 1
            
            analise["analise_skills"] = {
                "total_skills_unicas": len(skills_counter),
                "top_skills": dict(sorted(skills_counter.items(), key=lambda x: x[1], reverse=True)[:30]),
                "skills_por_setor": {}
            }
            
            # Skills por setor
            for setor in df['setor'].unique():
                if pd.notna(setor):
                    vagas_setor = df[df['setor'] == setor]
                    skills_setor = {}
                    for habilidades in vagas_setor['habilidades_requeridas'].dropna():
                        if isinstance(habilidades, str):
                            skills_list = [skill.strip() for skill in habilidades.split(',')]
                            for skill in skills_list:
                                if skill:
                                    skills_setor[skill] = skills_setor.get(skill, 0) + 1
                    
                    analise["analise_skills"]["skills_por_setor"][setor] = dict(
                        sorted(skills_setor.items(), key=lambda x: x[1], reverse=True)[:10]
                    )
        
        # Análise de qualidade dos dados
        analise["qualidade_dados"] = {
            "completude_por_coluna": {},
            "valores_nulos": {},
            "valores_unicos": {}
        }
        
        for coluna in df.columns:
            total_registros = len(df)
            valores_nao_nulos = df[coluna].notna().sum()
            valores_nulos = total_registros - valores_nao_nulos
            
            analise["qualidade_dados"]["completude_por_coluna"][coluna] = (valores_nao_nulos / total_registros) * 100
            analise["qualidade_dados"]["valores_nulos"][coluna] = int(valores_nulos)
            analise["qualidade_dados"]["valores_unicos"][coluna] = int(df[coluna].nunique())
        
        return analise
    
    def busca_inteligente(self, query: str, contexto: Optional[Dict] = None) -> Dict:
        """
        Busca inteligente que interpreta linguagem natural
        e mapeia para filtros da API
        """
        query_lower = query.lower()
        filtros_inferidos = {}
        
        # Mapeamento de palavras-chave para filtros
        mapeamentos = {
            # Modalidades
            'remoto': {'modalidade': 'Remoto'},
            'presencial': {'modalidade': 'Presencial'},
            'híbrido': {'modalidade': 'Híbrido'},
            'hibrido': {'modalidade': 'Híbrido'},
            
            # Níveis de experiência
            'junior': {'nivel_experiencia': 'Júnior'},
            'júnior': {'nivel_experiencia': 'Júnior'},
            'pleno': {'nivel_experiencia': 'Pleno'},
            'senior': {'nivel_experiencia': 'Sênior'},
            'sênior': {'nivel_experiencia': 'Sênior'},
            'especialista': {'nivel_experiencia': 'Especialista'},
            
            # Setores
            'tecnologia': {'setor': 'Tecnologia'},
            'tech': {'setor': 'Tecnologia'},
            'ti': {'setor': 'Tecnologia'},
            'saúde': {'setor': 'Saúde'},
            'saude': {'setor': 'Saúde'},
            'educação': {'setor': 'Educação'},
            'educacao': {'setor': 'Educação'},
            'financeiro': {'setor': 'Financeiro'},
            'finanças': {'setor': 'Financeiro'},
            'financas': {'setor': 'Financeiro'},
            
            # Estados (exemplos)
            'são paulo': {'estado': 'SP'},
            'sp': {'estado': 'SP'},
            'rio de janeiro': {'estado': 'RJ'},
            'rj': {'estado': 'RJ'},
            'minas gerais': {'estado': 'MG'},
            'mg': {'estado': 'MG'},
            
            # Skills comuns
            'python': {'habilidades_requeridas': 'Python'},
            'javascript': {'habilidades_requeridas': 'JavaScript'},
            'react': {'habilidades_requeridas': 'React'},
            'java': {'habilidades_requeridas': 'Java'},
            'sql': {'habilidades_requeridas': 'SQL'},
            'aws': {'habilidades_requeridas': 'AWS'},
            'docker': {'habilidades_requeridas': 'Docker'}
        }
        
        # Aplicar mapeamentos
        for palavra, filtro in mapeamentos.items():
            if palavra in query_lower:
                filtros_inferidos.update(filtro)
        
        # Detectar faixas salariais
        import re
        salario_match = re.search(r'(\d+)k?\s*(?:a|até|-)?\s*(\d+)?k?', query_lower)
        if salario_match:
            salario_min = int(salario_match.group(1))
            if 'k' in salario_match.group(0) or salario_min < 100:
                salario_min *= 1000
            filtros_inferidos['salario_min'] = salario_min
            
            if salario_match.group(2):
                salario_max = int(salario_match.group(2))
                if 'k' in salario_match.group(0) or salario_max < 100:
                    salario_max *= 1000
                filtros_inferidos['salario_max'] = salario_max
        
        # Buscar com filtros inferidos
        resultados = self.filtros_avancados_completos(
            **filtros_inferidos,
            search=query,
            limit=50
        )
        
        return {
            "query_original": query,
            "filtros_inferidos": filtros_inferidos,
            "total_resultados": len(resultados),
            "vagas_encontradas": resultados,
            "sugestoes": self._gerar_sugestoes(query, filtros_inferidos, len(resultados))
        }
    
    def _gerar_sugestoes(self, query: str, filtros: Dict, total_resultados: int) -> List[str]:
        """Gerar sugestões baseadas na busca"""
        sugestoes = []
        
        if total_resultados == 0:
            sugestoes.append("Tente remover alguns filtros para ampliar a busca")
            sugestoes.append("Verifique a ortografia dos termos utilizados")
        elif total_resultados < 5:
            sugestoes.append("Poucos resultados encontrados. Considere termos mais genéricos")
        elif total_resultados > 100:
            sugestoes.append("Muitos resultados. Adicione mais filtros para refinar")
        
        if 'modalidade' not in filtros:
            sugestoes.append("Especifique a modalidade: remoto, presencial ou híbrido")
        
        if 'estado' not in filtros:
            sugestoes.append("Adicione uma localização específica para melhores resultados")
        
        if 'nivel_experiencia' not in filtros:
            sugestoes.append("Defina o nível de experiência desejado")
        
        return sugestoes
    
    def exportar_dados(self, filtros: Dict, formato: str = 'csv', arquivo: str = None) -> str:
        """Exportar dados filtrados em diferentes formatos"""
        vagas = self.filtros_avancados_completos(**filtros)
        
        if not vagas:
            return "Nenhum dado para exportar"
        
        df = pd.DataFrame(vagas)
        
        if not arquivo:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            arquivo = f"vagas_export_{timestamp}"
        
        if formato.lower() == 'csv':
            arquivo_final = f"{arquivo}.csv"
            df.to_csv(arquivo_final, index=False, encoding='utf-8')
        elif formato.lower() == 'excel':
            arquivo_final = f"{arquivo}.xlsx"
            df.to_excel(arquivo_final, index=False)
        elif formato.lower() == 'json':
            arquivo_final = f"{arquivo}.json"
            df.to_json(arquivo_final, orient='records', indent=2, force_ascii=False)
        else:
            return f"Formato {formato} não suportado"
        
        return f"Dados exportados para: {arquivo_final}"

# ==================== EXEMPLO DE USO COMPLETO ====================

if __name__ == "__main__":
    # Inicializar integração
    integration = VagasCompleteIntegration()
    
    print("🚀 Iniciando demonstração completa da API de Vagas")
    print("=" * 60)
    
    # 1. Obter amostra com todas as colunas
    print("\n1️⃣ Obtendo amostra com todas as 25 colunas...")
    amostra = integration.obter_amostra_completa(limite=10)
    if amostra:
        print(f"✅ {len(amostra)} vagas obtidas")
        print(f"📊 Colunas disponíveis: {list(amostra[0].keys())}")
        print(f"📝 Exemplo de vaga: {amostra[0]['titulo_vaga']} - {amostra[0]['empresa_principal']}")
    
    # 2. Filtros avançados
    print("\n2️⃣ Testando filtros avançados...")
    filtros_exemplo = {
        'setor': 'Tecnologia',
        'modalidade': 'Remoto',
        'nivel_experiencia': 'Pleno',
        'estado': 'SP',
        'salario_min': 5000,
        'habilidades_requeridas': 'Python',
        'limit': 20
    }
    
    vagas_filtradas = integration.filtros_avancados_completos(**filtros_exemplo)
    print(f"✅ {len(vagas_filtradas)} vagas encontradas com filtros avançados")
    
    # 3. Busca inteligente
    print("\n3️⃣ Testando busca inteligente...")
    queries_teste = [
        "vagas remotas de python senior",
        "desenvolvedor react junior são paulo",
        "analista de dados 8k a 12k"
    ]
    
    for query in queries_teste:
        resultado = integration.busca_inteligente(query)
        print(f"🔍 '{query}' → {resultado['total_resultados']} resultados")
        print(f"   Filtros inferidos: {resultado['filtros_inferidos']}")
    
    # 4. Análise completa do dataset
    print("\n4️⃣ Executando análise completa do dataset...")
    analise = integration.analise_completa_dataset()
    
    if "erro" not in analise:
        print(f"✅ Análise concluída!")
        print(f"📊 Total de vagas analisadas: {analise['resumo_geral']['total_vagas']}")
        print(f"💰 Vagas com salário: {analise['analise_salarial'].get('percentual_com_salario', 0):.1f}%")
        print(f"🛠️ Skills únicas identificadas: {analise['analise_skills'].get('total_skills_unicas', 0)}")
        
        # Top 5 skills
        top_skills = list(analise['analise_skills']['top_skills'].items())[:5]
        print(f"🏆 Top 5 skills: {[skill for skill, count in top_skills]}")
    
    # 5. Exportar dados
    print("\n5️⃣ Exportando dados...")
    arquivo_exportado = integration.exportar_dados(
        filtros={'setor': 'Tecnologia', 'limit': 100},
        formato='csv'
    )
    print(f"💾 {arquivo_exportado}")
    
    print("\n🎉 Demonstração completa finalizada!")
    print("=" * 60)
```

### Exemplo de Uso Simplificado

```python
# Uso rápido e direto
from vagas_integration import VagasCompleteIntegration

# Inicializar
api = VagasCompleteIntegration()

# Busca simples
vagas = api.obter_amostra_completa(limite=50)
print(f"Total de vagas: {len(vagas)}")

# Busca com filtros
vagas_tech = api.filtros_avancados_completos(
    setor='Tecnologia',
    modalidade='Remoto',
    salario_min=6000
)

# Busca inteligente
resultado = api.busca_inteligente("desenvolvedor python remoto senior")
print(f"Encontradas {resultado['total_resultados']} vagas")

# Análise completa
analise = api.analise_completa_dataset()
print(f"Análise de {analise['resumo_geral']['total_vagas']} vagas concluída")
```

    # Análise comparativa entre setores
    setores = ['Tecnologia', 'Saúde', 'Educação', 'Financeiro']
    for setor in setores:
        print(f"\n--- Análise {setor} ---")
        vagas = analyzer.buscar_vagas_filtradas(setor=setor, limit=100)
        print(f"Vagas encontradas: {len(vagas)}")
    # Análise comparativa entre setores
    setores = ['Tecnologia', 'Saúde', 'Educação', 'Financeiro']
    for setor in setores:
        print(f"\n--- Análise {setor} ---")
        vagas = analyzer.buscar_vagas_filtradas(setor=setor, limit=100)
        print(f"Vagas encontradas: {len(vagas)}")
        
        # Análise de oportunidades remotas por setor
        if vagas:
            remotas = [v for v in vagas if v.get('modalidade') == 'Remoto']
            pct_remoto = (len(remotas) / len(vagas)) * 100
            print(f"Percentual remoto: {pct_remoto:.1f}%")
            
            # Skills mais demandadas no setor
            skills_setor = analyzer.obter_skills_por_setor(setor)
            if skills_setor:
                print(f"Top 3 skills: {[s['skill'] for s in skills_setor[:3]]}")
```

### 3. Sistema de Recomendação de Vagas

```python
import requests
from typing import List, Dict
import re

class JobRecommendationSystem:
    def __init__(self, api_base_url):
        self.base_url = api_base_url
    
    def get_user_profile_jobs(self, user_skills: List[str], 
                             location_state: str = None,
                             seniority: str = None,
                             modality: str = None) -> List[Dict]:
        """Buscar vagas baseadas no perfil do usuário"""
        params = {
            'skills': ','.join(user_skills),
            'limit': 100
        }
        
        if location_state:
            params['location_state'] = location_state
        if seniority:
            params['seniority'] = seniority
        if modality:
            params['modality'] = modality
        
        response = requests.get(f'{self.base_url}/jobs-filtered', params=params)
        return response.json()
    
    def calculate_job_match_score(self, job: Dict, user_skills: List[str]) -> float:
        """Calcular score de compatibilidade entre usuário e vaga"""
        job_skills = [skill.lower() for skill in job.get('skills', [])]
        user_skills_lower = [skill.lower() for skill in user_skills]
        
        # Skills em comum
        common_skills = set(job_skills) & set(user_skills_lower)
        
        if not job_skills:
            return 0.0
        
        # Score baseado na porcentagem de skills em comum
        match_score = len(common_skills) / len(job_skills)
        
        # Bonus por skills raras/valiosas
        valuable_skills = ['machine learning', 'ai', 'blockchain', 'kubernetes', 'aws']
        bonus = sum(0.1 for skill in common_skills if any(vs in skill for vs in valuable_skills))
        
        return min(match_score + bonus, 1.0)
    
    def recommend_jobs(self, user_skills: List[str], 
                      location_state: str = None,
                      seniority: str = None,
                      modality: str = None,
                      top_n: int = 10) -> List[Dict]:
        """Recomendar vagas para o usuário"""
        jobs = self.get_user_profile_jobs(user_skills, location_state, seniority, modality)
        
        # Calcular score para cada vaga
        for job in jobs:
            job['match_score'] = self.calculate_job_match_score(job, user_skills)
        
        # Ordenar por score e retornar top N
        recommended_jobs = sorted(jobs, key=lambda x: x['match_score'], reverse=True)
        return recommended_jobs[:top_n]
    
    def get_skill_recommendations(self, user_skills: List[str], 
                                 target_sector: str = None) -> List[str]:
        """Recomendar skills para aprender baseado no mercado"""
        # Obter skills por setor
        response = requests.get(f'{self.base_url}/skills-by-sector')
        sector_data = response.json()
        
        recommended_skills = set()
        user_skills_lower = [skill.lower() for skill in user_skills]
        
        for sector in sector_data['sectors']:
            if target_sector and target_sector.lower() not in sector['sector'].lower():
                continue
                
            for skill_info in sector['top_skills']:
                skill = skill_info['skill'].lower()
                # Recomendar skills que o usuário não tem
                if skill not in user_skills_lower and skill_info['percentage'] > 10:
                    recommended_skills.add(skill_info['skill'])
        
        return list(recommended_skills)[:10]

# Exemplo de uso
recommender = JobRecommendationSystem('http://localhost:8000')

# Perfil do usuário
user_profile = {
    'skills': ['Python', 'Django', 'PostgreSQL'],
    'location_state': 'SP',
    'seniority': 'Pleno',
    'modality': 'Remoto'
}

# Recomendar vagas
recommended_jobs = recommender.recommend_jobs(**user_profile, top_n=5)

print("🎯 Vagas Recomendadas:")
for i, job in enumerate(recommended_jobs, 1):
    print(f"{i}. {job['title']} - {job['company_name']}")
    print(f"   Match: {job['match_score']:.2%}")
    print(f"   Skills: {', '.join(job['skills'][:5])}")
    print(f"   Localização: {job['location_city']}, {job['location_state']}")
    print()

# Recomendar skills para aprender
skill_recommendations = recommender.get_skill_recommendations(
    user_profile['skills'], 
    target_sector='Tecnologia'
)

print("📚 Skills Recomendadas para Aprender:")
for skill in skill_recommendations:
    print(f"- {skill}")
```

### 4. Monitoramento de Vagas - Webhook/Notificação

```python
import requests
import time
import json
from datetime import datetime

class JobMonitor:
    def __init__(self, api_base_url):
        self.base_url = api_base_url
        self.last_check = None
        self.monitored_searches = []
    
    def add_search_alert(self, name: str, search_params: Dict):
        """Adicionar alerta de busca"""
        self.monitored_searches.append({
            'name': name,
            'params': search_params,
            'last_count': 0
        })
    
    def check_new_jobs(self):
        """Verificar novas vagas para todas as buscas monitoradas"""
        results = []
        
        for search in self.monitored_searches:
            response = requests.get(f'{self.base_url}/jobs-filtered', 
                                  params=search['params'])
            current_jobs = response.json()
            current_count = len(current_jobs)
            
            if current_count > search['last_count']:
                new_jobs_count = current_count - search['last_count']
                results.append({
                    'search_name': search['name'],
                    'new_jobs': new_jobs_count,
                    'total_jobs': current_count,
                    'jobs': current_jobs[:new_jobs_count]  # Assumindo que novas vagas aparecem primeiro
                })
            
            search['last_count'] = current_count
        
        return results
    
    def send_notification(self, alerts: List[Dict]):
        """Enviar notificação (implementar webhook/email)"""
        for alert in alerts:
            print(f"🔔 ALERTA: {alert['search_name']}")
            print(f"   {alert['new_jobs']} novas vagas encontradas!")
            print(f"   Total de vagas: {alert['total_jobs']}")
            
            for job in alert['jobs'][:3]:  # Mostrar apenas as 3 primeiras
                print(f"   • {job['title']} - {job['company_name']}")
            print()
    
    def start_monitoring(self, interval_minutes: int = 30):
        """Iniciar monitoramento contínuo"""
        print(f"🔍 Iniciando monitoramento (verificação a cada {interval_minutes} minutos)")
        
        while True:
            try:
                alerts = self.check_new_jobs()
                if alerts:
                    self.send_notification(alerts)
                else:
                    print(f"✅ Verificação realizada às {datetime.now().strftime('%H:%M:%S')} - Nenhuma nova vaga")
                
                time.sleep(interval_minutes * 60)
                
            except KeyboardInterrupt:
                print("\n🛑 Monitoramento interrompido pelo usuário")
                break
            except Exception as e:
                print(f"❌ Erro no monitoramento: {e}")
                time.sleep(60)  # Aguardar 1 minuto antes de tentar novamente

# Exemplo de uso
monitor = JobMonitor('http://localhost:8000')

# Adicionar alertas de busca
monitor.add_search_alert(
    "Python Remoto SP",
    {'skills': 'Python', 'modality': 'Remoto', 'location_state': 'SP', 'limit': 50}
)

monitor.add_search_alert(
    "React Pleno",
    {'skills': 'React', 'seniority': 'Pleno', 'limit': 30}
)

monitor.add_search_alert(
    "Data Science",
    {'skills': 'Python,Machine Learning,Pandas', 'limit': 40}
)

# Iniciar monitoramento (verificar a cada 15 minutos)
# monitor.start_monitoring(interval_minutes=15)
```

### 5. Análise Salarial por Região e Skill

```python
import requests
import pandas as pd
import numpy as np

class SalaryAnalyzer:
    def __init__(self, api_base_url):
        self.base_url = api_base_url
    
    def get_salary_data_by_skill(self, skill: str, limit: int = 200):
        """Obter dados salariais para uma skill específica"""
        response = requests.get(f'{self.base_url}/jobs-filtered', 
                              params={'skills': skill, 'limit': limit})
        jobs = response.json()
        
        # Filtrar apenas vagas com informação salarial
        salary_data = []
        for job in jobs:
            if job.get('salary_min') and job.get('salary_max'):
                avg_salary = (job['salary_min'] + job['salary_max']) / 2
                salary_data.append({
                    'skill': skill,
                    'title': job['title'],
                    'company': job['company_name'],
                    'city': job['location_city'],
                    'state': job['location_state'],
                    'seniority': job['seniority'],
                    'modality': job['modality'],
                    'salary_min': job['salary_min'],
                    'salary_max': job['salary_max'],
                    'salary_avg': avg_salary
                })
        
        return pd.DataFrame(salary_data)
    
    def compare_skills_salary(self, skills: List[str]):
        """Comparar salários entre diferentes skills"""
        all_data = []
        
        for skill in skills:
            skill_data = self.get_salary_data_by_skill(skill)
            all_data.append(skill_data)
        
        combined_df = pd.concat(all_data, ignore_index=True)
        
        # Estatísticas por skill
        salary_stats = combined_df.groupby('skill')['salary_avg'].agg([
            'count', 'mean', 'median', 'std', 'min', 'max'
        ]).round(2)
        
        return salary_stats
    
    def analyze_salary_by_region(self, skill: str = None):
        """Analisar salários por região"""
        params = {'limit': 500}
        if skill:
            params['skills'] = skill
        
        response = requests.get(f'{self.base_url}/jobs-filtered', params=params)
        jobs = response.json()
        
        # Processar dados
        regional_data = []
        for job in jobs:
            if job.get('salary_min') and job.get('salary_max'):
                avg_salary = (job['salary_min'] + job['salary_max']) / 2
                regional_data.append({
                    'state': job['location_state'],
                    'city': job['location_city'],
                    'salary_avg': avg_salary,
                    'seniority': job['seniority']
                })
        
        df = pd.DataFrame(regional_data)
        
        # Estatísticas por estado
        state_stats = df.groupby('state')['salary_avg'].agg([
            'count', 'mean', 'median'
        ]).round(2)
        
        return state_stats.sort_values('mean', ascending=False)

# Exemplo de uso
analyzer = SalaryAnalyzer('http://localhost:8000')

# Comparar salários entre skills
skills_comparison = analyzer.compare_skills_salary([
    'Python', 'JavaScript', 'Java', 'React', 'Angular'
])

print("💰 Comparação Salarial por Skill:")
print(skills_comparison)

# Analisar salários por região para Python
python_regional = analyzer.analyze_salary_by_region('Python')
print("\n🗺️ Salários Python por Estado:")
print(python_regional.head(10))
```

## Dicas de Performance

1. **Use paginação**: Sempre defina `limit` apropriado para evitar timeouts
2. **Cache resultados**: Implemente cache local para dados que não mudam frequentemente
3. **Filtros específicos**: Use filtros mais específicos para reduzir o volume de dados
4. **Batch requests**: Agrupe múltiplas consultas quando possível

## Tratamento de Erros Robusto

```javascript
async function robustApiCall(endpoint, params = {}) {
    const maxRetries = 3;
    let retries = 0;
    
    while (retries < maxRetries) {
        try {
            const url = new URL(endpoint, 'http://localhost:8000');
            Object.keys(params).forEach(key => 
                url.searchParams.append(key, params[key])
            );
            
            const response = await fetch(url);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            return await response.json();
            
        } catch (error) {
            retries++;
            console.warn(`Tentativa ${retries} falhou:`, error.message);
            
            if (retries >= maxRetries) {
                throw new Error(`Falha após ${maxRetries} tentativas: ${error.message}`);
            }
            
            // Aguardar antes de tentar novamente
            await new Promise(resolve => setTimeout(resolve, 1000 * retries));
        }
    }
}

// Uso
robustApiCall('/jobs-filtered', { skills: 'Python', limit: 50 })
    .then(jobs => console.log('Vagas encontradas:', jobs.length))
    .catch(error => console.error('Erro final:', error.message));
```