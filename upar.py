#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Upload de CSV para Supabase (tabela public.jobs)
- Faz upsert com on_conflict='link'
- Normaliza datas e modalidade
- Lida com CSV com cabeçalhos em PT-BR (Fonte, Titulo, Publicada em, ...)

Uso:
  export SUPABASE_URL="https://<your-project>.supabase.co"
  export SUPABASE_SERVICE_ROLE_KEY="<service-role-key>"
  python upload_csv_supabase.py --csv vagas.csv --table jobs --batch-size 300

Dica:
  Use --dry-run para só ver o que seria enviado (sem gravar).
"""

import os
import csv
import re
import argparse
from datetime import datetime, timedelta, date
from typing import Dict, Any, List, Optional

from supabase import create_client, Client
from tqdm import tqdm

# --------- Config de mapeamento: CSV -> colunas da tabela ----------
CSV_TO_DB = {
    "Fonte": "fonte",
    "Titulo": "titulo",
    "Link": "link",
    "Area": "area",
    "Localidade": "localidade",
    "Salario": "salario",
    "Habilidades": "habilidades",
    "Empresa": "empresa",
    "Publicada em": "publicada_em",
    "Modalidade": "modalidade",
    "Requisitos": "requisitos",
    "Descricao": "descricao",
    "Setor": "setor",
    "Beneficios": "beneficios",
    "Horario": "horario",
    "Regime contratacao": "regime_contratacao",
    "Data publicacao": "data_publicacao",
    "Nivel": "nivel",
}

VALID_MODALIDADES = {"remoto": "remoto", "presencial": "presencial", "híbrido": "híbrido", "hibrido": "híbrido"}

# --------- Helpers de normalização --------------------------------
def _none_if_blank(x: Optional[str]) -> Optional[str]:
    if x is None:
        return None
    s = str(x).strip()
    return s if s else None

def normalize_modalidade(s: Optional[str]) -> Optional[str]:
    s = _none_if_blank(s)
    if not s:
        return None
    txt = s.lower()
    for k, v in VALID_MODALIDADES.items():
        if k in txt:
            return v
    return None  # evita violar o CHECK da tabela

DATE_RE = re.compile(r"(\d{1,2})/(\d{1,2})(?:/(\d{2,4}))?")

def parse_date_br(s: Optional[str]) -> Optional[str]:
    """
    Converte strings como:
      'Publicada hoje', 'hoje', 'ontem', '24/06', '24/06/2025'
    para ISO 'YYYY-MM-DD'. Caso não reconheça, retorna None.
    """
    s = _none_if_blank(s)
    if not s:
        return None
    txt = s.lower()

    # remover prefixos comuns
    txt = txt.replace("publicada em", "").replace("publicada", "").strip()

    # hoje/ontem
    if "hoje" in txt:
        return date.today().isoformat()
    if "ontem" in txt:
        return (date.today() - timedelta(days=1)).isoformat()

    # há X dias
    m = re.search(r"há\s+(\d+)\s+dias?", txt)
    if m:
        dias = int(m.group(1))
        return (date.today() - timedelta(days=dias)).isoformat()

    # dd/mm[/aaaa]
    m = DATE_RE.search(txt)
    if m:
        dd, mm, yy = m.group(1), m.group(2), m.group(3)
        day = int(dd)
        month = int(mm)
        if yy:
            year = int(yy)
            if year < 100:  # '24' -> 2024 (heurística)
                year += 2000
        else:
            year = date.today().year
        try:
            return date(year, month, day).isoformat()
        except Exception:
            return None

    return None

def normalize_lista_semicolons(s: Optional[str]) -> Optional[str]:
    """
    Normaliza listas separadas por vírgula/; para '; ' (padrão do seu scraper).
    """
    s = _none_if_blank(s)
    if not s:
        return None
    # quebra por ; ou , e junta com ; 
    parts = re.split(r"[;,]\s*", s.strip())
    parts = [p.strip() for p in parts if p.strip()]
    return "; ".join(dict.fromkeys(parts)) if parts else None

# --------- Supabase Client ----------------------------------------
def get_client() -> Client:
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_KEY")
    if not url or not key:
        raise RuntimeError("Defina SUPABASE_URL e SUPABASE_SERVICE_ROLE_KEY nas variáveis de ambiente.")
    return create_client(url, key)

# --------- Transform de uma linha do CSV -> dict p/ DB ------------
def row_to_db(row: Dict[str, str]) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for csv_key, db_key in CSV_TO_DB.items():
        val = row.get(csv_key)

        # Normalizações específicas por campo
        if db_key in ("publicada_em", "data_publicacao"):
            out[db_key] = parse_date_br(val)
        elif db_key == "modalidade":
            out[db_key] = normalize_modalidade(val)
        elif db_key in ("beneficios", "habilidades", "requisitos"):
            out[db_key] = normalize_lista_semicolons(val)
        else:
            out[db_key] = _none_if_blank(val)

    return out

# --------- Upload em lotes ----------------------------------------
def upload_csv(csv_path: str, table: str = "jobs", batch_size: int = 300, dry_run: bool = False) -> None:
    print(f"Iniciando upload do arquivo: {csv_path}")
    supabase = get_client()
    print("Cliente Supabase conectado com sucesso")

    # Ler CSV
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        # checar se todas as colunas existem (avisa, mas não trava)
        missing = [k for k in CSV_TO_DB.keys() if k not in reader.fieldnames]
        if missing:
            print(f"[AVISO] Cabeçalhos ausentes no CSV: {missing} — prosseguindo com o que houver.")

        buffer: List[Dict[str, Any]] = []
        total, enviados = 0, 0

        for row in reader:
            total += 1
            payload = row_to_db(row)

            # sanity: precisa de link para ser upsertável
            if not payload.get("link"):
                continue

            buffer.append(payload)

            if len(buffer) >= batch_size:
                if dry_run:
                    enviados += len(buffer)
                    buffer.clear()
                else:
                    # Upsert em lote
                    supabase.table(table).upsert(buffer, on_conflict="link").execute()
                    enviados += len(buffer)
                    buffer.clear()

        # flush final
        if buffer:
            if not dry_run:
                supabase.table(table).upsert(buffer, on_conflict="link").execute()
            enviados += len(buffer)

    print(f"Concluído. Linhas lidas: {total}. Registros enviados: {enviados} (tabela: {table}). {'[DRY RUN]' if dry_run else ''}")

# --------- CLI ----------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Upload de CSV para Supabase (tabela jobs) com upsert por link.")
    parser.add_argument("--csv", required=True, help="Caminho do arquivo CSV")
    parser.add_argument("--table", default="jobs", help="Nome da tabela (default: jobs)")
    parser.add_argument("--batch-size", type=int, default=300, help="Tamanho do lote (default: 300)")
    parser.add_argument("--dry-run", action="store_true", help="Não grava no banco; só simula/processa")
    args = parser.parse_args()

    try:
        upload_csv(args.csv, table=args.table, batch_size=args.batch_size, dry_run=args.dry_run)
    except Exception as e:
        print(f"Erro ao enviar CSV: {e}")
        raise

if __name__ == "__main__":
    main()
