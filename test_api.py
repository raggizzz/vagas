#!/usr/bin/env python3
"""
Script de teste para a API de Vagas e Skills
Testa os principais endpoints e funcionalidades
"""

import requests
import json
from typing import Dict, Any

# Configuração da API
API_BASE_URL = "http://localhost:8000"

def test_endpoint(endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
    """Testa um endpoint da API"""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        response = requests.get(url, params=params, timeout=10)
        
        print(f"\n🔍 Testando: {endpoint}")
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Sucesso! Retornou {len(data) if isinstance(data, list) else 1} item(s)")
            return data
        else:
            print(f"❌ Erro: {response.text}")
            return {}
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro de conexão: {e}")
        return {}
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return {}

def main():
    """Executa todos os testes da API"""
    print("🚀 Iniciando testes da API de Vagas e Skills")
    print(f"🌐 URL base: {API_BASE_URL}")
    
    # Teste 1: Endpoint raiz
    print("\n" + "="*50)
    print("TESTE 1: Endpoint raiz")
    root_data = test_endpoint("/")
    if root_data:
        print(f"📋 Endpoints disponíveis: {list(root_data.get('endpoints', {}).keys())}")
    
    # Teste 2: Estatísticas gerais
    print("\n" + "="*50)
    print("TESTE 2: Estatísticas gerais")
    stats_data = test_endpoint("/stats")
    if stats_data:
        print(f"📊 Total de vagas: {stats_data.get('total_jobs', 0)}")
        print(f"🏢 Total de empresas: {stats_data.get('total_companies', 0)}")
        print(f"🛠️ Total de skills: {stats_data.get('total_skills', 0)}")
        
        top_skills = stats_data.get('top_skills', [])
        if top_skills:
            print(f"🔝 Top 3 skills:")
            for i, skill in enumerate(top_skills[:3], 1):
                print(f"   {i}. {skill.get('skill', 'N/A')} ({skill.get('count', 0)} vagas)")
    
    # Teste 3: Listar vagas (primeiras 5)
    print("\n" + "="*50)
    print("TESTE 3: Listar vagas")
    jobs_data = test_endpoint("/jobs", {"limit": 5})
    if jobs_data:
        print(f"📋 Primeiras 5 vagas:")
        for i, job in enumerate(jobs_data[:3], 1):
            print(f"   {i}. {job.get('title', 'N/A')} - {job.get('company_name', 'N/A')}")
            print(f"      📍 {job.get('location_city', 'N/A')}/{job.get('location_state', 'N/A')}")
            skills = job.get('skills', [])
            if skills:
                print(f"      🛠️ Skills: {', '.join(skills[:3])}{'...' if len(skills) > 3 else ''}")
    
    # Teste 4: Top skills
    print("\n" + "="*50)
    print("TESTE 4: Top skills")
    skills_data = test_endpoint("/skills", {"limit": 10})
    if skills_data:
        print(f"🛠️ Top 10 skills mais demandadas:")
        for i, skill in enumerate(skills_data[:10], 1):
            print(f"   {i:2d}. {skill.get('skill', 'N/A'):30} ({skill.get('count', 0):3d} vagas - {skill.get('percentage', 0):5.1f}%)")
    
    # Teste 5: Busca por skill específica
    print("\n" + "="*50)
    print("TESTE 5: Busca por skill (Python)")
    python_jobs = test_endpoint("/jobs", {"skills": "Python", "limit": 3})
    if python_jobs:
        print(f"🐍 Vagas com Python ({len(python_jobs)} encontradas):")
        for i, job in enumerate(python_jobs[:3], 1):
            print(f"   {i}. {job.get('title', 'N/A')} - {job.get('company_name', 'N/A')}")
    
    # Teste 6: Busca por localização
    print("\n" + "="*50)
    print("TESTE 6: Busca por localização (SP)")
    sp_jobs = test_endpoint("/jobs", {"location_state": "SP", "limit": 3})
    if sp_jobs:
        print(f"🏙️ Vagas em SP ({len(sp_jobs)} encontradas):")
        for i, job in enumerate(sp_jobs[:3], 1):
            print(f"   {i}. {job.get('title', 'N/A')} - {job.get('location_city', 'N/A')}")
    
    # Teste 7: Busca por modalidade
    print("\n" + "="*50)
    print("TESTE 7: Busca por modalidade (Remoto)")
    remote_jobs = test_endpoint("/jobs", {"modality": "Remoto", "limit": 3})
    if remote_jobs:
        print(f"🏠 Vagas remotas ({len(remote_jobs)} encontradas):")
        for i, job in enumerate(remote_jobs[:3], 1):
            print(f"   {i}. {job.get('title', 'N/A')} - {job.get('modality', 'N/A')}")
    
    # Teste 8: Busca textual
    print("\n" + "="*50)
    print("TESTE 8: Busca textual (desenvolvedor)")
    search_jobs = test_endpoint("/search", {"q": "desenvolvedor", "limit": 3})
    if search_jobs:
        print(f"🔍 Busca por 'desenvolvedor' ({len(search_jobs)} encontradas):")
        for i, job in enumerate(search_jobs[:3], 1):
            print(f"   {i}. {job.get('title', 'N/A')} - {job.get('area', 'N/A')}")
    
    # Teste 9: Detalhes de uma vaga específica
    if jobs_data and len(jobs_data) > 0:
        job_id = jobs_data[0].get('id')
        if job_id:
            print("\n" + "="*50)
            print(f"TESTE 9: Detalhes da vaga {job_id}")
            job_detail = test_endpoint(f"/jobs/{job_id}")
            if job_detail:
                print(f"📋 Título: {job_detail.get('title', 'N/A')}")
                print(f"🏢 Empresa: {job_detail.get('company_name', 'N/A')}")
                print(f"📍 Local: {job_detail.get('location_city', 'N/A')}/{job_detail.get('location_state', 'N/A')}")
                print(f"💼 Tipo: {job_detail.get('employment_type', 'N/A')}")
                print(f"🏠 Modalidade: {job_detail.get('modality', 'N/A')}")
                skills = job_detail.get('skills', [])
                if skills:
                    print(f"🛠️ Skills ({len(skills)}): {', '.join(skills[:5])}{'...' if len(skills) > 5 else ''}")
    
    print("\n" + "="*50)
    print("✅ Testes concluídos!")
    print("\n💡 Para usar a API:")
    print(f"   - Documentação interativa: {API_BASE_URL}/docs")
    print(f"   - Esquema OpenAPI: {API_BASE_URL}/openapi.json")
    print("\n🔧 Exemplos de uso:")
    print(f"   - Vagas com Python: {API_BASE_URL}/jobs?skills=Python")
    print(f"   - Vagas em SP: {API_BASE_URL}/jobs?location_state=SP")
    print(f"   - Vagas remotas: {API_BASE_URL}/jobs?modality=Remoto")
    print(f"   - Buscar 'desenvolvedor': {API_BASE_URL}/search?q=desenvolvedor")

if __name__ == "__main__":
    main()