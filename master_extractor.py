import pandas as pd
import json
import re
from datetime import datetime, timedelta
from collections import Counter
import unicodedata

def clean_description(description):
    """Remove ruídos e informações irrelevantes da descrição"""
    if not description or pd.isna(description):
        return ""
    
    desc = str(description)
    
    # Remove padrões de ruído comuns
    noise_patterns = [
        r'candidatura\s*f[aá]cil',
        r'continuar\s*lendo',
        r'leia\s*mais',
        r'ver\s*mais',
        r'clique\s*aqui',
        r'saiba\s*mais',
        r'acesse\s*o\s*link',
        r'entre\s*em\s*contato',
        r'envie\s*seu\s*curr[íi]culo',
        r'cadastre[\-\s]*se',
        r'inscreva[\-\s]*se',
        r'aplique[\-\s]*se',
        r'candidate[\-\s]*se',
        r'whatsapp\s*\d+',
        r'telefone\s*\d+',
        r'email\s*[^\s]+@[^\s]+',
        r'e[\-\s]*mail\s*[^\s]+@[^\s]+',
        r'www\.[^\s]+',
        r'http[s]?://[^\s]+',
        r'compartilhar\s*vaga',
        r'denunciar\s*vaga',
        r'salvar\s*vaga',
        r'favoritar\s*vaga',
    ]
    
    for pattern in noise_patterns:
        desc = re.sub(pattern, '', desc, flags=re.IGNORECASE)
    
    # Remove múltiplas quebras de linha e espaços
    desc = re.sub(r'\n\s*\n', '\n', desc)
    desc = re.sub(r'\s+', ' ', desc)
    
    return desc.strip()

def extract_location_advanced(description):
    """Extrai localização da descrição com fallback seguro"""
    if not description or pd.isna(description):
        return None
    
    desc = str(description)
    
    # Padrões para extrair localização
    location_patterns = [
        r'localiza[çc][ãa]o[:\s]*([^,\n]+)',
        r'local[:\s]*([^,\n]+)',
        r'cidade[:\s]*([^,\n]+)',
        r'regi[ãa]o[:\s]*([^,\n]+)',
        r'endere[çc]o[:\s]*([^,\n]+)',
        r'vaga\s*em\s*([^,\n]+)',
        r'oportunidade\s*em\s*([^,\n]+)',
        r'trabalhar\s*em\s*([^,\n]+)',
        # Estados brasileiros
        r'\b(acre|alagoas|amap[áa]|amazonas|bahia|cear[áa]|distrito federal|esp[íi]rito santo|goi[áa]s|maranh[ãa]o|mato grosso|mato grosso do sul|minas gerais|par[áa]|para[íi]ba|paran[áa]|pernambuco|piau[íi]|rio de janeiro|rio grande do norte|rio grande do sul|rond[ôo]nia|roraima|santa catarina|s[ãa]o paulo|sergipe|tocantins)\b',
        # Siglas de estados
        r'\b(AC|AL|AP|AM|BA|CE|DF|ES|GO|MA|MT|MS|MG|PA|PB|PR|PE|PI|RJ|RN|RS|RO|RR|SC|SP|SE|TO)\b',
        # Capitais principais
        r'\b(s[ãa]o paulo|rio de janeiro|belo horizonte|salvador|bras[íi]lia|fortaleza|manaus|curitiba|recife|porto alegre|bel[ée]m|goi[âa]nia|guarulhos|campinas|s[ãa]o lu[íi]s|s[ãa]o gon[çc]alo|maca[eé]i[óo]|duque de caxias|natal|teresina|campo grande|nova igua[çc]u|s[ãa]o bernardo do campo|jo[ãa]o pessoa|santos|osasco|santo andr[ée]|ribeir[ãa]o preto|uberl[âa]ndia|sorocaba|contagem|aracaju|feira de santana|cuiab[áa]|joinville|juiz de fora|londrina|aparecida de goi[âa]nia|ananindeua|porto velho|serra|niter[óo]i|caxias do sul|mau[áa]|s[ãa]o jo[ãa]o de meriti|campos dos goytacazes|vila velha|florianópolis|mogi das cruzes|volta redonda|são josé dos campos|diadema|carapicuíba|betim|petropolis|jundiaí|sumaré|piracicaba|franca|itaquaquecetuba|embu das artes|cariacica|maringá|blumenau|paulista|viamão)\b',
    ]
    
    for pattern in location_patterns:
        match = re.search(pattern, desc, re.IGNORECASE)
        if match:
            location = match.group(1).strip()
            # Limpa a localização
            location = re.sub(r'^[:\-\s]+|[:\-\s]+$', '', location)
            if len(location) > 2 and len(location) < 100:
                return location
    
    return None

