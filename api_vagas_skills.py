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
import uvicorn
from datetime import datetime
from dotenv import load_dotenv
import re
from collections import Counter

# Carregar variáveis de ambiente
load_dotenv()

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
    company_name: Optional[str]
    seniority: Optional[str]
    area: Optional[str]
    employment_type: Optional[str]
    modality: Optional[str]
    location_city: Optional[str]
    location_state: Optional[str]
    salary_min: Optional[float]
    salary_max: Optional[float]
    description: Optional[str]
    skills: List[str] = []

class SkillStats(BaseModel):
    skill: str
    count: int
    percentage: float

class APIStats(BaseModel):
    total_jobs: int
    total_companies: int
    total_skills: int
    top_skills: List[SkillStats]
    jobs_by_state: Dict[str, int]
    jobs_by_modality: Dict[str, int]

class MostWantedJob(BaseModel):
    id: int
    title: str
    company_name: Optional[str]
    seniority: Optional[str]
    area: Optional[str]
    employment_type: Optional[str]
    modality: Optional[str]
    location_city: Optional[str]
    location_state: Optional[str]
    salary_min: Optional[float]
    salary_max: Optional[float]
    description: Optional[str]
    skills: List[str] = []
    application_count: int
    similar_requirements_percentage: float
    similar_jobs: List[Dict[str, Any]] = []

class SkillBySector(BaseModel):
    skill: str
    percentage: float
    job_count: int

class SectorSkills(BaseModel):
    sector: str
    total_jobs: int
    average_salary: Optional[float]
    top_skills: List[SkillBySector]

class SkillsBySectorResponse(BaseModel):
    sectors: List[SectorSkills]
    total_jobs_analyzed: int
    last_updated: str

