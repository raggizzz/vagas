

from flask import Flask, jsonify, request
from flask_cors import CORS
from supabase import create_client, Client
from dotenv import load_dotenv
import os
from datetime import datetime
from typing import Dict, List, Any, Optional

# Carregar variáveis de ambiente
load_dotenv()

app = Flask(__name__)
CORS(app)  # Permitir requisições de qualquer origem

# Configuração do Supabase
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY') or os.getenv('SUPABASE_ANON_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL e SUPABASE_KEY devem estar definidas no arquivo .env")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

class VagasAPI:
    """Classe para gerenciar operações da API de vagas"""
    
    @staticmethod
    def format_response(data: Any, message: str = "Sucesso", status: int = 200) -> Dict:
        """Formatar resposta padrão da API"""
        return {
            "status": status,
            "message": message,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    def handle_error(error: Exception, message: str = "Erro interno") -> Dict:
        """Tratar erros da API"""
        return {
            "status": 500,
            "message": message,
            "error": str(error),
            "timestamp": datetime.now().isoformat()
        }

@app.route('/', methods=['GET'])
def home():
    """Endpoint raiz com informações da API"""
    return jsonify(VagasAPI.format_response({
        "api_name": "API de Vagas Supabase",
        "version": "2.0",
        "description": "API REST para consultar vagas estruturadas do Supabase",
        "endpoints": {
            "/": "Informações da API",
            "/vagas": "Lista todas as vagas (com paginação)",
            "/vagas/count": "Número total de vagas",
            "/vagas/search": "Buscar vagas por filtros",
            "/vagas/{id}": "Obter vaga específica por ID",
            "/vagas/stats": "Estatísticas das vagas",
            "/setores": "Lista todos os setores",
            "/sectors": "Lista todos os setores (English)",
            "/empresas": "Lista todas as empresas",
            "/skills": "Lista básica de skills",
            "/skills/statistics": "Estatísticas agregadas de skills",
            "/skills/top": "Top skills mais demandadas",
            "/skills/search": "Buscar skills por nome",
            "/sectors/analysis": "Análise completa de setores",
            "/sectors/mapping": "Mapeamento de setores",
            "/sectors/coverage": "Cobertura de vagas por setor",
            "/admin/recalculate-stats": "Recalcular estatísticas (POST)",
            "/health": "Status da API"
        },
        "database": "Supabase PostgreSQL",
        "cors_enabled": True
    }))

@app.route('/vagas', methods=['GET'])
def get_all_jobs():
    """Retorna todas as vagas com paginação e filtros"""
    try:
        # Parâmetros de paginação
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)  # Máximo 100
        
        # Parâmetros de filtro
        setor = request.args.get('setor')
        modalidade = request.args.get('modalidade')
        senioridade = request.args.get('senioridade')
        cidade = request.args.get('cidade')
        
        # Construir query usando a view completa
        query = supabase.table('jobs_complete_view').select('*')
        
        # Aplicar filtros
        if setor:
            query = query.eq('industry', setor)
        if modalidade:
            query = query.eq('modality', modalidade)
        if senioridade:
            query = query.eq('seniority', senioridade)
        if cidade:
            query = query.eq('location_city', cidade)
        
        # Aplicar paginação
        start = (page - 1) * per_page
        end = start + per_page - 1
        
        # Executar query com ordenação por data de criação
        result = query.order('created_at', desc=True).range(start, end).execute()
        
        # Contar total de registros
        count_query = supabase.table('jobs_complete_view').select('id', count='exact')
        if setor:
            count_query = count_query.eq('industry', setor)
        if modalidade:
            count_query = count_query.eq('modality', modalidade)
        if senioridade:
            count_query = count_query.eq('seniority', senioridade)
        if cidade:
            count_query = count_query.eq('location_city', cidade)
        
        count_result = count_query.execute()
        total_count = count_result.count
        
        return jsonify(VagasAPI.format_response({
            "vagas": result.data,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total_count,
                "total_pages": (total_count + per_page - 1) // per_page,
                "has_next": end < total_count - 1,
                "has_prev": page > 1
            },
            "filters_applied": {
                "setor": setor,
                "modalidade": modalidade,
                "senioridade": senioridade,
                "cidade": cidade
            }
        }))
        
    except Exception as e:
        return jsonify(VagasAPI.handle_error(e, "Erro ao buscar vagas")), 500

@app.route('/vagas/count', methods=['GET'])
def get_jobs_count():
    """Retorna número total de vagas"""
    try:
        result = supabase.table('jobs_complete_view').select('id', count='exact').execute()
        
        return jsonify(VagasAPI.format_response({
            "total_vagas": result.count,
            "ultima_atualizacao": datetime.now().isoformat()
        }))
        
    except Exception as e:
        return jsonify(VagasAPI.handle_error(e, "Erro ao contar vagas")), 500