def extract_published_date(description):
    """Extrai data de publicação da descrição"""
    if not description or pd.isna(description):
        return None
    
    desc = str(description).lower()
    
    # Data explícita (dd/mm/aaaa)
    date_patterns = [
        r'publicad[ao]\s*em[:\s]*(\d{1,2}\/\d{1,2}\/\d{4})',
        r'data[:\s]*(\d{1,2}\/\d{1,2}\/\d{4})',
        r'(\d{1,2}\/\d{1,2}\/\d{4})',
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, desc)
        if match:
            try:
                date_str = match.group(1)
                return datetime.strptime(date_str, '%d/%m/%Y').date().isoformat()
            except ValueError:
                continue
    
    # Data relativa
    relative_patterns = [
        r'h[áa]\s*(\d+)\s*dias?',
        r'(\d+)\s*dias?\s*atr[áa]s',
        r'h[áa]\s*(\d+)\s*horas?',
        r'(\d+)\s*horas?\s*atr[áa]s',
        r'h[áa]\s*(\d+)\s*semanas?',
        r'(\d+)\s*semanas?\s*atr[áa]s',
        r'ontem',
        r'hoje',
        r'esta\s*semana',
        r'semana\s*passada',
    ]
    
    now = datetime.now()
    
    for pattern in relative_patterns:
        if pattern in ['ontem', 'hoje', r'esta\s*semana', r'semana\s*passada']:
            if re.search(pattern, desc):
                if 'hoje' in pattern:
                    return now.date().isoformat()
                elif 'ontem' in pattern:
                    return (now - timedelta(days=1)).date().isoformat()
                elif r'esta\s*semana' in pattern:
                    return now.date().isoformat()
                elif r'semana\s*passada' in pattern:
                    return (now - timedelta(days=7)).date().isoformat()
        else:
            match = re.search(pattern, desc)
            if match:
                try:
                    value = int(match.group(1))
                    if 'dia' in pattern:
                        return (now - timedelta(days=value)).date().isoformat()
                    elif 'hora' in pattern:
                        return (now - timedelta(hours=value)).date().isoformat()
                    elif 'semana' in pattern:
                        return (now - timedelta(weeks=value)).date().isoformat()
                except (ValueError, IndexError):
                    continue
    
    return None

def extract_contract_type(description):
    """Extrai tipo de contrato e modelo de trabalho"""
    if not description or pd.isna(description):
        return {"contract_type": None, "work_model": None}
    
    desc = str(description).lower()
    
    # Tipo de contrato
    contract_type = None
    contract_patterns = {
        'clt': [r'\bclt\b', r'carteira\s*assinada', r'registro\s*em\s*carteira'],
        'pj': [r'\bpj\b', r'pessoa\s*jur[íi]dica', r'cnpj'],
        'estágio': [r'est[áa]gio', r'estagi[áa]rio'],
        'temporário': [r'tempor[áa]rio', r'contrato\s*tempor[áa]rio'],
        'aprendiz': [r'aprendiz', r'jovem\s*aprendiz'],
        'freelancer': [r'freelancer', r'free\s*lancer', r'aut[ôo]nomo'],
        'terceirizado': [r'terceirizado', r'terceiriza[çc][ãa]o'],
    }
    
    for contract, patterns in contract_patterns.items():
        for pattern in patterns:
            if re.search(pattern, desc):
                contract_type = contract
                break
        if contract_type:
            break
    
    # Modelo de trabalho
    work_model = None
    work_patterns = {
        'remoto': [r'remoto', r'home\s*office', r'trabalho\s*em\s*casa', r'distância'],
        'presencial': [r'presencial', r'no\s*local', r'escritório'],
        'híbrido': [r'h[íi]brido', r'misto', r'semi\s*presencial'],
    }
    
    for model, patterns in work_patterns.items():
        for pattern in patterns:
            if re.search(pattern, desc):
                work_model = model
                break
        if work_model:
            break
    
    return {"contract_type": contract_type, "work_model": work_model}

def normalize_text(text):
    """Normaliza texto removendo acentos e caracteres especiais"""
    if not text:
        return ""
    # Remove acentos
    text = unicodedata.normalize('NFD', text)
    text = ''.join(char for char in text if unicodedata.category(char) != 'Mn')
    return text.lower().strip()

def extract_salary_advanced(description):
    """Extrai informações salariais com suporte a vírgula decimal (pt-BR), faixas, período e comissão."""
    if not description or pd.isna(description):
        return {"min_salary": None, "max_salary": None, "salary_type": "a combinar", "commission": None, "currency": "BRL", "period": "mensal"}

    desc = str(description)
    desc_lower = desc.lower()

    # Comissão
    commission = None
    for pat in [
        r"comiss[ãa]o\s*de\s*([\d.,]+)%",
        r"comiss[ãa]o[:\s]*([\d.,]+)%",
        r"([\d.,]+)%\s*de\s*comiss[ãa]o",
    ]:
        m = re.search(pat, desc_lower)
        if m:
            # Converter percentual para número
            try:
                commission = float(str(m.group(1)).replace('.', '').replace(',', '.'))
            except ValueError:
                commission = m.group(1)
            break
    if commission is None and re.search(r"\bcomiss[ãa]o\b", desc_lower):
        commission = "sim"

    # Período do salário
    period = "mensal"
    if re.search(r"por\s*hora|hora\b", desc_lower):
        period = "hora"
    elif re.search(r"por\s*semana|semanal", desc_lower):
        period = "semanal"
    elif re.search(r"por\s*dia|di[áa]rio", desc_lower):
        period = "diario"

    # Padrões de faixa e valores únicos com formatos BR
    range_patterns = [
        r"(?:de|entre)\s*r?\$?\s*([\d\.\,]+)\s*(?:a|e|at[eé])\s*r?\$?\s*([\d\.\,]+)",
        r"([\d\.\,]+)\s*(?:a|\-)\s*r?\$?\s*([\d\.\,]+)",
    ]
    single_patterns = [
        r"r?\$\s*([\d\.\,]+)",
        r"(?:sal[áa]rio|remunera[cç][ãa]o|vencimento|ganho|renda|valor)[:\s]*r?\$?\s*([\d\.\,]+)",
    ]

    def parse_brl_number_local(s: str):
        if not s:
            return None
        s = s.strip()
        if "," in s and "." in s:
            s = s.replace(".", "").replace(",", ".")
        elif "," in s and "." not in s:
            m = re.match(r"^\d{1,3},\d{3}$", s)
            if m:
                s = s.replace(",", "")
            else:
                s = s.replace(",", ".")
        s = re.sub(r"[^0-9\.\-]", "", s)
        try:
            return float(s)
        except ValueError:
            return None

    min_salary = max_salary = None

    # Faixa salarial
    for pat in range_patterns:
        m = re.search(pat, desc_lower, flags=re.IGNORECASE)
        if m:
            v1 = parse_brl_number_local(m.group(1))
            v2 = parse_brl_number_local(m.group(2))
            if v1 is not None and v2 is not None:
                min_salary, max_salary = sorted([v1, v2])
            break

    # Valor único se não achou faixa
    if min_salary is None:
        for pat in single_patterns:
            m = re.search(pat, desc_lower, flags=re.IGNORECASE)
            if m:
                v = parse_brl_number_local(m.group(1))
                if v is not None:
                    min_salary = v
                break

    salary_type = "a combinar"
    if min_salary is not None and max_salary is not None:
        salary_type = "faixa salarial"
    elif min_salary is not None:
        salary_type = "valor mínimo"
    elif re.search(r"a\s*combinar|compat[íi]vel|negoci[áa]vel", desc_lower):
        salary_type = "a combinar"

    return {
        "min_salary": min_salary,
        "max_salary": max_salary,
        "salary_type": salary_type,
        "commission": commission,
        "currency": "BRL",
        "period": period,
    }