@app.get("/", summary="Informações da API")
async def root():
    """Endpoint raiz com informações da API"""
    return {
        "message": "API de Vagas e Skills",
        "version": "1.0.0",
        "endpoints": [
            "/jobs",
            "/skills-by-sector"
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

@app.get("/jobs-filtered", response_model=List[JobResponse])
async def get_jobs_filtered(
    skills: Optional[str] = Query(None, description="Skills separadas por vírgula"),
    location_state: Optional[str] = Query(None, description="Estado (UF)"),
    location_city: Optional[str] = Query(None, description="Cidade"),
    modality: Optional[str] = Query(None, description="Modalidade (Presencial, Remoto, Híbrido)"),
    seniority: Optional[str] = Query(None, description="Senioridade"),
    employment_type: Optional[str] = Query(None, description="Tipo de contrato"),
    limit: int = Query(50, le=200, description="Limite de resultados")
):
    """Buscar vagas com filtros opcionais"""
    try:
        # Query base
        query = supabase.table('jobs').select('*')
        
        # Aplicar filtros
        if location_state:
            query = query.eq('location_state', location_state.upper())
        if location_city:
            query = query.ilike('location_city', f'%{location_city}%')
        if modality:
            query = query.ilike('modality', f'%{modality}%')
        if seniority:
            query = query.ilike('seniority', f'%{seniority}%')
        if employment_type:
            query = query.ilike('employment_type', f'%{employment_type}%')
        
        # Executar query
        response = query.limit(limit).execute()
        jobs = response.data
        
        # Se filtro por skills, buscar jobs que tenham essas skills
        if skills:
            skill_list = [s.strip() for s in skills.split(',')]
            job_ids = []
            
            for skill in skill_list:
                skill_response = supabase.table('job_requirements_must').select('job_id').ilike('requirement', f'%{skill}%').execute()
                job_ids.extend([r['job_id'] for r in skill_response.data])
            
            # Filtrar jobs pelos IDs encontrados
            if job_ids:
                jobs = [job for job in jobs if job['id'] in job_ids]
        
        # Buscar skills para cada vaga
        result = []
        for job in jobs:
            skills_response = supabase.table('job_requirements_must').select('requirement').eq('job_id', job['id']).execute()
            job_skills = [s['requirement'] for s in skills_response.data]
            
            result.append(JobResponse(
                id=job['id'],
                title=job['title'],
                company_name=job.get('company_name'),
                seniority=job.get('seniority'),
                area=job.get('area'),
                employment_type=job.get('employment_type'),
                modality=job.get('modality'),
                location_city=job.get('location_city'),
                location_state=job.get('location_state'),
                salary_min=job.get('salary_min'),
                salary_max=job.get('salary_max'),
                description=job.get('description'),
                skills=job_skills
            ))
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar vagas: {str(e)}")

@app.get("/jobs/{job_id}", response_model=JobResponse)
async def get_job_details(job_id: int):
    """Obter detalhes de uma vaga específica"""
    try:
        # Buscar vaga
        job_response = supabase.table('jobs').select('*').eq('id', job_id).execute()
        
        if not job_response.data:
            raise HTTPException(status_code=404, detail="Vaga não encontrada")
        
        job = job_response.data[0]
        
        # Buscar skills da vaga
        skills_response = supabase.table('job_requirements_must').select('requirement').eq('job_id', job_id).execute()
        job_skills = [s['requirement'] for s in skills_response.data]
        
        return JobResponse(
            id=job['id'],
            title=job['title'],
            company_name=job.get('company_name'),
            seniority=job.get('seniority'),
            area=job.get('area'),
            employment_type=job.get('employment_type'),
            modality=job.get('modality'),
            location_city=job.get('location_city'),
            location_state=job.get('location_state'),
            salary_min=job.get('salary_min'),
            salary_max=job.get('salary_max'),
            description=job.get('description'),
            skills=job_skills
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar vaga: {str(e)}")

@app.get("/skills", response_model=List[SkillStats])
async def get_top_skills(limit: int = Query(20, le=100, description="Limite de skills")):
    """Obter skills mais demandadas"""
    try:
        # Contar ocorrências de cada skill
        response = supabase.rpc('get_skill_stats', {'limit_count': limit}).execute()
        
        if response.data:
            return response.data
        
        # Fallback: contar manualmente
        skills_response = supabase.table('job_requirements_must').select('requirement').execute()
        skills_count = {}
        total_skills = len(skills_response.data)
        
        for skill_record in skills_response.data:
            skill = skill_record['requirement']
            skills_count[skill] = skills_count.get(skill, 0) + 1
        
        # Ordenar por contagem
        sorted_skills = sorted(skills_count.items(), key=lambda x: x[1], reverse=True)[:limit]
        
        return [
            SkillStats(
                skill=skill,
                count=count,
                percentage=round((count / total_skills) * 100, 2)
            )
            for skill, count in sorted_skills
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar skills: {str(e)}")

@app.get("/stats", response_model=APIStats)
async def get_stats():
    """Obter estatísticas gerais da base de dados"""
    try:
        # Contar totais
        jobs_response = supabase.table('jobs').select('id', count='exact').execute()
        companies_response = supabase.table('companies').select('id', count='exact').execute()
        skills_response = supabase.table('job_requirements_must').select('requirement').execute()
        
        total_jobs = jobs_response.count or 0
        total_companies = companies_response.count or 0
        total_skills = len(set(s['requirement'] for s in skills_response.data))
        
        # Top skills
        top_skills_data = await get_top_skills(10)
        
        # Jobs por estado
        jobs_by_state_response = supabase.table('jobs').select('location_state').execute()
        jobs_by_state = {}
        for job in jobs_by_state_response.data:
            state = job.get('location_state', 'N/A')
            jobs_by_state[state] = jobs_by_state.get(state, 0) + 1
        
        # Jobs por modalidade
        jobs_by_modality_response = supabase.table('jobs').select('modality').execute()
        jobs_by_modality = {}
        for job in jobs_by_modality_response.data:
            modality = job.get('modality', 'N/A')
            jobs_by_modality[modality] = jobs_by_modality.get(modality, 0) + 1
        
        return APIStats(
            total_jobs=total_jobs,
            total_companies=total_companies,
            total_skills=total_skills,
            top_skills=top_skills_data,
            jobs_by_state=jobs_by_state,
            jobs_by_modality=jobs_by_modality
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar estatísticas: {str(e)}")

@app.get("/search", response_model=List[JobResponse])
async def search_jobs(
    q: str = Query(..., description="Termo de busca"),
    limit: int = Query(50, le=200, description="Limite de resultados")
):
    """Buscar vagas por texto livre"""
    try:
        # Buscar em título e descrição
        response = supabase.table('jobs').select('*').or_(
            f'title.ilike.%{q}%,description.ilike.%{q}%,area.ilike.%{q}%'
        ).limit(limit).execute()
        
        jobs = response.data
        
        # Buscar skills para cada vaga
        result = []
        for job in jobs:
            skills_response = supabase.table('job_requirements_must').select('requirement').eq('job_id', job['id']).execute()
            job_skills = [s['requirement'] for s in skills_response.data]
            
            result.append(JobResponse(
                id=job['id'],
                title=job['title'],
                company_name=job.get('company_name'),
                seniority=job.get('seniority'),
                area=job.get('area'),
                employment_type=job.get('employment_type'),
                modality=job.get('modality'),
                location_city=job.get('location_city'),
                location_state=job.get('location_state'),
                salary_min=job.get('salary_min'),
                salary_max=job.get('salary_max'),
                description=job.get('description'),
                skills=job_skills
            ))
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na busca: {str(e)}")



@app.get("/skills-by-sector", response_model=SkillsBySectorResponse)
async def get_skills_by_sector():
    """Obter habilidades mais requisitadas organizadas por setor baseado nos dados reais dos jobs"""
    try:
        from datetime import datetime
        import re
        
        # Buscar todas as vagas
        jobs_response = supabase.table('jobs').select('*').execute()
        jobs = jobs_response.data
        
        if not jobs:
            return SkillsBySectorResponse(
                sectors=[],
                total_jobs_analyzed=0,
                last_updated=datetime.now().isoformat()
            )
        
        # Função para extrair skills reais das descrições
        def extract_real_skills(job):
            skills_found = set()
            
            # Combinar todos os campos de texto relevantes
            text_fields = [
                str(job.get('descricao', '')),
                str(job.get('titulo', '')),
                str(job.get('requisitos', '')),
                str(job.get('habilidades', ''))
            ]
            
            full_text = ' '.join(text_fields).lower()
            
            # Padrões de skills técnicas mais comuns
            skill_patterns = {
                # Linguagens de Programação
                'Python': r'\bpython\b',
                'Java': r'\bjava\b(?!script)',
                'JavaScript': r'\b(javascript|js)\b',
                'PHP': r'\bphp\b',
                'C#': r'\bc#\b',
                'C++': r'\bc\+\+\b',
                'React': r'\breact(js)?\b',
                'Vue.js': r'\bvue(\.js)?\b',
                'Angular': r'\bangular\b',
                'Node.js': r'\bnode(\.js)?\b',
                
                # Bancos de Dados
                'SQL': r'\bsql\b',
                'MySQL': r'\bmysql\b',
                'PostgreSQL': r'\b(postgresql|postgres)\b',
                'MongoDB': r'\bmongodb\b',
                'Oracle': r'\boracle\b',
                
                # Ferramentas e Tecnologias
                'Git': r'\bgit\b',
                'Docker': r'\bdocker\b',
                'Kubernetes': r'\bkubernetes\b',
                'AWS': r'\baws\b',
                'Azure': r'\bazure\b',
                'Linux': r'\blinux\b',
                'Excel': r'\bexcel\b',
                'Power BI': r'\bpower\s*bi\b',
                'Tableau': r'\btableau\b',
                
                # Metodologias
                'Scrum': r'\bscrum\b',
                'Agile': r'\b(agile|ágil)\b',
                'DevOps': r'\bdevops\b',
                
                # Soft Skills
                'Comunicação': r'\bcomunica(ção|cao)\b',
                'Liderança': r'\blideran(ça|ca)\b',
                'Trabalho em Equipe': r'\btrabalho\s+em\s+equipe\b',
                'Organização': r'\borganiza(ção|cao)\b',
                'Inglês': r'\b(inglês|ingles|english)\b',
                'Espanhol': r'\bespanhol\b',
                
                # Outras Skills Técnicas
                'HTML': r'\bhtml\b',
                'CSS': r'\bcss\b',
                'API': r'\bapi\b',
                'REST': r'\brest\b',
                'JSON': r'\bjson\b',
                'XML': r'\bxml\b'
            }
            
            # Buscar por padrões de skills
            for skill_name, pattern in skill_patterns.items():
                if re.search(pattern, full_text, re.IGNORECASE):
                    skills_found.add(skill_name)
            
            # Extrair skills adicionais de listas (separadas por vírgula, ponto e vírgula, etc.)
            skill_indicators = ['conhecimento', 'experiência', 'domínio', 'habilidade', 'requisito']
            for indicator in skill_indicators:
                pattern = rf'{indicator}[^.]*?([A-Za-z][A-Za-z0-9\s\+#\.]*?)(?:[,;\n]|\.|$)'
                matches = re.findall(pattern, full_text, re.IGNORECASE)
                for match in matches:
                    skill = match.strip()
                    if len(skill) > 2 and len(skill) < 30:  # Filtrar skills muito curtas ou longas
                        skills_found.add(skill.title())
            
            return list(skills_found)
        
        # Organizar dados por setor
        sectors_data = {}
        total_jobs = 0
        
        for job in jobs:
            sector = job.get('setor', job.get('area', 'Outros'))
            if not sector or sector.strip() == '':
                sector = 'Outros'
            
            if sector not in sectors_data:
                sectors_data[sector] = {
                    'jobs': [],
                    'skills_count': {},
                    'salaries': []
                }
            
            # Extrair skills do job
            job_skills = extract_real_skills(job)
            sectors_data[sector]['jobs'].append(job)
            
            # Contar skills
            for skill in job_skills:
                if skill not in sectors_data[sector]['skills_count']:
                    sectors_data[sector]['skills_count'][skill] = 0
                sectors_data[sector]['skills_count'][skill] += 1
            
            total_jobs += 1
        
        # Construir resposta
        sectors_response = []
        
        for sector_name, sector_data in sectors_data.items():
            total_sector_jobs = len(sector_data['jobs'])
            
            # Calcular top skills (apenas skills que aparecem em pelo menos 2 vagas)
            top_skills = []
            for skill, count in sorted(sector_data['skills_count'].items(), key=lambda x: x[1], reverse=True):
                if count >= 2:  # Filtrar skills que aparecem pelo menos 2 vezes
                    percentage = (count / total_sector_jobs) * 100
                    top_skills.append(SkillBySector(
                        skill=skill,
                        percentage=round(percentage, 1),
                        job_count=count
                    ))
                    if len(top_skills) >= 15:  # Limitar a 15 skills por setor
                        break
            
            if total_sector_jobs >= 3:  # Apenas setores com pelo menos 3 vagas
                sectors_response.append(SectorSkills(
                    sector=sector_name,
                    total_jobs=total_sector_jobs,
                    average_salary=None,  # Não calculamos salário por enquanto
                    top_skills=top_skills
                ))
        
        # Ordenar setores por número de vagas
        sectors_response.sort(key=lambda x: x.total_jobs, reverse=True)
        
        return SkillsBySectorResponse(
            sectors=sectors_response,
            total_jobs_analyzed=total_jobs,
            last_updated=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar skills por setor: {str(e)}")



if __name__ == "__main__":
    print("🚀 Iniciando API de Vagas e Skills...")
    print(f"📊 Conectando ao Supabase: {SUPABASE_URL}")
    
    uvicorn.run(
        "api_vagas_skills:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )