from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Permitir requisições de qualquer origem

# Função para carregar dados do arquivo JSON
def load_job_data():
    try:
        with open('catho_job_titles.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"total_titles": 0, "titles": [], "timestamp": ""}

@app.route('/', methods=['GET'])
def home():
    """Endpoint raiz com informações da API"""
    return jsonify({
        "message": "API de Vagas da Catho",
        "version": "1.0",
        "endpoints": {
            "/": "Informações da API",
            "/vagas": "Lista todas as vagas extraídas",
            "/vagas/count": "Número total de vagas",
            "/vagas/search?q=termo": "Buscar vagas por termo",
            "/vagas/{id}": "Obter vaga específica por ID"
        },
        "timestamp": datetime.now().isoformat()
    })

@app.route('/vagas', methods=['GET'])
def get_all_jobs():
    """Retorna todas as vagas extraídas"""
    data = load_job_data()
    
    # Parâmetros de paginação
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Calcular índices para paginação
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    
    titles = data.get('titles', [])
    paginated_titles = titles[start_idx:end_idx]
    
    # Criar lista de vagas com IDs
    jobs = []
    for i, title in enumerate(paginated_titles, start=start_idx + 1):
        jobs.append({
            "id": i,
            "title": title,
            "source": "catho.com.br"
        })
    
    return jsonify({
        "success": True,
        "data": jobs,
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": len(titles),
            "total_pages": (len(titles) + per_page - 1) // per_page
        },
        "extracted_at": data.get('timestamp', '')
    })

@app.route('/vagas/count', methods=['GET'])
def get_jobs_count():
    """Retorna o número total de vagas"""
    data = load_job_data()
    return jsonify({
        "success": True,
        "total_jobs": data.get('total_titles', 0),
        "extracted_at": data.get('timestamp', '')
    })

@app.route('/vagas/search', methods=['GET'])
def search_jobs():
    """Busca vagas por termo"""
    query = request.args.get('q', '').lower()
    
    if not query:
        return jsonify({
            "success": False,
            "error": "Parâmetro 'q' é obrigatório para busca"
        }), 400
    
    data = load_job_data()
    titles = data.get('titles', [])
    
    # Filtrar títulos que contêm o termo de busca
    filtered_jobs = []
    for i, title in enumerate(titles, 1):
        if query in title.lower():
            filtered_jobs.append({
                "id": i,
                "title": title,
                "source": "catho.com.br"
            })
    
    return jsonify({
        "success": True,
        "query": query,
        "results_count": len(filtered_jobs),
        "data": filtered_jobs,
        "extracted_at": data.get('timestamp', '')
    })

@app.route('/vagas/<int:job_id>', methods=['GET'])
def get_job_by_id(job_id):
    """Retorna uma vaga específica por ID"""
    data = load_job_data()
    titles = data.get('titles', [])
    
    if job_id < 1 or job_id > len(titles):
        return jsonify({
            "success": False,
            "error": "Vaga não encontrada"
        }), 404
    
    job = {
        "id": job_id,
        "title": titles[job_id - 1],
        "source": "catho.com.br",
        "extracted_at": data.get('timestamp', '')
    }
    
    return jsonify({
        "success": True,
        "data": job
    })

@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint de verificação de saúde da API"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "data_available": os.path.exists('catho_job_titles.json')
    })

if __name__ == '__main__':
    print("🚀 Iniciando API de Vagas da Catho...")
    print("📋 Endpoints disponíveis:")
    print("   GET /vagas - Lista todas as vagas")
    print("   GET /vagas/count - Número total de vagas")
    print("   GET /vagas/search?q=termo - Buscar vagas")
    print("   GET /vagas/{id} - Vaga específica")
    print("   GET /health - Status da API")
    print("\n🌐 Acesse: http://localhost:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000)