def extract_experience_advanced(description):
    """Extrai informações de experiência com padrões mais detalhados"""
    if not description or pd.isna(description):
        return None
    
    desc_lower = str(description).lower()
    
    # Padrões para experiência
    experience_patterns = [
        # Tempo específico
        r'(\d+)\s*anos?\s*de\s*experi[êe]ncia',
        r'experi[êe]ncia\s*de\s*(\d+)\s*anos?',
        r'(\d+)\s*anos?\s*na\s*[áa]rea',
        r'(\d+)\s*anos?\s*na\s*fun[çc][ãa]o',
        r'(\d+)\s*anos?\s*em\s*vendas',
        r'(\d+)\s*anos?\s*como',
        r'm[íi]nimo\s*(\d+)\s*anos?',
        r'pelo\s*menos\s*(\d+)\s*anos?',
        # Experiência geral
        r'experi[êe]ncia\s*em\s*([^.,;]+)',
        r'experi[êe]ncia\s*na\s*[áa]rea\s*de\s*([^.,;]+)',
        r'experi[êe]ncia\s*como\s*([^.,;]+)',
        r'experi[êe]ncia\s*pr[ée]via\s*em\s*([^.,;]+)',
        r'conhecimento\s*em\s*([^.,;]+)',
        r'vivência\s*em\s*([^.,;]+)',
        r'atua[çc][ãa]o\s*em\s*([^.,;]+)',
        # Níveis de experiência
        r'experi[êe]ncia\s*(iniciante|júnior|pleno|sênior|senior)',
        r'n[íi]vel\s*(iniciante|júnior|pleno|sênior|senior)',
        r'profissional\s*(iniciante|júnior|pleno|sênior|senior)',
        # Sem experiência
        r'sem\s*experi[êe]ncia',
        r'n[ãa]o\s*[ée]\s*necess[áa]ria\s*experi[êe]ncia',
        r'primeiro\s*emprego',
        r'aceita\s*iniciantes',
    ]
    
    for pattern in experience_patterns:
        match = re.search(pattern, desc_lower)
        if match:
            if match.groups():
                return match.group(1).strip()
            else:
                return "Experiência requerida"
    
    return None

