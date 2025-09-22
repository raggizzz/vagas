#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
from typing import List, Optional, Dict
from supabase import create_client, Client
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from dotenv import load_dotenv
from datetime import datetime

# ---------------------------
# Configuração Supabase
# ---------------------------
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("⚠️ Configure SUPABASE_URL e SUPABASE_SERVICE_KEY nas variáveis de ambiente.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ---------------------------
# Configuração FastAPI
# ---------------------------
app = FastAPI(title="API Vagas", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

# ---------------------------
# Modelos de resposta
# ---------------------------
class JobResponse(BaseModel):
    id: int
    titulo: str
    empresa: Optional[str]
    setor: Optional[str]
    regime_contratacao: Optional[str]
    modalidade: Optional[str]
    localidade: Optional[str]
    salario: Optional[str]
    descricao: Optional[str]
    habilidades: List[str] = []
    requisitos: List[str] = []
    publicada_em: Optional[str]

# ---------------------------
# Helpers
# ---------------------------
def parse_skills(job: Dict) -> List[str]:
    skills = []
    for field in ["habilidades", "requisitos"]:
        if job.get(field):
            parts = re.split(r"[;,\n]", job[field])
            skills.extend([p.strip() for p in parts if p.strip()])
    return list(set(skills))

# ---------------------------
# Endpoints
# ---------------------------

@app.get("/", summary="Informações da API")
async def root():
    return {
        "message": "API de Vagas conectada ao Supabase",
        "version": "1.0.0",
        "endpoints": ["/jobs", "/jobs-filtered", "/skills-by-sector"]
    }

@app.get("/jobs", response_model=List[JobResponse])
async def get_jobs(limit: int = 50, offset: int = 0):
    """Lista todas as vagas"""
    try:
        response = supabase.table("vagas").select("*").range(offset, offset + limit - 1).execute()
        jobs = response.data or []

        return [
            JobResponse(
                id=job.get("id"),
                titulo=job.get("titulo"),
                empresa=job.get("empresa"),
                setor=job.get("setor"),
                regime_contratacao=job.get("regime_contratacao"),
                modalidade=job.get("modalidade"),
                localidade=job.get("localidade"),
                salario=job.get("salario"),
                descricao=job.get("descricao"),
                habilidades=parse_skills(job),
                requisitos=parse_skills(job),
                publicada_em=job.get("data_publicacao"),
            )
            for job in jobs
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar vagas: {e}")

@app.get("/jobs-filtered", response_model=List[JobResponse])
async def get_jobs_filtered(
    setor: Optional[str] = None,
    localidade: Optional[str] = None,
    modalidade: Optional[str] = None,
    regime: Optional[str] = None,
    salario: Optional[str] = None,
    titulo: Optional[str] = None,
    horario: Optional[str] = None,
    requisitos: Optional[str] = None,
    limit: int = 50
):
    """Filtrar vagas por setor, localidade, modalidade, regime, salário, título, horário e requisitos"""
    try:
        query = supabase.table("vagas").select("*")

        if setor: query = query.ilike("setor", f"%{setor}%")
        if localidade: query = query.ilike("localidade", f"%{localidade}%")
        if modalidade: query = query.ilike("modalidade", f"%{modalidade}%")
        if regime: query = query.ilike("regime_contratacao", f"%{regime}%")
        if salario: query = query.ilike("salario", f"%{salario}%")
        if titulo: query = query.ilike("titulo", f"%{titulo}%")
        if horario: query = query.ilike("horario", f"%{horario}%")
        if requisitos: query = query.ilike("requisitos", f"%{requisitos}%")

        jobs = query.limit(limit).execute().data or []

        return [
            JobResponse(
                id=job.get("id"),
                titulo=job.get("titulo"),
                empresa=job.get("empresa"),
                setor=job.get("setor"),
                regime_contratacao=job.get("regime_contratacao"),
                modalidade=job.get("modalidade"),
                localidade=job.get("localidade"),
                salario=job.get("salario"),
                descricao=job.get("descricao"),
                habilidades=parse_skills(job),
                requisitos=parse_skills(job),
                publicada_em=job.get("data_publicacao"),
            )
            for job in jobs
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no filtro: {e}")

@app.get("/skills-by-sector")
async def skills_by_sector():
    """Estatísticas de skills agrupadas por setor"""
    try:
        jobs = supabase.table("vagas").select("*").execute().data or []
        sectors = {}

        for job in jobs:
            sector = job.get("setor") or "Outros"
            if sector not in sectors:
                sectors[sector] = {"count": 0, "skills": {}}
            sectors[sector]["count"] += 1

            for skill in parse_skills(job):
                sectors[sector]["skills"][skill] = sectors[sector]["skills"].get(skill, 0) + 1

        results = []
        for sector, data in sectors.items():
            skills_sorted = sorted(data["skills"].items(), key=lambda x: x[1], reverse=True)
            results.append({
                "sector": sector,
                "total_jobs": data["count"],
                "top_skills": [{"skill": s, "count": c} for s, c in skills_sorted[:10]]
            })

        return {"sectors": results, "last_updated": datetime.now().isoformat()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar estatísticas: {e}")

# ---------------------------
# Runner
# ---------------------------
if __name__ == "__main__":
    uvicorn.run("api_vagas_skills:app", host="0.0.0.0", port=8000, reload=True)