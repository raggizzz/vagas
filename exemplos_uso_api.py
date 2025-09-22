#!/usr/bin/env python3
"""
Exemplos Práticos de Uso da API de Vagas e Skills
=================================================

Este arquivo contém exemplos práticos de como usar a API de Vagas e Skills
em diferentes cenários e linguagens de programação.

Requisitos:
- API rodando em http://localhost:8000
- Biblioteca requests instalada: pip install requests
"""

import requests
import json
from typing import List, Dict, Optional
import asyncio
import aiohttp

# Configuração base
BASE_URL = "http://localhost:8000"

class VagasAPIClient:
    """Cliente Python para a API de Vagas e Skills"""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
    
    def get_api_info(self) -> Dict:
        """Obtém informações básicas da API"""
        response = self.session.get(f"{self.base_url}/")
        response.raise_for_status()
        return response.json()
    
    def listar_vagas(self, limit: int = 50, offset: int = 0) -> List[Dict]:
        """Lista vagas com paginação"""
        params = {"limit": limit, "offset": offset}
        response = self.session.get(f"{self.base_url}/jobs", params=params)
        response.raise_for_status()
        return response.json()
    
    def filtrar_vagas(self, 
                     setor: Optional[str] = None,
                     localidade: Optional[str] = None,
                     modalidade: Optional[str] = None,
                     regime: Optional[str] = None,
                     limit: int = 50) -> List[Dict]:
        """Filtra vagas por critérios específicos"""
        params = {"limit": limit}
        
        if setor:
            params["setor"] = setor
        if localidade:
            params["localidade"] = localidade
        if modalidade:
            params["modalidade"] = modalidade
        if regime:
            params["regime"] = regime
        
        response = self.session.get(f"{self.base_url}/jobs-filtered", params=params)
        response.raise_for_status()
        return response.json()
    
    def obter_skills_por_setor(self) -> Dict:
        """Obtém estatísticas de skills por setor"""
        response = self.session.get(f"{self.base_url}/skills-by-sector")
        response.raise_for_status()
        return response.json()
    
    def buscar_vagas_tecnologia(self, modalidade: str = "Remoto", limit: int = 20) -> List[Dict]:
        """Busca específica para vagas de tecnologia"""
        return self.filtrar_vagas(
            setor="Tecnologia",
            modalidade=modalidade,
            limit=limit
        )
    
    def analisar_mercado_trabalho(self) -> Dict:
        """Análise completa do mercado de trabalho"""
        # Obter estatísticas de skills
        skills_stats = self.obter_skills_por_setor()
        
        # Obter vagas por modalidade
        vagas_remotas = len(self.filtrar_vagas(modalidade="Remoto", limit=1000))
        vagas_presenciais = len(self.filtrar_vagas(modalidade="Presencial", limit=1000))
        vagas_hibridas = len(self.filtrar_vagas(modalidade="Híbrido", limit=1000))
        
        return {
            "skills_por_setor": skills_stats,
            "distribuicao_modalidade": {
                "Remoto": vagas_remotas,
                "Presencial": vagas_presenciais,
                "Híbrido": vagas_hibridas
            }
        }

# ============================================================================
# EXEMPLOS DE USO BÁSICO
# ============================================================================

def exemplo_basico():
    """Exemplo básico de uso da API"""
    print("🔍 Exemplo Básico - Listando primeiras 10 vagas")
    
    client = VagasAPIClient()
    
    # Obter informações da API
    info = client.get_api_info()
    print(f"API: {info['message']}")
    print(f"Versão: {info['version']}")
    
    # Listar primeiras 10 vagas
    vagas = client.listar_vagas(limit=10)
    print(f"\n📋 Encontradas {len(vagas)} vagas:")
    
    for vaga in vagas[:3]:  # Mostrar apenas 3 para exemplo
        print(f"- {vaga['titulo']} na {vaga.get('empresa', 'N/A')}")
        print(f"  Setor: {vaga.get('setor', 'N/A')} | Modalidade: {vaga.get('modalidade', 'N/A')}")
        print()

def exemplo_filtros():
    """Exemplo de uso de filtros"""
    print("🎯 Exemplo de Filtros - Vagas de Tecnologia Remotas")
    
    client = VagasAPIClient()
    
    # Filtrar vagas de tecnologia remotas
    vagas_tech = client.filtrar_vagas(
        setor="Tecnologia",
        modalidade="Remoto",
        limit=15
    )
    
    print(f"📊 Encontradas {len(vagas_tech)} vagas de tecnologia remotas:")
    
    for vaga in vagas_tech[:5]:  # Mostrar apenas 5
        skills = vaga.get('habilidades', [])
        skills_str = ', '.join(skills[:3]) if skills else 'N/A'
        
        print(f"- {vaga['titulo']}")
        print(f"  Empresa: {vaga.get('empresa', 'N/A')}")
        print(f"  Skills: {skills_str}")
        print(f"  Salário: {vaga.get('salario', 'N/A')}")
        print()

def exemplo_skills_por_setor():
    """Exemplo de análise de skills por setor"""
    print("📈 Exemplo de Skills por Setor")
    
    client = VagasAPIClient()
    
    # Obter estatísticas de skills
    stats = client.obter_skills_por_setor()
    
    print(f"📊 Análise de {len(stats.get('sectors', []))} setores:")
    
    for setor in stats.get('sectors', [])[:3]:  # Mostrar apenas 3 setores
        print(f"\n🏢 Setor: {setor['sector']}")
        print(f"   Total de vagas: {setor['total_jobs']}")
        print("   Top 5 skills:")
        
        for skill in setor.get('top_skills', [])[:5]:
            print(f"   - {skill['skill']}: {skill['count']} vagas")

# ============================================================================
# EXEMPLOS AVANÇADOS
# ============================================================================

def exemplo_analise_mercado():
    """Exemplo de análise completa do mercado"""
    print("🔬 Análise Completa do Mercado de Trabalho")
    
    client = VagasAPIClient()
    
    # Análise completa
    analise = client.analisar_mercado_trabalho()
    
    # Mostrar distribuição por modalidade
    print("\n📊 Distribuição por Modalidade:")
    modalidades = analise['distribuicao_modalidade']
    total_vagas = sum(modalidades.values())
    
    for modalidade, count in modalidades.items():
        percentual = (count / total_vagas * 100) if total_vagas > 0 else 0
        print(f"   {modalidade}: {count} vagas ({percentual:.1f}%)")
    
    # Mostrar top skills geral
    print("\n🎯 Skills Mais Demandadas por Setor:")
    for setor in analise['skills_por_setor'].get('sectors', [])[:2]:
        print(f"\n   {setor['sector']}:")
        for skill in setor.get('top_skills', [])[:3]:
            print(f"   - {skill['skill']}: {skill['count']} vagas")

def exemplo_busca_personalizada():
    """Exemplo de busca personalizada para diferentes perfis"""
    print("👤 Buscas Personalizadas por Perfil")
    
    client = VagasAPIClient()
    
    # Perfil 1: Desenvolvedor Python Remoto
    print("\n🐍 Perfil: Desenvolvedor Python Remoto")
    vagas_python = client.filtrar_vagas(
        setor="Tecnologia",
        modalidade="Remoto",
        limit=10
    )
    
    # Filtrar vagas que mencionam Python nas skills
    vagas_python_filtered = [
        vaga for vaga in vagas_python 
        if any('python' in skill.lower() for skill in vaga.get('habilidades', []))
    ]
    
    print(f"   Encontradas {len(vagas_python_filtered)} vagas Python remotas")
    
    # Perfil 2: Vagas Presenciais em São Paulo
    print("\n🏢 Perfil: Vagas Presenciais em São Paulo")
    vagas_sp = client.filtrar_vagas(
        localidade="São Paulo",
        modalidade="Presencial",
        limit=10
    )
    print(f"   Encontradas {len(vagas_sp)} vagas presenciais em SP")
    
    # Perfil 3: Vagas CLT
    print("\n📄 Perfil: Vagas CLT")
    vagas_clt = client.filtrar_vagas(
        regime="CLT",
        limit=10
    )
    print(f"   Encontradas {len(vagas_clt)} vagas CLT")

# ============================================================================
# EXEMPLOS COM ASYNC/AWAIT
# ============================================================================

class AsyncVagasAPIClient:
    """Cliente assíncrono para a API"""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
    
    async def get_vagas_async(self, session: aiohttp.ClientSession, **params) -> List[Dict]:
        """Busca vagas de forma assíncrona"""
        async with session.get(f"{self.base_url}/jobs-filtered", params=params) as response:
            response.raise_for_status()
            return await response.json()
    
    async def busca_paralela(self) -> Dict:
        """Executa múltiplas buscas em paralelo"""
        async with aiohttp.ClientSession() as session:
            # Executar múltiplas buscas em paralelo
            tasks = [
                self.get_vagas_async(session, setor="Tecnologia", limit=20),
                self.get_vagas_async(session, modalidade="Remoto", limit=20),
                self.get_vagas_async(session, regime="CLT", limit=20),
            ]
            
            resultados = await asyncio.gather(*tasks)
            
            return {
                "vagas_tecnologia": resultados[0],
                "vagas_remotas": resultados[1],
                "vagas_clt": resultados[2]
            }

async def exemplo_async():
    """Exemplo de uso assíncrono"""
    print("⚡ Exemplo Assíncrono - Buscas Paralelas")
    
    client = AsyncVagasAPIClient()
    resultados = await client.busca_paralela()
    
    print(f"📊 Resultados das buscas paralelas:")
    print(f"   Vagas de Tecnologia: {len(resultados['vagas_tecnologia'])}")
    print(f"   Vagas Remotas: {len(resultados['vagas_remotas'])}")
    print(f"   Vagas CLT: {len(resultados['vagas_clt'])}")

# ============================================================================
# EXEMPLOS DE INTEGRAÇÃO COM OUTRAS FERRAMENTAS
# ============================================================================

def exemplo_exportar_csv():
    """Exemplo de exportação para CSV"""
    print("📄 Exemplo: Exportar Vagas para CSV")
    
    import csv
    
    client = VagasAPIClient()
    vagas = client.filtrar_vagas(setor="Tecnologia", limit=50)
    
    # Exportar para CSV
    filename = "vagas_tecnologia.csv"
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        if vagas:
            fieldnames = ['titulo', 'empresa', 'setor', 'modalidade', 'localidade', 'salario']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for vaga in vagas:
                row = {field: vaga.get(field, '') for field in fieldnames}
                writer.writerow(row)
    
    print(f"   ✅ Exportadas {len(vagas)} vagas para {filename}")

def exemplo_dashboard_simples():
    """Exemplo de dashboard simples com estatísticas"""
    print("📊 Dashboard Simples - Estatísticas do Mercado")
    
    client = VagasAPIClient()
    
    # Coletar dados
    stats = client.obter_skills_por_setor()
    
    print("\n" + "="*50)
    print("           DASHBOARD DE VAGAS")
    print("="*50)
    
    # Estatísticas gerais
    total_setores = len(stats.get('sectors', []))
    print(f"📈 Total de Setores Analisados: {total_setores}")
    
    # Top 3 setores com mais vagas
    setores_ordenados = sorted(
        stats.get('sectors', []), 
        key=lambda x: x['total_jobs'], 
        reverse=True
    )
    
    print(f"\n🏆 Top 3 Setores com Mais Vagas:")
    for i, setor in enumerate(setores_ordenados[:3], 1):
        print(f"   {i}. {setor['sector']}: {setor['total_jobs']} vagas")
    
    # Skills mais demandadas globalmente
    all_skills = {}
    for setor in stats.get('sectors', []):
        for skill in setor.get('top_skills', []):
            skill_name = skill['skill']
            all_skills[skill_name] = all_skills.get(skill_name, 0) + skill['count']
    
    top_skills_global = sorted(all_skills.items(), key=lambda x: x[1], reverse=True)[:5]
    
    print(f"\n🎯 Top 5 Skills Mais Demandadas (Global):")
    for i, (skill, count) in enumerate(top_skills_global, 1):
        print(f"   {i}. {skill}: {count} vagas")
    
    print("="*50)

# ============================================================================
# EXEMPLOS EM JAVASCRIPT (para referência)
# ============================================================================

def gerar_exemplos_javascript():
    """Gera exemplos em JavaScript para referência"""
    js_code = '''
// ============================================================================
// EXEMPLOS EM JAVASCRIPT
// ============================================================================

// Configuração base
const BASE_URL = 'http://localhost:8000';

// Classe cliente para a API
class VagasAPIClient {
    constructor(baseUrl = BASE_URL) {
        this.baseUrl = baseUrl;
    }

    async getApiInfo() {
        const response = await fetch(`${this.baseUrl}/`);
        return await response.json();
    }

    async listarVagas(limit = 50, offset = 0) {
        const params = new URLSearchParams({ limit, offset });
        const response = await fetch(`${this.baseUrl}/jobs?${params}`);
        return await response.json();
    }

    async filtrarVagas(filtros = {}) {
        const params = new URLSearchParams(filtros);
        const response = await fetch(`${this.baseUrl}/jobs-filtered?${params}`);
        return await response.json();
    }

    async obterSkillsPorSetor() {
        const response = await fetch(`${this.baseUrl}/skills-by-sector`);
        return await response.json();
    }
}

// Exemplo de uso básico
async function exemploBasico() {
    const client = new VagasAPIClient();
    
    // Obter informações da API
    const info = await client.getApiInfo();
    console.log('API:', info.message);
    
    // Listar vagas
    const vagas = await client.listarVagas(10);
    console.log(`Encontradas ${vagas.length} vagas`);
    
    vagas.slice(0, 3).forEach(vaga => {
        console.log(`- ${vaga.titulo} na ${vaga.empresa || 'N/A'}`);
    });
}

// Exemplo com filtros
async function exemploFiltros() {
    const client = new VagasAPIClient();
    
    const vagasTech = await client.filtrarVagas({
        setor: 'Tecnologia',
        modalidade: 'Remoto',
        limit: 15
    });
    
    console.log(`Encontradas ${vagasTech.length} vagas de tecnologia remotas`);
}

// Exemplo de análise de skills
async function exemploSkills() {
    const client = new VagasAPIClient();
    
    const stats = await client.obterSkillsPorSetor();
    
    stats.sectors.slice(0, 3).forEach(setor => {
        console.log(`Setor: ${setor.sector}`);
        console.log(`Total de vagas: ${setor.total_jobs}`);
        
        setor.top_skills.slice(0, 5).forEach(skill => {
            console.log(`  - ${skill.skill}: ${skill.count} vagas`);
        });
    });
}

// Executar exemplos
exemploBasico();
exemploFiltros();
exemploSkills();
'''
    
    with open("exemplos_javascript.js", "w", encoding="utf-8") as f:
        f.write(js_code)
    
    print("📄 Exemplos JavaScript salvos em 'exemplos_javascript.js'")

# ============================================================================
# FUNÇÃO PRINCIPAL
# ============================================================================

def main():
    """Executa todos os exemplos"""
    print("🚀 Executando Exemplos da API de Vagas e Skills")
    print("=" * 60)
    
    try:
        # Verificar se a API está rodando
        response = requests.get(f"{BASE_URL}/")
        if response.status_code != 200:
            print("❌ API não está rodando. Inicie a API primeiro:")
            print("   python api_vagas_skills.py")
            return
        
        print("✅ API está rodando!")
        print()
        
        # Executar exemplos
        exemplo_basico()
        print("\n" + "-" * 60 + "\n")
        
        exemplo_filtros()
        print("\n" + "-" * 60 + "\n")
        
        exemplo_skills_por_setor()
        print("\n" + "-" * 60 + "\n")
        
        exemplo_analise_mercado()
        print("\n" + "-" * 60 + "\n")
        
        exemplo_busca_personalizada()
        print("\n" + "-" * 60 + "\n")
        
        exemplo_dashboard_simples()
        print("\n" + "-" * 60 + "\n")
        
        exemplo_exportar_csv()
        print("\n" + "-" * 60 + "\n")
        
        # Exemplo assíncrono
        print("⚡ Executando exemplo assíncrono...")
        asyncio.run(exemplo_async())
        print("\n" + "-" * 60 + "\n")
        
        # Gerar exemplos JavaScript
        gerar_exemplos_javascript()
        
        print("\n🎉 Todos os exemplos executados com sucesso!")
        print("\n📚 Para mais informações, consulte:")
        print("   - Documentação: API_VAGAS_SKILLS_DOCUMENTATION.md")
        print("   - Swagger UI: http://localhost:8000/docs")
        print("   - ReDoc: http://localhost:8000/redoc")
        
    except requests.exceptions.ConnectionError:
        print("❌ Erro de conexão com a API.")
        print("   Verifique se a API está rodando em http://localhost:8000")
        print("   Execute: python api_vagas_skills.py")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

if __name__ == "__main__":
    main()