def extract_responsibilities_advanced(description):
    """Extrai responsabilidades com análise mais robusta e filtro de ruídos"""
    if not description or pd.isna(description):
        return []

    text = str(description)

    # Normalização simples
    text_norm = re.sub(r"[\t\r]+", "\n", text)

    responsibilities = []

    # Padrões para identificar seções de responsabilidades (captura bloco após cabeçalhos)
    responsibility_sections = [
        r"responsabilidades?\s*:?[\s\-]*([\s\S]+?)(?:\n\s*\n|\n\s*(?:requisitos|qualifica[çc][ãa]o|benef[íi]cios|sal[áa]rio)\b|$)",
        r"atividades?\s*:?[\s\-]*([\s\S]+?)(?:\n\s*\n|\n\s*(?:requisitos|qualifica[çc][ãa]o|benef[íi]cios|sal[áa]rio)\b|$)",
        r"fun[çc][õo]es?\s*:?[\s\-]*([\s\S]+?)(?:\n\s*\n|\n\s*(?:requisitos|qualifica[çc][ãa]o|benef[íi]cios|sal[áa]rio)\b|$)",
        r"atribui[çc][õo]es?\s*:?[\s\-]*([\s\S]+?)(?:\n\s*\n|\n\s*(?:requisitos|qualifica[çc][ãa]o|benef[íi]cios|sal[áa]rio)\b|$)",
        r"principais\s*atividades\s*:?[\s\-]*([\s\S]+?)(?:\n\s*\n|\n\s*(?:requisitos|qualifica[çc][ãa]o|benef[íi]cios|sal[áa]rio)\b|$)",
        r"o\s*que\s*voc[êe]\s*far[áa]\s*:?[\s\-]*([\s\S]+?)(?:\n\s*\n|\n\s*(?:requisitos|qualifica[çc][ãa]o|benef[íi]cios|sal[áa]rio)\b|$)",
        r"suas\s*fun[çc][õo]es\s*:?[\s\-]*([\s\S]+?)(?:\n\s*\n|\n\s*(?:requisitos|qualifica[çc][ãa]o|benef[íi]cios|sal[áa]rio)\b|$)",
    ]

    # Verbos de ação para fallback (captura trechos objetivos)
    action_patterns = [
        r"(?:desenvolver|executar|realizar|coordenar|gerenciar|supervisionar|administrar|controlar|organizar|planejar|implementar|monitorar|acompanhar|elaborar|preparar|conduzir|liderar|orientar|apoiar|auxiliar|assessorar|atender|prestar|fornecer|garantir|assegurar|manter|zelar|cuidar|operar|monitorar|configurar)\s+([^\n.;]+)",
        r"(?:ser[áa]\s+respons[áa]vel\s+por|respons[áa]vel\s+por)\s+([^\n.;]+)",
        r"(?:dever[áa]|deve|ir[áa]|precisa|necess[áa]rio|obrigat[óo]rio)\s+([^\n.;]+)",
        r"[•\-*\u2022]\s*([^\n]+)",
        r"\d+[.)]\s*([^\n]+)",
    ]

    # Palavras de ruído para filtrar itens que não são responsabilidades
    noise_keywords = [
        # Remuneração/benefícios
        r"r\$\s*\d", r"sal[áa]ri", r"remunera", r"benef[íi]cio", r"comiss", r"plr", r"fgts", r"13[ºo]", r"vale\s*(?:transporte|refei[çc][ãa]o|alimenta[çc][ãa]o)", r"\bvt\b", r"\bvr\b", r"\bva\b",
        # CTA e navegação
        r"candidatar", r"candidatura", r"enviar\s+curr[ií]culo", r"curr[ií]culo", r"email|e\-?mail|@|http|www|clique|link|contin(uar|ue)\s+lendo",
        # Metadados e outros
        r"vaga\s+(?:publicada|dispon[ií]vel)", r"somos|empresa|sobre\s+a\s+empresa",
        # Requisitos/qualificações
        r"requisitos?|qualifica[çc][ãa]o|experi[êe]ncia\s+(?:m[íi]nima|necess[áa]ria|obrigat[óo]ria)", r"forma[çc][ãa]o|escolaridade|habilidades|conhecimentos|certifica[çc][ãa]o",
    ]
    noise_regex = re.compile(r"(" + r"|".join(noise_keywords) + r")", flags=re.IGNORECASE)

    # Função auxiliar: quebra e limpa uma seção em itens
    def split_section_to_items(section_text: str):
        items = []
        # Divide por linhas e marcadores
        raw_lines = re.split(r"[\n\r]+|[•\-*\u2022]+|\d+[.)]\s*", section_text)
        for line in raw_lines:
            line = re.sub(r"^[•\-*\u2022\d.)\s]+", "", line).strip()
            # Normaliza espaços
            line = re.sub(r"\s+", " ", line)
            if len(line) < 12 or len(line) > 220:
                continue
            if noise_regex.search(line):
                continue
            # Evita frases muito genéricas
            if re.fullmatch(r"respons[áa]vel\s+por", line, flags=re.IGNORECASE):
                continue
            items.append(line)
        return items

    # 1) Busca por blocos de seções nomeadas
    for pat in responsibility_sections:
        m = re.search(pat, text_norm, flags=re.IGNORECASE)
        if m:
            section = m.group(1)
            responsibilities.extend(split_section_to_items(section))

    # 2) Se vazio, usa fallback com verbos de ação e bullets em todo o texto
    if not responsibilities:
        for pat in action_patterns:
            for m in re.findall(pat, text_norm, flags=re.IGNORECASE | re.MULTILINE):
                candidate = m if isinstance(m, str) else m[0]
                candidate = re.sub(r"^[•\-*\u2022\d.)\s]+", "", candidate).strip()
                candidate = re.sub(r"\s+", " ", candidate)
                if len(candidate) < 12 or len(candidate) > 220:
                    continue
                if noise_regex.search(candidate):
                    continue
                responsibilities.append(candidate)

    # 3) Pós-processamento: dedup, corte e retorno
    seen = set()
    cleaned = []
    for item in responsibilities:
        # Remove pontuação final redundante
        item_norm = item.rstrip(" ;-.,")
        if item_norm.lower() not in seen:
            seen.add(item_norm.lower())
            cleaned.append(item_norm)

    return cleaned[:12]  # Limita a 12 responsabilidades

def extract_benefits_advanced(description):
    """Extrai benefícios com padrões mais abrangentes"""
    if not description or pd.isna(description):
        return []
    
    desc_lower = str(description).lower()
    benefits = []
    
    # Dicionário de benefícios com variações
    benefit_patterns = {
        'Vale Alimentação': [r'vale[\s-]*alimenta[çc][ãa]o', r'va[\s]*alimenta[çc][ãa]o', r'cart[ãa]o[\s]*alimenta[çc][ãa]o'],
        'Vale Transporte': [r'vale[\s-]*transporte', r'vt[\s]*transporte', r'cart[ãa]o[\s]*transporte'],
        'Vale Refeição': [r'vale[\s-]*refei[çc][ãa]o', r'vr[\s]*refei[çc][ãa]o', r'cart[ãa]o[\s]*refei[çc][ãa]o'],
        'Plano de Saúde': [r'plano[\s]*de[\s]*sa[úu]de', r'conv[êe]nio[\s]*m[ée]dico', r'assist[êe]ncia[\s]*m[ée]dica'],
        'Plano Odontológico': [r'plano[\s]*odontol[óo]gico', r'conv[êe]nio[\s]*odontol[óo]gico', r'assist[êe]ncia[\s]*odontol[óo]gica'],
        'Seguro de Vida': [r'seguro[\s]*de[\s]*vida', r'seguro[\s]*vida'],
        'Participação nos Lucros': [r'participa[çc][ãa]o[\s]*nos[\s]*lucros', r'plr', r'participa[çc][ãa]o[\s]*lucros'],
        'Décimo Terceiro': [r'd[ée]cimo[\s]*terceiro', r'13[ºo][\s]*sal[áa]rio', r'gratifica[çc][ãa]o[\s]*natalina'],
        'Férias': [r'f[ée]rias[\s]*remuneradas', r'f[ée]rias'],
        'FGTS': [r'fgts', r'fundo[\s]*de[\s]*garantia'],
        'PIS': [r'pis', r'programa[\s]*de[\s]*integra[çc][ãa]o[\s]*social'],
        'Comissão': [r'comiss[ãa]o', r'comissionamento'],
        'Home Office': [r'home[\s]*office', r'trabalho[\s]*remoto', r'trabalho[\s]*em[\s]*casa'],
        'Horário Flexível': [r'hor[áa]rio[\s]*flex[íi]vel', r'flexibilidade[\s]*de[\s]*hor[áa]rio'],
        'Treinamento': [r'treinamento', r'capacita[çc][ãa]o', r'curso[\s]*de[\s]*forma[çc][ãa]o'],
        'Estacionamento': [r'estacionamento', r'vaga[\s]*de[\s]*estacionamento'],
        'Cesta Básica': [r'cesta[\s]*b[áa]sica', r'cesta[\s]*de[\s]*alimentos'],
        'Auxílio Creche': [r'aux[íi]lio[\s]*creche', r'aux[íi]lio[\s]*bab[áa]'],
        'Auxílio Educação': [r'aux[íi]lio[\s]*educa[çc][ãa]o', r'aux[íi]lio[\s]*estudo'],
        'Ginástica Laboral': [r'gin[áa]stica[\s]*laboral', r'atividade[\s]*f[íi]sica'],
        'Refeitório': [r'refeit[óo]rio', r'restaurante[\s]*da[\s]*empresa'],
        'Almoço': [r'almo[çc]o[\s]*gratuito', r'almo[çc]o[\s]*fornecido', r'almo[çc]o'],
        'Lanche': [r'lanche[\s]*gratuito', r'caf[ée][\s]*da[\s]*manh[ãa]', r'lanche'],
        'Uniforme': [r'uniforme[\s]*fornecido', r'uniforme'],
        'Equipamentos': [r'equipamentos[\s]*fornecidos', r'ferramentas[\s]*de[\s]*trabalho'],
    }
    
    # Busca por cada benefício
    for benefit_name, patterns in benefit_patterns.items():
        for pattern in patterns:
            if re.search(pattern, desc_lower):
                benefits.append(benefit_name)
                break
    
    return list(set(benefits))  # Remove duplicatas