@app.route('/vagas/search', methods=['GET'])
def search_jobs():
    """Buscar vagas por termo"""
    try:
        termo = request.args.get('q', '').strip()
        if not termo:
            return jsonify(VagasAPI.format_response(
                [], "Termo de busca é obrigatório", 400
            )), 400
        
        # Parâmetros de paginação
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        
        # Buscar em título, empresa e área
        start = (page - 1) * per_page
        end = start + per_page - 1
        
        result = supabase.table('jobs_complete_view').select('*').or_(
            f'title.ilike.%{termo}%,company_name.ilike.%{termo}%,area.ilike.%{termo}%'
        ).order('created_at', desc=True).range(start, end).execute()
        
        return jsonify(VagasAPI.format_response({
            "vagas": result.data,
            "termo_busca": termo,
            "total_encontradas": len(result.data),
            "pagination": {
                "page": page,
                "per_page": per_page
            }
        }))
        
    except Exception as e:
        return jsonify(VagasAPI.handle_error(e, "Erro na busca")), 500

@app.route('/vagas/<int:job_id>', methods=['GET'])
def get_job_by_id(job_id: int):
    """Obter vaga específica por ID com dados completos"""
    try:
        result = supabase.table('jobs_complete_view').select('*').eq('id', job_id).execute()
        
        if not result.data:
            return jsonify(VagasAPI.format_response(
                None, f"Vaga com ID {job_id} não encontrada", 404
            )), 404
        
        vaga = result.data[0]
        
        return jsonify(VagasAPI.format_response(vaga))
        
    except Exception as e:
        return jsonify(VagasAPI.handle_error(e, "Erro ao buscar vaga")), 500

@app.route('/vagas/stats', methods=['GET'])
def get_jobs_stats():
    """Estatísticas das vagas"""
    try:
        # Total de vagas
        total_result = supabase.table('jobs_complete_view').select('id', count='exact').execute()
        
        # Vagas por setor
        setores_result = supabase.rpc('get_jobs_by_industry').execute()
        
        # Vagas por modalidade
        modalidade_result = supabase.rpc('get_jobs_by_modality').execute()
        
        # Vagas por senioridade
        senioridade_result = supabase.rpc('get_jobs_by_seniority').execute()
        
        return jsonify(VagasAPI.format_response({
            "total_vagas": total_result.count,
            "por_setor": setores_result.data if setores_result.data else [],
            "por_modalidade": modalidade_result.data if modalidade_result.data else [],
            "por_senioridade": senioridade_result.data if senioridade_result.data else [],
            "ultima_atualizacao": datetime.now().isoformat()
        }))
        
    except Exception as e:
        # Se as funções RPC não existirem, fazer queries simples
        try:
            # Fallback para queries simples
            setores = supabase.table('jobs_complete_view').select('industry').execute()
            modalidades = supabase.table('jobs_complete_view').select('modality').execute()
            senioridades = supabase.table('jobs_complete_view').select('seniority').execute()
            
            # Contar manualmente
            setores_count = {}
            for job in setores.data:
                setor = job.get('industry', 'N/A')
                setores_count[setor] = setores_count.get(setor, 0) + 1
            
            modalidades_count = {}
            for job in modalidades.data:
                modalidade = job.get('modality', 'N/A')
                modalidades_count[modalidade] = modalidades_count.get(modalidade, 0) + 1
            
            senioridades_count = {}
            for job in senioridades.data:
                senioridade = job.get('seniority', 'N/A')
                senioridades_count[senioridade] = senioridades_count.get(senioridade, 0) + 1
            
            return jsonify(VagasAPI.format_response({
                "total_vagas": len(setores.data),
                "por_setor": [{'industry': k, 'count': v} for k, v in setores_count.items()],
                "por_modalidade": [{'modality': k, 'count': v} for k, v in modalidades_count.items()],
                "por_senioridade": [{'seniority': k, 'count': v} for k, v in senioridades_count.items()],
                "ultima_atualizacao": datetime.now().isoformat()
            }))
            
        except Exception as fallback_error:
            return jsonify(VagasAPI.handle_error(fallback_error, "Erro ao gerar estatísticas")), 500

@app.route('/setores', methods=['GET'])
def get_sectors():
    """Lista todos os setores únicos"""
    try:
        result = supabase.table('jobs').select('industry').execute()
        setores = list(set([job['industry'] for job in result.data if job.get('industry')]))
        setores.sort()
        
        return jsonify(VagasAPI.format_response({
            "setores": setores,
            "total": len(setores)
        }))
        
    except Exception as e:
        return jsonify(VagasAPI.handle_error(e, "Erro ao buscar setores")), 500

@app.route('/sectors', methods=['GET'])
def get_sectors_en():
    """Lista todos os setores únicos (English alias)"""
    try:
        result = supabase.table('jobs').select('industry').execute()
        sectors = list(set([job['industry'] for job in result.data if job.get('industry')]))
        sectors.sort()
        
        return jsonify(VagasAPI.format_response({
            "sectors": sectors,
            "total": len(sectors)
        }))
        
    except Exception as e:
        return jsonify(VagasAPI.handle_error(e, "Erro ao buscar setores")), 500

@app.route('/skills', methods=['GET'])
def get_skills():
    """Lista todas as skills básicas"""
    try:
        # Buscar skills da tabela skills_complete_stats
        limit = min(request.args.get('limit', 100, type=int), 500)
        result = supabase.table('skills_statistics').select('skill_name, total_jobs').order('total_jobs', desc=True).limit(limit).execute()
        
        skills = [{
            "name": skill['skill_name'],
            "total_jobs": skill.get('total_jobs', 0)
        } for skill in result.data]
        
        return jsonify(VagasAPI.format_response({
            "skills": skills,
            "total": len(skills),
            "limit": limit
        }))
        
    except Exception as e:
        return jsonify(VagasAPI.handle_error(e, "Erro ao buscar skills")), 500

