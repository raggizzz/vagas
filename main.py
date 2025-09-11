#!/usr/bin/env python3
"""
API para consultar vagas por skills e setores no Supabase
Utiliza os dados carregados nas tabelas jobs, companies e job_requirements_must
"""

import os
from typing import List, Dict, Optional, Any
from supabase import create_client, Client
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import re
from collections import Counter

# Configuração do Supabase
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY') or os.getenv('SUPABASE_ANON_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Variáveis de ambiente SUPABASE_URL e SUPABASE_KEY (ou SUPABASE_ANON_KEY) são obrigatórias")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Configuração da API
app = FastAPI(
    title="API de Vagas e Skills",
    description="API para consultar vagas de emprego por skills e setores",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos Pydantic
class JobResponse(BaseModel):
    id: int
    title: str
    company: Optional[str] = None
    sector: Optional[str] = None
    location: Optional[str] = None
    salary_range: Optional[str] = None
    skills: List[str] = []
    requirements: List[str] = []
    description: Optional[str] = None
    url: Optional[str] = None
    posted_date: Optional[str] = None

class SkillsByJobResponse(BaseModel):
    skill: str
    jobs: List[JobResponse]
    total_jobs: int

class SkillsBySectorResponse(BaseModel):
    sector: str
    skills: List[Dict[str, Any]]
    total_jobs: int
    analysis_date: str

class CommonSkill(BaseModel):
    skill: str
    frequency: int
    percentage: float
    job_ids: List[int]

class CommonSkillsResponse(BaseModel):
    total_jobs_analyzed: int
    common_skills: List[CommonSkill]
    analysis_date: str

class MostWantedJobResponse(BaseModel):
    title: str
    count: int
    percentage: float
    sample_jobs: List[JobResponse]

class MostWantedJobsResponse(BaseModel):
    total_jobs_analyzed: int
    most_wanted_jobs: List[MostWantedJobResponse]
    analysis_date: str

# Funções auxiliares
def extract_skills_from_text(text: str) -> List[str]:
    """Extrai skills de um texto usando padrões comuns"""
    if not text:
        return []
    
    # Lista de skills comuns para buscar
    common_skills = [
        'Python', 'Java', 'JavaScript', 'C++', 'C#', 'PHP', 'Ruby', 'Go', 'Rust', 'Swift',
        'React', 'Angular', 'Vue', 'Node.js', 'Django', 'Flask', 'Spring', 'Laravel',
        'HTML', 'CSS', 'SQL', 'MongoDB', 'PostgreSQL', 'MySQL', 'Redis', 'Docker',
        'Kubernetes', 'AWS', 'Azure', 'GCP', 'Git', 'Linux', 'Windows', 'MacOS',
        'Scrum', 'Agile', 'DevOps', 'CI/CD', 'Jenkins', 'Terraform', 'Ansible',
        'Machine Learning', 'AI', 'Data Science', 'Big Data', 'Hadoop', 'Spark',
        'Excel', 'Power BI', 'Tableau', 'Photoshop', 'Illustrator', 'Figma',
        'Inglês', 'Espanhol', 'Francês', 'Alemão', 'Comunicação', 'Liderança',
        'Trabalho em Equipe', 'Gestão de Projetos', 'Análise', 'Criatividade',
        'Organização', 'Proatividade', 'Resolução de Problemas'
    ]
    
    found_skills = []
    text_upper = text.upper()
    
    for skill in common_skills:
        if skill.upper() in text_upper:
            found_skills.append(skill)
    
    return found_skills

def analyze_common_skills(jobs_data: List[Dict], min_frequency: int = 1) -> Dict:
    """Analisa skills comuns entre as vagas"""
    all_skills = []
    job_skills_map = {}
    
    for job in jobs_data:
        job_id = job['id']
        job_skills = []
        
        # Extrair skills do título
        if job.get('titulo'):
            job_skills.extend(extract_skills_from_text(job['titulo']))
        
        # Extrair skills dos requisitos
        if job.get('requisitos'):
            job_skills.extend(extract_skills_from_text(job['requisitos']))
        
        # Extrair skills do campo habilidades (se existir e não for None)
        if job.get('habilidades'):
            job_skills.extend(extract_skills_from_text(str(job['habilidades'])))
        
        # Remover duplicatas para este job
        job_skills = list(set(job_skills))
        job_skills_map[job_id] = job_skills
        all_skills.extend(job_skills)
    
    # Contar frequência das skills
    skill_counter = Counter(all_skills)
    
    # Filtrar por frequência mínima
    filtered_skills = {skill: count for skill, count in skill_counter.items() if count >= min_frequency}
    
    # Criar lista de skills comuns com detalhes
    common_skills = []
    total_jobs = len(jobs_data)
    
    for skill, frequency in sorted(filtered_skills.items(), key=lambda x: x[1], reverse=True):
        # Encontrar IDs dos jobs que têm essa skill
        job_ids = [job_id for job_id, skills in job_skills_map.items() if skill in skills]
        
        percentage = (frequency / total_jobs) * 100
        
        common_skills.append({
            'skill': skill,
            'frequency': frequency,
            'percentage': round(percentage, 2),
            'job_ids': job_ids
        })
    
    return {
        'total_jobs_analyzed': total_jobs,
        'common_skills': common_skills,
        'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

# Endpoints
@app.get("/", summary="Informações da API")
async def root():
    return {
        "message": "API de Vagas e Skills",
        "version": "1.0.0",
        "endpoints": [
            "/jobs",
            "/skills-by-sector",
            "/common-skills",
            "/most-wanted-jobs"
        ]
    }

@app.get("/jobs", summary="Todas as vagas da tabela jobs")
async def get_all_jobs(limit: int = Query(100, ge=1, le=1000), offset: int = Query(0, ge=0)):
    """Retorna todas as vagas exatamente como estão na tabela jobs"""
    try:
        # Buscar todos os dados da tabela jobs sem modificações
        response = supabase.table('jobs').select('*').range(offset, offset + limit - 1).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Nenhuma vaga encontrada")
        
        # Contar total de registros
        count_response = supabase.table('jobs').select('*', count='exact').execute()
        total_count = count_response.count if hasattr(count_response, 'count') else len(response.data)
        
        return {
            "total_jobs": total_count,
            "limit": limit,
            "offset": offset,
            "jobs": response.data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@app.get("/skills-by-sector", response_model=List[SkillsBySectorResponse], summary="Skills por setor")
async def get_skills_by_sector(limit: int = Query(10, ge=1, le=100)):
    try:
        # Buscar dados das vagas
        response = supabase.table('jobs').select('id, titulo, setor, habilidades, requisitos').limit(1000).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Nenhuma vaga encontrada")
        
        # Agrupar por setor e analisar skills
        sectors_data = {}
        
        for job in response.data:
            sector = job.get('setor', 'Não especificado')
            if sector not in sectors_data:
                sectors_data[sector] = []
            sectors_data[sector].append(job)
        
        result = []
        for sector, jobs in list(sectors_data.items())[:limit]:
            skills_analysis = analyze_common_skills(jobs, min_frequency=1)
            
            result.append({
                'sector': sector,
                'skills': skills_analysis['common_skills'][:10],  # Top 10 skills por setor
                'total_jobs': len(jobs),
                'analysis_date': skills_analysis['analysis_date']
            })
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@app.get("/common-skills", response_model=CommonSkillsResponse, summary="Skills mais comuns")
async def get_common_skills(min_frequency: int = Query(1, ge=1, description="Frequência mínima da skill")):
    try:
        # Buscar dados das vagas
        response = supabase.table('jobs').select('id, titulo, setor, habilidades, requisitos').execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Nenhuma vaga encontrada")
        
        # Analisar skills comuns
        analysis = analyze_common_skills(response.data, min_frequency)
        
        return analysis
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@app.get("/most-wanted-jobs", response_model=MostWantedJobsResponse, summary="Vagas mais procuradas")
async def get_most_wanted_jobs(limit: int = Query(10, ge=1, le=50)):
    try:
        # Buscar dados das vagas
        response = supabase.table('jobs').select('*').execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Nenhuma vaga encontrada")
        
        # Contar títulos de vagas (normalizados)
        job_titles = {}
        jobs_by_title = {}
        
        for job in response.data:
            title = job.get('titulo', '').strip()
            if title:
                # Normalizar título (remover caracteres especiais, converter para minúsculas)
                normalized_title = re.sub(r'[^a-zA-Z0-9\s]', '', title).lower().strip()
                
                if normalized_title not in job_titles:
                    job_titles[normalized_title] = 0
                    jobs_by_title[normalized_title] = []
                
                job_titles[normalized_title] += 1
                jobs_by_title[normalized_title].append({
                    'id': job['id'],
                    'title': title,
                    'company': job.get('empresa'),
                    'sector': job.get('setor'),
                    'location': job.get('localizacao'),
                    'salary_range': job.get('salario'),
                    'skills': extract_skills_from_text(f"{job.get('titulo', '')} {job.get('requisitos', '')}"),
                    'requirements': [job.get('requisitos', '')] if job.get('requisitos') else [],
                    'description': job.get('descricao'),
                    'url': job.get('url'),
                    'posted_date': job.get('data_publicacao')
                })
        
        # Ordenar por frequência e pegar os mais comuns
        sorted_titles = sorted(job_titles.items(), key=lambda x: x[1], reverse=True)[:limit]
        
        total_jobs = len(response.data)
        most_wanted = []
        
        for normalized_title, count in sorted_titles:
            percentage = (count / total_jobs) * 100
            sample_jobs = jobs_by_title[normalized_title][:3]  # Máximo 3 exemplos
            
            # Usar o título original do primeiro job como representativo
            original_title = sample_jobs[0]['title'] if sample_jobs else normalized_title
            
            most_wanted.append({
                'title': original_title,
                'count': count,
                'percentage': round(percentage, 2),
                'sample_jobs': sample_jobs
            })
        
        return {
            'total_jobs_analyzed': total_jobs,
            'most_wanted_jobs': most_wanted,
            'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

# Para o Vercel
handler = app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)