def extract_education_and_skills(description):
    """Extrai formação acadêmica e habilidades da descrição"""
    if not description or pd.isna(description):
        return {"education": [], "skills": []}
    
    desc = str(description)
    desc_lower = desc.lower()
    education = []
    skills = set()
    
    # Padrões de formação acadêmica (pt-BR)
    edu_patterns = [
        r'(ensino\s+m[ée]dio\s+(?:completo|incompleto))',
        r'(ensino\s+t[ée]cnico\s+(?:completo|incompleto))',
        r'(ensino\s+superior\s+(?:completo|incompleto))',
        r'(t[ée]cnico\s+em\s+[\wÀ-ÿ\s]+)',
        r'(gradua[çc][ãa]o\s+em\s+[\wÀ-ÿ\s]+)',
        r'(forma[çc][ãa]o\s+em\s+[\wÀ-ÿ\s]+)',
        r'(p[óo]s[-\s]*gradua[çc][ãa]o)',
        r'(especializa[çc][ãa]o)',
        r'(mba)',
        r'(mestrado)',
        r'(doutorado)'
    ]
    for pat in edu_patterns:
        for m in re.findall(pat, desc_lower, flags=re.IGNORECASE):
            val = m if isinstance(m, str) else m[0]
            val = val.strip()
            if val and val not in education:
                education.append(val)
    
    # Padrões de habilidades (hard/soft e ferramentas)
    skill_map = {
        'excel': [r'\bexcel\b', r'pacote\s*office'],
        'word': [r'\bword\b'],
        'power bi': [r'power\s*bi'],
        'sql': [r'\bsql\b'],
        'python': [r'\bpython\b'],
        'java': [r'\bjava\b'],
        'javascript': [r'javascript', r'\bjs\b', r'node\.?js', r'react'],
        'c#': [r'\bc#\b', r'csharp'],
        'git': [r'\bgit\b', r'github', r'gitlab'],
        'linux': [r'linux'],
        'comunicação': [r'comunica[çc][ãa]o'],
        'liderança': [r'lideran[çc]a'],
        'negociação': [r'negocia[çc][ãa]o'],
        'vendas': [r'\bvendas\b'],
        'atendimento ao cliente': [r'atendimento\s+ao\s+cliente'],
        'crm': [r'\bcrm\b'],
        'erp': [r'\berp\b', r'sap'],
        'autocad': [r'autocad'],
        'solidworks': [r'solid\s*works'],
        'marketing digital': [r'marketing\s*digital'],
        'redes sociais': [r'redes\s*sociais'],
        'photoshop': [r'photoshop'],
        'illustrator': [r'illustrator'],
        'powerpoint': [r'power\s*point', r'powerpoint'],
        'inglês': [r'\bingl[êe]s\b'],
        'espanhol': [r'\bespanhol\b']
    }
    for canonical, patterns in skill_map.items():
        for pat in patterns:
            if re.search(pat, desc_lower, flags=re.IGNORECASE):
                skills.add(canonical)
                break
    
    # Seções de requisitos podem conter habilidades adicionais (captura genérica de bullets após "Requisitos")
    req_sections = [
        r'requisitos?[:\s]*([\s\S]{0,400})',
        r'qualifica[çc][õo]es?[:\s]*([\s\S]{0,400})',
        r'conhecimentos?[:\s]*([\s\S]{0,400})'
    ]
    for pat in req_sections:
        m = re.search(pat, desc, flags=re.IGNORECASE)
        if m:
            snippet = m.group(1)
            for canonical, patterns in skill_map.items():
                for sp in patterns:
                    if re.search(sp, snippet, flags=re.IGNORECASE):
                        skills.add(canonical)
                        break
    
    return {"education": education[:5], "skills": sorted(list(skills))[:15]}

def calculate_data_quality_score(job):
    """Calcula score de qualidade dos dados extraídos"""
    score = 0
    
    # Salário (peso 2)
    if job.get('salary', {}).get('min_salary') and job['salary']['salary_type'] != 'a combinar':
        score += 2
    
    # Experiência (peso 1)
    if job.get('experience'):
        score += 1
    
    # Responsabilidades (peso 1)
    if job.get('responsibilities') and len(job['responsibilities']) > 0:
        score += 1
    
    # Benefícios (peso 1)
    if job.get('benefits') and len(job['benefits']) > 0:
        score += 1
    
    # Comissão (peso 0.5)
    if job.get('salary', {}).get('commission'):
        score += 0.5
    
    # Formação (peso 0.5)
    if job.get('education'):
        score += 0.5
    
    # Habilidades (peso 0.5)
    if job.get('skills'):
        score += 0.5
    
    return score

