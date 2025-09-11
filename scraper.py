#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import csv
import time
import random
import sqlite3
import argparse
import requests
from dataclasses import dataclass
from typing import Optional, Iterable, List, Dict
from datetime import datetime, timedelta
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

# Selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.common.exceptions import (
    TimeoutException, WebDriverException
)
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ---------------------------
# Config HTTP / sessão
# ---------------------------
DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Referer': 'https://www.google.com/',
}
SESSION = requests.Session()
SESSION.headers.update(DEFAULT_HEADERS)

UF_CODES = {
    "AC","AL","AP","AM","BA","CE","DF","ES","GO","MA","MT","MS","MG","PA","PB","PR",
    "PE","PI","RJ","RN","RS","RO","RR","SC","SP","SE","TO"
}

# ---------------------------
# Setores Catho
# ---------------------------
CATHO_SECTORS = {
    'Administracao': {'url': 'https://www.catho.com.br/vagas/?area_id%5B0%5D=1&area_id%5B1%5D=3&area_id%5B2%5D=12&area_id%5B3%5D=20&area_id%5B4%5D=47&area_id%5B5%5D=67&area_id%5B6%5D=69&area_id%5B7%5D=73&area_id%5B8%5D=74&area_id%5B9%5D=75&area_id%5B10%5D=1906&area_id%5B11%5D=1937'},
    'Comercial e vendas': {'url': 'https://www.catho.com.br/vagas/area-comercial-vendas/'},
    'Comercio exterior': {'url': 'https://www.catho.com.br/vagas/?area_id%5B0%5D=15&area_id%5B1%5D=70'},
    'Educacao': {'url': 'https://www.catho.com.br/vagas/?area_id%5B0%5D=24&area_id%5B1%5D=87'},
    'Financeira': {'url': 'https://www.catho.com.br/vagas/?area_id%5B0%5D=2&area_id%5B1%5D=11&area_id%5B2%5D=19&area_id%5B3%5D=23&area_id%5B4%5D=40&area_id%5B5%5D=76'},
    'Hotelaria e turismo': {'url': 'https://www.catho.com.br/vagas/?area_id%5B0%5D=48&area_id%5B1%5D=72'},
    'Informatica': {'url': 'https://www.catho.com.br/vagas/?area_id%5B0%5D=51&area_id%5B1%5D=52'},
    'Saude': {'url': 'https://www.catho.com.br/vagas/?area_id%5B0%5D=13&area_id%5B1%5D=26&area_id%5B2%5D=39&area_id%5B3%5D=41&area_id%5B4%5D=43&area_id%5B5%5D=45&area_id%5B6%5D=46&area_id%5B7%5D=58&area_id%5B8%5D=61&area_id%5B9%5D=62&area_id%5B10%5D=65&area_id%5B11%5D=1902'},
    'Suprimentos': {'url': 'https://www.catho.com.br/vagas/?area_id%5B0%5D=55&area_id%5B1%5D=88'},
    'Agricultura,pecuaria e veterinaria': {'url': 'https://www.catho.com.br/vagas/?area_id%5B0%5D=1858&area_id%5B1%5D=1859&area_id%5B2%5D=1904&area_id%5B3%5D=1943'},
    'Artes,arquitetura e design': {'url': 'https://www.catho.com.br/vagas/?area_id%5B0%5D=5&area_id%5B1%5D=6&area_id%5B2%5D=7&area_id%5B3%5D=21&area_id%5B4%5D=60'},
    'Comunicacao e marketing': {'url': 'https://www.catho.com.br/vagas/?area_id%5B0%5D=53&area_id%5B1%5D=57&area_id%5B2%5D=66&area_id%5B3%5D=71&area_id%5B4%5D=1965'},
    'Engenharia': {'url': 'https://www.catho.com.br/vagas/?area_id%5B0%5D=18&area_id%5B1%5D=29&area_id%5B2%5D=30&area_id%5B3%5D=31&area_id%5B4%5D=32&area_id%5B5%5D=34&area_id%5B6%5D=35&area_id%5B7%5D=36&area_id%5B8%5D=37&area_id%5B9%5D=38&area_id%5B10%5D=483&area_id%5B11%5D=484'},
    'Industrial': {'url': 'https://www.catho.com.br/vagas/?area_id%5B0%5D=9&area_id%5B1%5D=10&area_id%5B2%5D=25&area_id%5B3%5D=50&area_id%5B4%5D=56'},
    'Juridica': {'url': 'https://www.catho.com.br/vagas/area-juridica/'},
    'Tecnica': {'url': 'https://www.catho.com.br/vagas/?area_id%5B0%5D=79&area_id%5B1%5D=80'},
    'Telemarketing': {'url': 'https://www.catho.com.br/vagas/area-atendimento-ao-cliente-call-center-telemarketing/'},
    'Telecomunicacoes': {'url': 'https://www.catho.com.br/vagas/area-telecomunicacoes-engenharia-de-telecomunicacoes/'},
    'ServicoSocial': {'url': 'https://www.catho.com.br/vagas/area-servico-social/'}
}

