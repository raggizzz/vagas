import json
import os
from supabase_uploader import SupabaseUploader
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

def test_supabase_connection():
    """Testa a conexão com o Supabase"""
    print("🔍 Testando conexão com Supabase...")
    
    try:
        uploader = SupabaseUploader()
        print("✅ Conexão estabelecida com sucesso!")
        return uploader
    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
        return None

def create_sample_data():
    """Cria dados de amostra para teste"""
    sample_jobs = [
        {
            "id": "test_001",
            "title": "Desenvolvedor Python - TESTE",
            "company": "Empresa Teste LTDA",
            "location": "São Paulo, SP",
            "work_type": "CLT",
            "contract_type": "Efetivo",
            "work_model": "Remoto",
            "description": "Vaga de teste para integração com Supabase",
            "description_raw": "<p>Vaga de teste para integração com Supabase</p>",
            "link": "https://teste.com/vaga/001",
            "published_date": "2025-01-05",
            "extraction_timestamp": "2025-01-05T13:54:00",
            "data_quality_score": 85,
            "salary": {
                "min_salary": 5000.0,
                "max_salary": 8000.0,
                "salary_type": "range",
                "currency": "BRL",
                "period": "mensal"
            },
            "responsibilities": [
                "Desenvolver aplicações Python",
                "Integrar com APIs REST",
                "Trabalhar com bancos de dados"
            ],
            "benefits": [
                "Vale refeição",
                "Plano de saúde",
                "Home office"
            ],
            "education": [
                "Superior completo em Tecnologia"
            ],
            "skills": [
                "Python",
                "Django",
                "PostgreSQL",
                "Git"
            ],
            "experience": "2-4 anos de experiência em desenvolvimento Python"
        },
        {
            "id": "test_002",
            "title": "Analista de Dados - TESTE",
            "company": "DataTech Soluções",
            "location": "Rio de Janeiro, RJ",
            "work_type": "PJ",
            "contract_type": "Freelancer",
            "work_model": "Híbrido",
            "description": "Segunda vaga de teste para validação",
            "description_raw": "<p>Segunda vaga de teste para validação</p>",
            "link": "https://teste.com/vaga/002",
            "published_date": "2025-01-05",
            "extraction_timestamp": "2025-01-05T13:55:00",
            "data_quality_score": 92,
            "salary": {
                "min_salary": 4000.0,
                "max_salary": 6000.0,
                "salary_type": "range",
                "currency": "BRL",
                "period": "mensal"
            },
            "responsibilities": [
                "Analisar dados de vendas",
                "Criar dashboards",
                "Gerar relatórios executivos"
            ],
            "benefits": [
                "Vale transporte",
                "Seguro de vida"
            ],
            "education": [
                "Superior em Estatística ou áreas afins"
            ],
            "skills": [
                "Python",
                "Pandas",
                "Power BI",
                "SQL"
            ],
            "experience": "1-3 anos em análise de dados"
        }
    ]
    
    return {"jobs": sample_jobs}

def test_sample_upload(uploader):
    """Testa o upload de dados de amostra"""
    print("\n📤 Testando upload de dados de amostra...")
    
    try:
        # Cria dados de teste
        sample_data = create_sample_data()
        
        # Salva arquivo temporário
        test_file = 'test_sample.json'
        with open(test_file, 'w', encoding='utf-8') as f:
            json.dump(sample_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Arquivo de teste criado: {test_file}")
        
        # Faz upload
        uploader.upload_json_file(test_file, batch_size=10)
        
        # Remove arquivo temporário
        os.remove(test_file)
        print(f"🗑️ Arquivo temporário removido")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de upload: {e}")
        return False

def test_database_queries(uploader):
    """Testa algumas consultas básicas no banco"""
    print("\n🔍 Testando consultas no banco de dados...")
    
    try:
        # Testa consulta de vagas
        jobs_result = uploader.supabase.table('jobs').select('id, title, company_name').limit(5).execute()
        print(f"✅ Consulta de vagas: {len(jobs_result.data)} registros encontrados")
        
        if jobs_result.data:
            print("📋 Primeiras vagas encontradas:")
            for job in jobs_result.data[:3]:
                print(f"   - {job['title']} ({job['company_name']})")
        
        # Testa consulta de empresas
        companies_result = uploader.supabase.table('companies').select('id, name').limit(5).execute()
        print(f"✅ Consulta de empresas: {len(companies_result.data)} registros encontrados")
        
        # Testa view completa
        complete_jobs = uploader.supabase.table('jobs_complete').select('*').limit(2).execute()
        print(f"✅ View jobs_complete: {len(complete_jobs.data)} registros encontrados")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro nas consultas: {e}")
        return False

def cleanup_test_data(uploader):
    """Remove dados de teste do banco"""
    print("\n🧹 Limpando dados de teste...")
    
    try:
        # Remove vagas de teste
        uploader.supabase.table('jobs').delete().like('title', '%TESTE%').execute()
        print("✅ Vagas de teste removidas")
        
        # Remove empresas de teste
        uploader.supabase.table('companies').delete().like('name', '%Teste%').execute()
        print("✅ Empresas de teste removidas")
        
        return True
        
    except Exception as e:
        print(f"⚠️ Erro na limpeza (normal se não houver dados): {e}")
        return False

def main():
    """Função principal de teste"""
    print("🚀 Iniciando testes de integração com Supabase\n")
    
    # Verifica variáveis de ambiente
    if not os.getenv('SUPABASE_URL') or not os.getenv('SUPABASE_KEY'):
        print("❌ Variáveis de ambiente SUPABASE_URL e SUPABASE_KEY não encontradas!")
        print("💡 Crie um arquivo .env baseado no .env.example")
        return
    
    # Teste 1: Conexão
    uploader = test_supabase_connection()
    if not uploader:
        return
    
    # Teste 2: Estatísticas iniciais
    print("\n📊 Estatísticas antes do teste:")
    initial_stats = uploader.get_database_stats()
    
    # Teste 3: Upload de amostra
    upload_success = test_sample_upload(uploader)
    if not upload_success:
        return
    
    # Teste 4: Consultas
    query_success = test_database_queries(uploader)
    
    # Teste 5: Estatísticas finais
    print("\n📊 Estatísticas após o teste:")
    final_stats = uploader.get_database_stats()
    
    # Teste 6: Limpeza (opcional)
    print("\n❓ Deseja remover os dados de teste? (s/n): ", end="")
    try:
        choice = input().lower().strip()
        if choice in ['s', 'sim', 'y', 'yes']:
            cleanup_test_data(uploader)
    except:
        print("\n⏭️ Pulando limpeza...")
    
    # Resumo final
    print("\n" + "="*50)
    print("📋 RESUMO DOS TESTES")
    print("="*50)
    print(f"✅ Conexão: {'OK' if uploader else 'FALHOU'}")
    print(f"✅ Upload: {'OK' if upload_success else 'FALHOU'}")
    print(f"✅ Consultas: {'OK' if query_success else 'FALHOU'}")
    
    if all([uploader, upload_success, query_success]):
        print("\n🎉 Todos os testes passaram! Supabase está funcionando corretamente.")
        print("\n💡 Próximos passos:")
        print("   1. Configure suas credenciais reais do Supabase no .env")
        print("   2. Execute o schema SQL no seu projeto Supabase")
        print("   3. Execute supabase_uploader.py para fazer upload dos dados reais")
    else:
        print("\n❌ Alguns testes falharam. Verifique a configuração.")

if __name__ == "__main__":
    main()