def process_csv_master(csv_file):
    """Processa CSV com extração master de dados"""
    print("🚀 Iniciando extração MASTER de dados...")
    
    # Carrega o CSV
    df = pd.read_csv(csv_file, encoding='utf-8')
    print(f"📊 Total de vagas carregadas: {len(df)}")
    
    jobs_data = []
    stats = {
        'total_jobs': len(df),
        'with_salary': 0,
        'with_commission': 0,
        'with_experience': 0,
        'with_responsibilities': 0,
        'with_benefits': 0,
        'high_quality': 0
    }
    
    for index, row in df.iterrows():
        if index % 1000 == 0:
            print(f"⚡ Processando vaga {index + 1}/{len(df)}...")
        
        # Extrai dados da descrição
        description_raw = row.get('Descrição', '')
        description = clean_description(description_raw)
        
        salary_info = extract_salary_advanced(description)
        experience = extract_experience_advanced(description)
        responsibilities = extract_responsibilities_advanced(description)
        benefits = extract_benefits_advanced(description)
        edu_skills = extract_education_and_skills(description)
        
        # Campos adicionais extraídos da descrição
        location_extracted = extract_location_advanced(description)
        published_date = extract_published_date(description)
        contract_info = extract_contract_type(description)
        
        # Fallbacks e consolidação
        location_csv = row.get('Localidade', '')
        location_final = location_csv if (isinstance(location_csv, str) and location_csv.strip()) else location_extracted
        
        work_type_csv = row.get('Modalidade', '')
        work_type_final = work_type_csv if (isinstance(work_type_csv, str) and work_type_csv.strip()) else contract_info.get('work_model')
        
        # Cria objeto da vaga
        job = {
            'id': index + 1,
            'title': row.get('Título', ''),
            'company': row.get('Empresa', ''),
            'location': location_final,
            'work_type': work_type_final,
            'description': description,
            'description_raw': description_raw,
            'link': row.get('Link', ''),
            'salary': salary_info,
            'experience': experience,
            'responsibilities': responsibilities,
            'benefits': benefits,
            'published_date': published_date,
            'contract_type': contract_info.get('contract_type'),
            'work_model': contract_info.get('work_model'),
            'location_extracted': location_extracted,
            'education': edu_skills.get('education', []),
            'skills': edu_skills.get('skills', []),
            'extraction_timestamp': datetime.now().isoformat()
        }
        
        # Calcula score de qualidade
        quality_score = calculate_data_quality_score(job)
        job['data_quality_score'] = quality_score
        
        # Atualiza estatísticas
        if salary_info['min_salary'] and salary_info['salary_type'] != 'a combinar':
            stats['with_salary'] += 1
        if salary_info['commission']:
            stats['with_commission'] += 1
        if experience:
            stats['with_experience'] += 1
        if responsibilities:
            stats['with_responsibilities'] += 1
        if benefits:
            stats['with_benefits'] += 1
        if quality_score >= 3:
            stats['high_quality'] += 1
        
        jobs_data.append(job)
    
    # Cria estrutura final
    final_data = {
        'metadata': {
            'extraction_date': datetime.now().isoformat(),
            'total_jobs': stats['total_jobs'],
            'extraction_stats': stats,
            'extraction_method': 'master_advanced_extraction',
            'version': '1.0'
        },
        'jobs': jobs_data
    }
    
    # Salva o arquivo JSON
    output_file = 'catho_worker3_master_extraction.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(final_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Extração MASTER concluída!")
    print(f"📁 Arquivo gerado: {output_file}")
    print(f"📊 Estatísticas:")
    print(f"   💰 Salários extraídos: {stats['with_salary']} ({stats['with_salary']/stats['total_jobs']*100:.1f}%)")
    print(f"   💸 Comissões extraídas: {stats['with_commission']} ({stats['with_commission']/stats['total_jobs']*100:.1f}%)")
    print(f"   ⏰ Experiência extraída: {stats['with_experience']} ({stats['with_experience']/stats['total_jobs']*100:.1f}%)")
    print(f"   📋 Responsabilidades: {stats['with_responsibilities']} ({stats['with_responsibilities']/stats['total_jobs']*100:.1f}%)")
    print(f"   🎁 Benefícios: {stats['with_benefits']} ({stats['with_benefits']/stats['total_jobs']*100:.1f}%)")
    print(f"   🌟 Alta qualidade: {stats['high_quality']} ({stats['high_quality']/stats['total_jobs']*100:.1f}%)")
    
    return output_file

if __name__ == "__main__":
    # Processa o arquivo CSV
    csv_file = 'catho_batch_009_vagas_36001-40500.csv'
    process_csv_master(csv_file)