# ---------------------------
# Model
# ---------------------------
@dataclass
class Job:
    fonte: str
    titulo: str
    link: str
    area: Optional[str] = None
    localidade: Optional[str] = None
    salario: Optional[str] = None
    habilidades: Optional[str] = None
    empresa: Optional[str] = None
    publicada_em: Optional[str] = None
    modalidade: Optional[str] = None
    requisitos: Optional[str] = None
    descricao: Optional[str] = None
    setor: Optional[str] = None
    beneficios: Optional[str] = None
    horario: Optional[str] = None
    regime_contratacao: Optional[str] = None
    data_publicacao: Optional[str] = None
    nivel: Optional[str] = None

# ---------------------------
# Helpers de parsing
# ---------------------------
def html_to_clean_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script","style","noscript"]): tag.decompose()
    for tag in soup.select("header, footer, nav, aside, svg"): tag.decompose()
    container = soup.select_one("main") or soup.select_one("article") or soup.body
    text = container.get_text("\n", strip=True) if container else soup.get_text("\n", strip=True)
    text = text.replace("·", "- ").replace("•", "- ").replace("\r", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

def title_from_slug(url: str) -> Optional[str]:
    try:
        path = urlparse(url).path.strip("/")
        # /vagas/<slug>/<id>/
        parts = path.split("/")
        if len(parts) >= 3 and parts[0] == "vagas":
            slug = parts[1]
        elif len(parts) >= 2 and parts[0] == "vagas":
            slug = parts[1]
        else:
            return None
        slug = slug.replace("-", " ")
        # Title-case com exceções simples
        words = []
        for w in slug.split():
            if w.lower() in {"de","da","do","e","em","para","com","a","o"}:
                words.append(w.lower())
            else:
                words.append(w.capitalize())
        return " ".join(words)
    except Exception:
        return None

def _float_money(s):
    try: return float(s.replace("R$","").replace(".","").replace(",",".").strip())
    except: return None

def parse_date_from_text(val: str) -> Optional[str]:
    now = datetime.now()
    v = val.strip().lower()
    if v.startswith("hoje"):
        return now.strftime("%Y-%m-%d")
    if v.startswith("ontem"):
        return (now - timedelta(days=1)).strftime("%Y-%m-%d")
    m = re.search(r"há\s+(\d+)\s+dias?", v)
    if m:
        return (now - timedelta(days=int(m.group(1)))).strftime("%Y-%m-%d")
    m = re.search(r"([0-3]?\d)/([01]?\d)(?:/(\d{2,4}))?", v)
    if m:
        d, mo, y = m.group(1), m.group(2), m.group(3)
        if y and len(y) == 2: y = "20"+y
        if not y: y = str(now.year)
        try:
            return datetime(int(y), int(mo), int(d)).strftime("%Y-%m-%d")
        except: pass
    return None

def parse_vaga_from_text(text: str, job_url: Optional[str] = None) -> dict:
    t = text
    BAD = {"candidatura fácil","candidatos","compatibilidade","gráfico de colunas","suas chances","mostrar menos","compartilhar"}
    lines = [ln.strip() for ln in t.splitlines() if ln.strip()]

    # -------- título (evita "Sobre a vaga")
    titulo = None
    # primeiro: linha que parece H1 antes de "Sobre a vaga"
    for i, ln in enumerate(lines[:80]):
        low = ln.lower()
        if low in BAD or "sobre a vaga" in low or ln.endswith(":"): 
            continue
        if 3 < len(ln) < 100 and not ln.isupper():
            # heurística: se a próxima linha for nome da empresa ou ficar perto de "Vaga com..." ainda ok
            titulo = ln
            break
    # fallback pelo slug
    if not titulo and job_url:
        titulo = title_from_slug(job_url)

    # -------- empresa
    empresa = None
    m = re.search(r"Dados da Empresa\s*\n([^\n]{2,100})", t, re.I)
    if m:
        empresa = m.group(1).strip()
    if not empresa and titulo:
        # linha imediatamente abaixo do título frequentemente é empresa
        try:
            idx = lines.index(titulo)
            if idx+1 < len(lines):
                cand = lines[idx+1]
                if cand and 2 < len(cand) < 80 and "vaga com recrutador" not in cand.lower():
                    empresa = cand
        except ValueError:
            pass

    # -------- data de publicação
    publicada_em = None
    m = re.search(r"Publicada\s+(hoje|ontem|há\s+\d+\s+dias?|em\s+[0-3]?\d/[01]?\d(?:/\d{2,4})?)", t, re.I)
    if m:
        publicada_em = parse_date_from_text(m.group(1))

    # -------- localização
    localidade = None
    # padrão "1 vaga: Cidade - UF"
    m = re.search(r"vaga[s]?:\s*([A-Za-zÁ-ú\.\s\-]+-\s*([A-Z]{2}))", t, re.I)
    if m:
        uf = m.group(2).upper()
        if uf in UF_CODES:
            localidade = m.group(1).strip()
    if not localidade:
        # "Cidade - UF" solto
        m = re.search(r"\b([A-Za-zÁ-ú\. ]+)\s*-\s*([A-Z]{2})\b", t)
        if m and m.group(2).upper() in UF_CODES:
            localidade = f"{m.group(1).strip()} - {m.group(2).upper()}"

    # -------- salário
    salario = None
    if re.search(r"\bA combinar\b", t, re.I):
        salario = None
    else:
        faixa = re.search(r"(R\$\s?[\d\.\,]+)\s*(?:a|–|-|até)\s*(R\$\s?[\d\.\,]+)", t, re.I)
        if faixa:
            salario = {"min": faixa.group(1), "max": faixa.group(2)}
        else:
            vals = re.findall(r"R\$\s?\d{1,3}(?:\.\d{3})*(?:,\d{2})?", t)
            if vals:
                salario = {"value": max(vals, key=_float_money)}

    # -------- regime
    regime = None
    m = re.search(r"Regime de Contrata[cç][aã]o\s*\n([^\n]+)", t, re.I)
    if m: regime = m.group(1).strip()

    # -------- horário
    horario = None
    m = re.search(r"Hor[áa]rio\s*\n([^\n]+)", t, re.I)
    if m:
        horario = m.group(1).strip()
    if not horario:
        m = re.search(r"(?:Das?|de)\s*(\d{1,2}[:h]\d{2})\s*(?:às|as|-|a)\s*(\d{1,2}[:h]\d{2})", t, re.I)
        if m:
            h1 = m.group(1).replace("h", ":"); h2 = m.group(2).replace("h", ":")
            horario = f"{h1} às {h2}"

    # -------- benefícios
    beneficios: List[str] = []
    m = re.search(r"Benef[ií]cios\s*\n([^\n]+)", t, re.I)
    if m:
        raw = m.group(1)
        beneficios = [re.sub(r"\s*/\s*Medicina em grupo", "", p, flags=re.I).strip()
                      for p in re.split(r",|;|\|", raw) if p.strip()]

    # -------- modalidade
    modalidade = None
    lowt = t.lower()
    if "remoto" in lowt or "home office" in lowt: modalidade = "remoto"
    elif "híbrido" in lowt or "hibrido" in lowt: modalidade = "híbrido"
    elif "presencial" in lowt: modalidade = "presencial"

    # -------- bullets (competências vs requisitos)
    bullets: List[str] = []
    for ln in lines:
        if re.match(r"^[\-\u2013\u2014]\s?.+", ln):  # -, – ou —
            bullets.append(re.sub(r"^[\-\u2013\u2014]\s?", "", ln).strip(" .;"))

    requisitos_livres: List[str] = []
    for ln in lines:
        s = ln
        if s.lower() in BAD: continue
        if re.match(r"^(Experi[êe]ncia|Ensino|Escolaridade|Gradua[cç][aã]o|Ingl[eê]s|Espanhol|Franc[eê]s|Alem[aã]o|Excel|Conhecimento|Sistema|Winthor)", s, re.I):
            requisitos_livres.append(s)

    VERB_PREFIXES = ("Realizar","Análise","Analisar","Elaboração","Elaborar","Gestão","Gerir",
                     "Controle","Controlar","Cadastramento","Cadastrar","Verificação","Verificar",
                     "Relacionamento","Relacionar","Suporte","Apoiar","Auxiliar","Examinar","Impugnação","Impugnar",
                     "Emissão","Atualização","Definição","Programação","Conferência","Acompanhamento","Cadastro","Cotação")
    competencias, requisitos = [], []
    for b in bullets:
        if b.startswith(VERB_PREFIXES):
            competencias.append(b)
        elif re.search(r"\b(Experi[êe]ncia|Form[aá]?[cç][aã]o|Escolaridade|Certificado|Curso|Habilita[cç][aã]o|Conhecimento|Ingl[eê]s|Espanhol|Excel|Winthor|SQL|Power BI|Tableau)\b", b, re.I):
            requisitos.append(b)
        else:
            competencias.append(b)
    requisitos.extend(requisitos_livres)

    def _dedup(seq: List[str]) -> List[str]:
        out, seen = [], set()
        for x in seq:
            k = x.strip().lower()
            if k and k not in seen:
                seen.add(k); out.append(x.strip())
        return out

    competencias = _dedup(competencias)
    requisitos = _dedup(requisitos)
    beneficios = _dedup(beneficios)

    # -------- nível pelo título
    nivel = None
    if titulo:
        m = re.search(r"\b(J[úu]nior|Junior|Pleno|S[êe]nior|Senior|Est[áa]gio|Trainee)\b", titulo, re.I)
        if m: 
            nivel = m.group(1).title().replace("Junior","Júnior").replace("Senior","Sênior")

    # -------- se horário veio como "Remote Work", trate como modalidade
    if horario and re.search(r"remote\s*work", horario, re.I):
        modalidade = modalidade or "remoto"
        horario = None

    return {
        "titulo": titulo,
        "empresa": empresa,
        "publicada_em": publicada_em,
        "localidade": localidade,
        "salario": salario,
        "regime_contratacao": regime,
        "horario": horario,
        "beneficios": beneficios,
        "requisitos": requisitos,
        "competencias": competencias,
        "modalidade": modalidade,
        "nivel": nivel,
        "descricao_bruta": t
    }

# ---------------------------
# Persistência
# ---------------------------
class JobStore:
    def __init__(self, db_path: str = "jobs.db"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._create_table()

    def _create_table(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fonte TEXT NOT NULL,
                titulo TEXT NOT NULL,
                link TEXT UNIQUE NOT NULL,
                area TEXT,
                localidade TEXT,
                salario TEXT,
                habilidades TEXT,
                empresa TEXT,
                publicada_em TEXT,
                modalidade TEXT,
                requisitos TEXT,
                descricao TEXT,
                setor TEXT,
                beneficios TEXT,
                horario TEXT,
                regime_contratacao TEXT,
                data_publicacao TEXT,
                nivel TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        for name, typ in [
            ("setor", "TEXT"), ("beneficios", "TEXT"), ("horario", "TEXT"),
            ("regime_contratacao", "TEXT"), ("data_publicacao", "TEXT"), ("nivel", "TEXT")
        ]:
            try:
                self.conn.execute(f"ALTER TABLE jobs ADD COLUMN {name} {typ}")
            except sqlite3.OperationalError:
                pass
        self.conn.commit()

    def upsert(self, job: Job):
        self.conn.execute("""
            INSERT OR REPLACE INTO jobs (
                fonte, titulo, link, area, localidade, salario, habilidades, empresa,
                publicada_em, modalidade, requisitos, descricao, setor, beneficios, horario,
                regime_contratacao, data_publicacao, nivel
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            job.fonte, job.titulo, job.link, job.area, job.localidade, job.salario,
            job.habilidades, job.empresa, job.publicada_em, job.modalidade, job.requisitos,
            job.descricao, job.setor, job.beneficios, job.horario, job.regime_contratacao,
            job.data_publicacao, job.nivel
        ))
        self.conn.commit()

    def export_csv(self, filename: str):
        cols = ["fonte","titulo","link","area","localidade","salario","habilidades","empresa",
                "publicada_em","modalidade","requisitos","descricao","setor",
                "beneficios","horario","regime_contratacao","data_publicacao","nivel"]
        cursor = self.conn.execute(f"SELECT {', '.join(cols)} FROM jobs ORDER BY id DESC")
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            w = csv.writer(f)
            w.writerow(["Fonte","Titulo","Link","Area","Localidade","Salario","Habilidades","Empresa",
                        "Publicada em","Modalidade","Requisitos","Descricao","Setor",
                        "Beneficios","Horario","Regime contratacao","Data publicacao","Nivel"])
            w.writerows(cursor.fetchall())
        print(f"Dados exportados para {filename}")

    def close(self):
        self.conn.close()

# ---------------------------
# Provider Catho (Selenium)
# ---------------------------
class CathoProvider:
    BASE = "https://www.catho.com.br"

    def __init__(self, sectors_list: Optional[List[str]] = None, headless: bool = True):
        self.sectors_list = list(sectors_list) if sectors_list else list(CATHO_SECTORS.keys())
        self.driver: Optional[webdriver.Chrome] = None
        self.headless = headless
        self._logged_in = False
        self.account = {
            "email": "igorperes005@gmail.com",
            "password": "Igor311205@"
        }

    def _setup_driver(self) -> bool:
        if self.driver: return True
        options = Options()
        if self.headless: options.add_argument("--headless=new")
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument('--user-agent=' + DEFAULT_HEADERS['User-Agent'])
        options.add_argument('--no-sandbox'); options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size=1920,1080')
        service = Service(ChromeDriverManager().install())
        try:
            self.driver = webdriver.Chrome(service=service, options=options)
            self.driver.set_page_load_timeout(25)
            self.driver.implicitly_wait(5)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.driver.get('about:blank')
            return True
        except Exception as e:
            print(f"[Driver] erro: {e}")
            self.driver = None
            return False

    def _login_if_needed(self) -> bool:
        if self._logged_in or not self.driver: return True
        if not (self.account["email"] and self.account["password"]):
            return True
        try:
            self.driver.get(f"{self.BASE}/login")
            time.sleep(2)
            wait = WebDriverWait(self.driver, 12)
            email = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="email"],input[name="email"],input#email')))
            email.clear(); email.send_keys(self.account["email"])
            pwd = self.driver.find_element(By.CSS_SELECTOR, 'input[type="password"],input[name="password"],input#password')
            pwd.clear(); pwd.send_keys(self.account["password"])
            for sel in ['button[type="submit"]','input[type="submit"]','.btn-login']:
                try:
                    self.driver.find_element(By.CSS_SELECTOR, sel).click(); break
                except: pass
            time.sleep(3)
            if 'login' not in self.driver.current_url.lower():
                self._logged_in = True
            return True
        except Exception as e:
            print(f"[Login] aviso: {e}")
            return True

    @staticmethod
    def _extract_job_links_from_listing_html(html: str) -> List[str]:
        soup = BeautifulSoup(html, "html.parser")
        links = []
        for a in soup.select('a[href*="/vagas/"]'):
            href = a.get('href') or ''
            if not href: continue
            if any(x in href.lower() for x in ['/empresa/','/company/','/anunciar','/cadastro','/login',
                                               '/por-local/','/por-area/','filtros','busca-de-vagas',
                                               '/vagas/?','/vagas/$']):
                continue
            if re.search(r'/vagas/[^/]+/\d+/?$', href):
                links.append(href if href.startswith('http') else urljoin(CathoProvider.BASE, href))
        # dedup
        out, seen = [], set()
        for u in links:
            if u not in seen: seen.add(u); out.append(u)
        return out

    # --------- EXTRAÇÃO DETALHES ----------
    def _extract_by_selectors(self, soup: BeautifulSoup) -> Dict[str, Optional[str]]:
        def pick(selectors):
            for sel in selectors:
                el = soup.select_one(sel)
                if el:
                    txt = el.get_text(" ", strip=True)
                    if txt and len(txt) > 1:
                        return txt
            return None

        titulo = pick(['h1[data-testid="job-title"]','h1','.job-title','.vacancy-title','.position-title'])
        empresa = pick(['.company-name','.employer-name','[data-testid="company-name"]','.job-company','.job-header .company'])
        loc = pick(['.location','.job-location','[data-testid="location"]','.job-header .location','.position-location'])
        salario = pick(['.salary','.wage','.compensation','[data-testid="salary"]','.job-salary'])
        modalidade = pick(['.work-mode','.job-type','.employment-type','[data-testid="work-mode"]'])
        publicada = pick(['.publication-date','.posted-date','[data-testid="publication-date"]','.date-posted'])

        return {
            "titulo": titulo,
            "empresa": empresa,
            "localidade": loc,
            "salario_raw": salario,
            "modalidade": modalidade,
            "publicada_em": publicada
        }

    def extract_individual_job_details(self, job_url: str, setor_hint: Optional[str]) -> Optional[Dict]:
        try:
            self.driver.get(job_url)
            try:
                WebDriverWait(self.driver, 15).until(lambda d: d.execute_script("return document.readyState") == "complete")
            except TimeoutException:
                pass

            html = self.driver.page_source
            soup = BeautifulSoup(html, "html.parser")
            text = html_to_clean_text(html)

            # 1) tenta por seletores
            sel = self._extract_by_selectors(soup)

            # título (preferência seletor -> fallback texto -> slug)
            titulo = sel.get("titulo")
            if not titulo:
                titulo = parse_vaga_from_text(text, job_url).get("titulo")
            if not titulo:
                titulo = title_from_slug(job_url)
            if not titulo or "sobre a vaga" == titulo.strip().lower():
                titulo = title_from_slug(job_url)

            # empresa
            empresa = sel.get("empresa") or parse_vaga_from_text(text, job_url).get("empresa")

            # localidade (valida UF)
            localidade = sel.get("localidade")
            if localidade and re.search(r"\b([A-Za-zÁ-ú\. ]+)\s*-\s*([A-Z]{2})\b", localidade):
                uf = re.search(r"\b([A-Za-zÁ-ú\. ]+)\s*-\s*([A-Z]{2})\b", localidade).group(2).upper()
                if uf not in UF_CODES:
                    localidade = None
            if not localidade:
                localidade = parse_vaga_from_text(text, job_url).get("localidade")

            # salário
            salario = None
            if sel.get("salario_raw"):
                sraw = sel["salario_raw"]
                if not re.search(r"A combinar", sraw, re.I):
                    faixa = re.search(r"(R\$\s?[\d\.\,]+)\s*(?:a|–|-|até)\s*(R\$\s?[\d\.\,]+)", sraw, re.I)
                    if faixa:
                        salario = f"{faixa.group(1)} - {faixa.group(2)}"
                    else:
                        v = re.findall(r"R\$\s?\d{1,3}(?:\.\d{3})*(?:,\d{2})?", sraw)
                        if v: salario = max(v, key=_float_money)
            if not salario:
                p = parse_vaga_from_text(text, job_url).get("salario")
                if isinstance(p, dict):
                    salario = p.get("value") or (("{}".format(p.get("min",""))+" - "+p.get("max","")).strip(" -") if (p.get("min") or p.get("max")) else None)

            # modalidade
            modalidade = sel.get("modalidade")
            lowm = (modalidade or "").lower()
            if "remoto" in lowm or "home office" in lowm:
                modalidade = "remoto"
            elif "híbrido" in lowm or "hibrido" in lowm:
                modalidade = "híbrido"
            elif "presencial" in lowm:
                modalidade = "presencial"

            # publicada
            publicada_em = sel.get("publicada_em")
            if publicada_em:
                publicada_em = parse_date_from_text(publicada_em) or publicada_em
            else:
                publicada_em = parse_vaga_from_text(text, job_url).get("publicada_em")

            parsed = parse_vaga_from_text(text, job_url)

            # horário: se vier "Remote Work", virar modalidade
            horario = parsed.get("horario")
            if horario and re.search(r"remote\s*work", horario, re.I):
                modalidade = modalidade or "remoto"
                horario = None

            job = {
                "titulo": titulo,
                "empresa": empresa,
                "localidade": localidade,
                "modalidade": modalidade,
                "salario": salario,
                "habilidades": '; '.join(parsed.get("competencias") or []) or None,
                "requisitos": '; '.join(parsed.get("requisitos") or []) or None,
                "descricao": parsed.get("descricao_bruta"),
                "publicada_em": publicada_em,
                "setor": setor_hint or 'Outros',
                "beneficios": '; '.join(parsed.get("beneficios") or []) or None,
                "horario": horario,
                "regime_contratacao": parsed.get("regime_contratacao"),
                "nivel": parsed.get("nivel"),
                "link": job_url
            }

            # sanity: precisa de título
            if not job["titulo"]:
                return None
            return job

        except Exception as e:
            print(f"[Detalhe] erro em {job_url}: {e}")
            return None

    # --------- LOOP DE BUSCA ----------
    def search(self, paginas: int = 1, all_pages: bool = False) -> Iterable[Job]:
        if not self._setup_driver():
            print("[Catho] driver indisponível.")
            return
        self._login_if_needed()

        for sector_name, cfg in CATHO_SECTORS.items():
            if sector_name not in self.sectors_list: 
                continue
            base = cfg['url']
            page = 1
            vazias = 0
            print(f"\n[Catho] Setor: {sector_name}")
            while True:
                url = base + ("&p=" if "?" in base else "?p=") + str(page)
                print(f"[Catho] Página {page}: {url}")
                try:
                    self.driver.get(url)
                    time.sleep(0.8)
                    html = self.driver.page_source
                    if "404" in (self.driver.title or "").lower():
                        print("[Catho] 404 - fim do setor.")
                        break
                    links = self._extract_job_links_from_listing_html(html)
                    print(f"[Catho] {len(links)} links")
                    if not links:
                        vazias += 1
                        if vazias >= 3: 
                            print("[Catho] 3 páginas vazias seguidas - fim do setor.")
                            break
                        page += 1
                        if not all_pages and page > paginas: break
                        continue
                    vazias = 0

                    for lk in links:
                        data = self.extract_individual_job_details(lk, setor_hint=sector_name)
                        if not data: 
                            continue
                        yield Job(
                            fonte="catho",
                            titulo=data.get('titulo') or "Vaga - Catho",
                            link=data.get('link'),
                            area=None,
                            localidade=data.get('localidade'),
                            salario=data.get('salario'),
                            habilidades=data.get('habilidades'),
                            empresa=data.get('empresa'),
                            publicada_em=data.get('publicada_em'),
                            modalidade=data.get('modalidade'),
                            requisitos=data.get('requisitos'),
                            descricao=data.get('descricao'),
                            setor=data.get('setor') or sector_name,
                            beneficios=data.get('beneficios'),
                            horario=data.get('horario'),
                            regime_contratacao=data.get('regime_contratacao'),
                            data_publicacao=data.get('publicada_em'),
                            nivel=data.get('nivel')
                        )
                        time.sleep(random.uniform(0.1, 0.3))

                    page += 1
                    if not all_pages and page > paginas:
                        break
                except Exception as e:
                    print(f"[Catho] exceção na página {page}: {e}")
                    page += 1
                    if not all_pages and page > paginas:
                        break

        if self.driver:
            try: self.driver.quit()
            except: pass
            self.driver = None
        print("[Catho] busca finalizada.")

# ---------------------------
# Runner
# ---------------------------
def run(catho_pages: int = 1, catho_all: bool = False, catho_sectors: Optional[List[str]] = None,
        csv_file: Optional[str] = None, headless: bool = True) -> int:
    store = JobStore()
    total = 0
    try:
        sectors = list(catho_sectors) if catho_sectors else list(CATHO_SECTORS.keys())
        prov = CathoProvider(sectors_list=sectors, headless=headless)
        for job in prov.search(paginas=catho_pages, all_pages=catho_all):
            store.upsert(job)
            total += 1
        print(f"\nTotal de vagas coletadas: {total}")
        if csv_file:
            store.export_csv(csv_file)
        return total
    finally:
        store.close()

# ---------------------------
# CLI
# ---------------------------
def main():
    parser = argparse.ArgumentParser(description='Scraper Catho com parser robusto do texto completo e seletores de HTML.')
    parser.add_argument('--catho-pages', type=int, default=1, help='Páginas por setor (default: 1)')
    parser.add_argument('--catho-all', action='store_true', help='Varre todas as páginas informadas (por setor)')
    parser.add_argument('--catho-sectors', nargs='+', help=f'Setores a extrair. Disponíveis: {", ".join(CATHO_SECTORS.keys())}')
    parser.add_argument('--csv', type=str, help='Arquivo CSV de saída')
    parser.add_argument('--headless', action='store_true', help='Chrome em modo headless')
    args = parser.parse_args()

    if args.catho_sectors:
        invalid = [s for s in args.catho_sectors if s not in CATHO_SECTORS]
        if invalid:
            print(f"❌ Setores inválidos: {', '.join(invalid)}")
            print(f"   Válidos: {', '.join(CATHO_SECTORS.keys())}")
            return

    print("Configurações:")
    print(f"  - Setores: {', '.join(args.catho_sectors) if args.catho_sectors else 'TODOS'}")
    print(f"  - Páginas por setor: {'TODAS' if args.catho_all else args.catho_pages}")
    print(f"  - Headless: {bool(args.headless)}")
    if args.csv: print(f"  - CSV: {args.csv}")

    count = run(
        catho_pages=args.catho_pages,
        catho_all=args.catho_all,
        catho_sectors=args.catho_sectors,
        csv_file=args.csv,
        headless=bool(args.headless)
    )
    print(f"\nScraping concluído! {count} vagas coletadas.")

if __name__ == "__main__":
    main()
