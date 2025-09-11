#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para testar os novos endpoints de Skills e Setores da API
Testa todos os endpoints relacionados a skills_agg e sector_map
"""

import requests
import json
from datetime import datetime

# Configuração da API
API_BASE_URL = "http://localhost:5000"

def test_endpoint(endpoint, method="GET", params=None, data=None):
    """Função auxiliar para testar endpoints"""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        
        if method == "GET":
            response = requests.get(url, params=params)
        elif method == "POST":
            response = requests.post(url, json=data)
        
        print(f"\n{'='*60}")
        print(f"Testando: {method} {endpoint}")
        if params:
            print(f"Parâmetros: {params}")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if 'data' in result:
                data_content = result['data']
                if isinstance(data_content, dict):
                    # Mostrar estatísticas resumidas
                    for key, value in data_content.items():
                        if isinstance(value, list):
                            print(f"{key}: {len(value)} itens")
                        else:
                            print(f"{key}: {value}")
                elif isinstance(data_content, list):
                    print(f"Retornou {len(data_content)} itens")
                    if data_content:
                        print(f"Primeiro item: {list(data_content[0].keys()) if isinstance(data_content[0], dict) else data_content[0]}")
            else:
                print(f"Resposta: {result}")
        else:
            print(f"Erro: {response.text}")
            
        return response
        
    except requests.exceptions.ConnectionError:
        print(f"\n❌ ERRO: Não foi possível conectar à API em {API_BASE_URL}")
        print("Certifique-se de que a API está rodando!")
        return None
    except Exception as e:
        print(f"\n❌ ERRO: {str(e)}")
        return None

def main():
    """Função principal para executar todos os testes"""
    print("🚀 Iniciando testes dos novos endpoints de Skills e Setores")
    print(f"API Base URL: {API_BASE_URL}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    # Testar endpoint raiz primeiro para verificar se API está rodando
    print("\n📋 Verificando se a API está rodando...")
    root_response = test_endpoint("/")
    if not root_response or root_response.status_code != 200:
        print("\n❌ API não está respondendo. Encerrando testes.")
        return
    
    print("\n✅ API está rodando! Iniciando testes dos novos endpoints...")
    
    # ===== TESTES DE SKILLS =====
    print("\n\n🎯 TESTANDO ENDPOINTS DE SKILLS")
    
    # 1. Estatísticas de Skills
    test_endpoint("/skills/statistics")
    test_endpoint("/skills/statistics", params={"limit": 10})
    test_endpoint("/skills/statistics", params={"category": "Programação", "limit": 5})
    test_endpoint("/skills/statistics", params={"skill_type": "technical"})
    
    # 2. Top Skills
    test_endpoint("/skills/top")
    test_endpoint("/skills/top", params={"limit": 10, "by": "total_jobs"})
    test_endpoint("/skills/top", params={"limit": 5, "by": "percentage"})
    test_endpoint("/skills/top", params={"by": "avg_salary_max"})
    
    # 3. Busca de Skills
    test_endpoint("/skills/search", params={"q": "Python"})
    test_endpoint("/skills/search", params={"q": "Java", "limit": 5})
    test_endpoint("/skills/search", params={"q": "SQL"})
    test_endpoint("/skills/search", params={"q": "comunicação"})
    
    # Teste de erro - busca sem parâmetro
    test_endpoint("/skills/search")
    
    # ===== TESTES DE SETORES =====
    print("\n\n🏭 TESTANDO ENDPOINTS DE SETORES")
    
    # 1. Análise de Setores
    test_endpoint("/sectors/analysis")
    test_endpoint("/sectors/analysis", params={"limit": 10})
    test_endpoint("/sectors/analysis", params={"category": "tertiary"})
    
    # 2. Mapeamento de Setores
    test_endpoint("/sectors/mapping")
    test_endpoint("/sectors/mapping", params={"original_sector": "Tecnologia"})
    test_endpoint("/sectors/mapping", params={"normalized_sector": "TI"})
    
    # 3. Cobertura de Setores
    test_endpoint("/sectors/coverage")
    test_endpoint("/sectors/coverage", params={"limit": 15})
    
    # ===== TESTE ADMINISTRATIVO =====
    print("\n\n⚙️ TESTANDO ENDPOINT ADMINISTRATIVO")
    
    # Recalcular estatísticas (POST)
    test_endpoint("/admin/recalculate-stats", method="POST")
    
    # ===== TESTES DE HEALTH CHECK =====
    print("\n\n🏥 TESTANDO HEALTH CHECK")
    test_endpoint("/health")
    
    print("\n\n✅ Todos os testes concluídos!")
    print("\n📊 RESUMO DOS NOVOS ENDPOINTS:")
    print("   • /skills/statistics - Estatísticas agregadas de skills")
    print("   • /skills/top - Top skills mais demandadas")
    print("   • /skills/search - Buscar skills por nome")
    print("   • /sectors/analysis - Análise completa de setores")
    print("   • /sectors/mapping - Mapeamento de setores")
    print("   • /sectors/coverage - Cobertura de vagas por setor")
    print("   • /admin/recalculate-stats - Recalcular estatísticas (POST)")
    
    print("\n💡 Para usar a API:")
    print(f"   • Acesse {API_BASE_URL}/ para ver todos os endpoints")
    print(f"   • Use parâmetros como ?limit=10&category=Programação")
    print(f"   • Para busca: ?q=Python&limit=20")

if __name__ == "__main__":
    main()