@app.route('/empresas', methods=['GET'])
def get_companies():
    """Lista todas as empresas únicas"""
    try:
        result = supabase.table('jobs').select('company_name').execute()
        empresas = list(set([job['company_name'] for job in result.data if job.get('company_name')]))
        empresas.sort()
        
        return jsonify(VagasAPI.format_response({
            "empresas": empresas,
            "total": len(empresas)
        }))
        
    except Exception as e:
        return jsonify(VagasAPI.handle_error(e, "Erro ao buscar empresas")), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Verificação de saúde da API"""
    try:
        # Testar conexão com Supabase
        result = supabase.table('jobs').select('id').limit(1).execute()
        
        return jsonify(VagasAPI.format_response({
            "status": "healthy",
            "database": "connected",
            "supabase_url": SUPABASE_URL,
            "timestamp": datetime.now().isoformat()
        }))
        
    except Exception as e:
        return jsonify(VagasAPI.handle_error(e, "API não está saudável")), 500

# ===== NOVOS ENDPOINTS PARA SKILLS E SETORES =====

@app.route('/skills/statistics', methods=['GET'])
def get_skills_statistics():
    """Obter estatísticas agregadas de skills"""
    try:
        limit = min(request.args.get('limit', 50, type=int), 100)
        category = request.args.get('category')
        skill_type = request.args.get('skill_type')
        
        query = supabase.table('skills_statistics').select('*')
        
        if category:
            query = query.eq('category', category)
        if skill_type:
            query = query.eq('skill_type', skill_type)
            
        result = query.order('id', desc=True).limit(limit).execute()
        
        return jsonify(VagasAPI.format_response({
            "total_skills": len(result.data),
            "skills": result.data,
            "filters": {
                "category": category,
                "skill_type": skill_type,
                "limit": limit
            }
        }))
        
    except Exception as e:
        return jsonify(VagasAPI.handle_error(e, "Erro ao buscar estatísticas de skills")), 500

@app.route('/skills/top', methods=['GET'])
def get_top_skills():
    """Obter as skills mais demandadas"""
    try:
        limit = min(request.args.get('limit', 20, type=int), 100)
        order_by = request.args.get('by', 'total_jobs')
        
        valid_order_by = ['total_jobs', 'percentage', 'avg_salary_max']
        if order_by not in valid_order_by:
            order_by = 'total_jobs'
            
        result = supabase.table('skills_statistics').select('*').order(order_by, desc=True).limit(limit).execute()
        
        return jsonify(VagasAPI.format_response({
            "ordered_by": order_by,
            "top_skills": result.data
        }))
        
    except Exception as e:
        return jsonify(VagasAPI.handle_error(e, "Erro ao buscar top skills")), 500

@app.route('/skills/search', methods=['GET'])
def search_skills():
    """Buscar skills por nome ou sinônimos"""
    try:
        query_term = request.args.get('q', '').strip()
        if not query_term:
            return jsonify(VagasAPI.format_response(
                [], "Termo de busca é obrigatório", 400
            )), 400
            
        limit = min(request.args.get('limit', 20, type=int), 100)
        
        # Buscar por nome da skill
        result = supabase.table('skills_statistics').select('*').ilike('skill_name', f'%{query_term}%').limit(limit).execute()
        
        return jsonify(VagasAPI.format_response({
            "query": query_term,
            "results": result.data,
            "total_found": len(result.data)
        }))
        
    except Exception as e:
        return jsonify(VagasAPI.handle_error(e, "Erro ao buscar skills")), 500

@app.route('/sectors/analysis', methods=['GET'])
def get_sectors_analysis():
    """Obter análise completa de setores"""
    try:
        limit = min(request.args.get('limit', 50, type=int), 100)
        category = request.args.get('category')
        
        query = supabase.table('sector_mapping').select('*')
        
        if category:
            query = query.eq('sector_category', category)
            
        result = query.order('id', desc=True).limit(limit).execute()
        
        return jsonify(VagasAPI.format_response({
            "total_sectors": len(result.data),
            "sectors": result.data,
            "filters": {
                "category": category,
                "limit": limit
            }
        }))
        
    except Exception as e:
        return jsonify(VagasAPI.handle_error(e, "Erro ao buscar análise de setores")), 500

@app.route('/sectors/mapping', methods=['GET'])
def get_sector_mapping():
    """Obter mapeamento de setores"""
    try:
        original_sector = request.args.get('original_sector')
        normalized_sector = request.args.get('normalized_sector')
        
        query = supabase.table('sector_mapping').select('*')
        
        if original_sector:
            query = query.ilike('sector_original', f'%{original_sector}%')
        elif normalized_sector:
            query = query.ilike('sector_normalized', f'%{normalized_sector}%')
            
        result = query.execute()
        
        return jsonify(VagasAPI.format_response({
            "mappings": result.data,
            "total_mappings": len(result.data),
            "filters": {
                "original_sector": original_sector,
                "normalized_sector": normalized_sector
            }
        }))
        
    except Exception as e:
        return jsonify(VagasAPI.handle_error(e, "Erro ao buscar mapeamento de setores")), 500

@app.route('/sectors/coverage', methods=['GET'])
def get_sector_coverage():
    """Obter cobertura de vagas por setor"""
    try:
        limit = min(request.args.get('limit', 20, type=int), 100)
        
        result = supabase.table('sector_coverage').select('*').order('total_jobs', desc=True).limit(limit).execute()
        
        return jsonify(VagasAPI.format_response({
            "sector_coverage": result.data,
            "total_sectors": len(result.data)
        }))
        
    except Exception as e:
        return jsonify(VagasAPI.handle_error(e, "Erro ao buscar cobertura de setores")), 500

@app.route('/admin/recalculate-stats', methods=['POST'])
def recalculate_statistics():
    """Recalcular estatísticas de skills e setores (endpoint administrativo)"""
    try:
        # Executar função de recálculo de skills
        skills_result = supabase.rpc('recalculate_skills_stats').execute()
        
        # Executar função de recálculo de setores
        sectors_result = supabase.rpc('recalculate_sector_coverage').execute()
        
        return jsonify(VagasAPI.format_response({
            "message": "Estatísticas recalculadas com sucesso",
            "skills_updated": True,
            "sectors_updated": True,
            "timestamp": datetime.now().isoformat()
        }))
        
    except Exception as e:
        return jsonify(VagasAPI.handle_error(e, "Erro ao recalcular estatísticas")), 500

@app.errorhandler(404)
def not_found(error):
    """Handler para rotas não encontradas"""
    return jsonify(VagasAPI.format_response(
        None, "Endpoint não encontrado", 404
    )), 404

@app.errorhandler(500)
def internal_error(error):
    """Handler para erros internos"""
    return jsonify(VagasAPI.format_response(
        None, "Erro interno do servidor", 500
    )), 500

if __name__ == '__main__':
    print("Iniciando API de Vagas Supabase...")
    print("Endpoints disponiveis:")
    print("   GET / - Informacoes da API")
    print("   GET /vagas - Lista vagas (paginacao)")
    print("   GET /vagas/count - Total de vagas")
    print("   GET /vagas/search?q=termo - Buscar vagas")
    print("   GET /vagas/{id} - Vaga específica")
    print("   GET /vagas/stats - Estatísticas")
    print("   GET /setores - Lista setores")
    print("   GET /sectors - Lista setores (English)")
    print("   GET /empresas - Lista empresas")
    print("   GET /skills - Lista básica de skills")
    print("   GET /skills/statistics - Estatísticas de skills")
    print("   GET /skills/top - Top skills")
    print("   GET /skills/search?q=termo - Buscar skills")
    print("   GET /sectors/analysis - Análise de setores")
    print("   GET /sectors/mapping - Mapeamento de setores")
    print("   GET /sectors/coverage - Cobertura por setor")
    print("   POST /admin/recalculate-stats - Recalcular estatísticas")
    print("   GET /health - Status da API")
    print("\nAcesse: http://localhost:5000")
    print("Conectado ao Supabase:", SUPABASE_URL)
    
    app.run(debug=True, host='0.0.0.0', port=5000)