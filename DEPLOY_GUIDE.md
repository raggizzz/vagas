# 🚀 Guia de Deploy e Configuração - API de Vagas e Skills

Este guia fornece instruções detalhadas para fazer o deploy da API de Vagas e Skills em diferentes ambientes.

## 📋 Índice

1. [Pré-requisitos](#pré-requisitos)
2. [Configuração Local](#configuração-local)
3. [Deploy em Produção](#deploy-em-produção)
4. [Deploy com Docker](#deploy-com-docker)
5. [Deploy na Nuvem](#deploy-na-nuvem)
6. [Monitoramento e Logs](#monitoramento-e-logs)
7. [Backup e Recuperação](#backup-e-recuperação)
8. [Troubleshooting](#troubleshooting)

---

## 🔧 Pré-requisitos

### Sistema Operacional
- **Linux**: Ubuntu 20.04+ (recomendado)
- **Windows**: Windows 10/11 com WSL2
- **macOS**: macOS 10.15+

### Software Necessário
- **Python**: 3.8+ (recomendado 3.11+)
- **pip**: Gerenciador de pacotes Python
- **Git**: Para controle de versão
- **Supabase**: Conta ativa com projeto configurado

### Hardware Mínimo
- **RAM**: 512MB (recomendado 1GB+)
- **CPU**: 1 core (recomendado 2+ cores)
- **Armazenamento**: 1GB livre
- **Rede**: Conexão estável com internet

---

## 🏠 Configuração Local

### 1. Clone do Repositório
```bash
# Clone o repositório
git clone <url-do-repositorio>
cd BancoDeDados

# Ou se já tem os arquivos localmente
cd c:\Users\nuxay\Documents\BancoDeDados
```

### 2. Ambiente Virtual Python
```bash
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate
```

### 3. Instalação de Dependências
```bash
# Instalar dependências
pip install -r requirements.txt

# Ou instalar manualmente
pip install fastapi uvicorn supabase python-dotenv pydantic
```

### 4. Configuração do Ambiente
```bash
# Copiar arquivo de exemplo
cp .env.example .env

# Editar arquivo .env
nano .env  # ou use seu editor preferido
```

**Conteúdo do arquivo `.env`:**
```env
# Configurações obrigatórias do Supabase
SUPABASE_URL=https://sua-url.supabase.co
SUPABASE_SERVICE_KEY=sua_service_role_key_aqui

# Configurações opcionais
SUPABASE_KEY=sua_chave_aqui
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=false
```

### 5. Verificação da Configuração
```bash
# Testar conexão com Supabase
python -c "
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_SERVICE_KEY')

if url and key:
    client = create_client(url, key)
    print('✅ Conexão com Supabase OK')
else:
    print('❌ Configuração do Supabase incompleta')
"
```

### 6. Executar Localmente
```bash
# Executar API
python api_vagas_skills.py

# Ou usando uvicorn diretamente
uvicorn api_vagas_skills:app --host 0.0.0.0 --port 8000 --reload
```

### 7. Testar API
```bash
# Testar endpoint básico
curl http://localhost:8000/

# Executar testes automatizados
python test_api.py

# Executar exemplos
python exemplos_uso_api.py
```

---

## 🌐 Deploy em Produção

### 1. Servidor Linux (Ubuntu)

#### Preparação do Servidor
```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Python e dependências
sudo apt install python3 python3-pip python3-venv nginx supervisor -y

# Criar usuário para a aplicação
sudo useradd -m -s /bin/bash apiuser
sudo su - apiuser
```

#### Deploy da Aplicação
```bash
# Como usuário apiuser
cd /home/apiuser

# Clone do projeto
git clone <url-do-repositorio> api-vagas
cd api-vagas

# Ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Configurar ambiente
cp .env.example .env
nano .env  # Configurar com dados de produção
```

#### Configuração do Supervisor
```bash
# Criar arquivo de configuração do supervisor
sudo nano /etc/supervisor/conf.d/api-vagas.conf
```

**Conteúdo do arquivo:**
```ini
[program:api-vagas]
command=/home/apiuser/api-vagas/venv/bin/uvicorn api_vagas_skills:app --host 127.0.0.1 --port 8000
directory=/home/apiuser/api-vagas
user=apiuser
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/api-vagas.log
environment=PATH="/home/apiuser/api-vagas/venv/bin"
```

```bash
# Recarregar supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start api-vagas

# Verificar status
sudo supervisorctl status api-vagas
```

#### Configuração do Nginx
```bash
# Criar configuração do Nginx
sudo nano /etc/nginx/sites-available/api-vagas
```

**Conteúdo do arquivo:**
```nginx
server {
    listen 80;
    server_name seu-dominio.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Logs
    access_log /var/log/nginx/api-vagas-access.log;
    error_log /var/log/nginx/api-vagas-error.log;
}
```

```bash
# Ativar site
sudo ln -s /etc/nginx/sites-available/api-vagas /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

#### SSL com Let's Encrypt
```bash
# Instalar Certbot
sudo apt install certbot python3-certbot-nginx -y

# Obter certificado SSL
sudo certbot --nginx -d seu-dominio.com

# Verificar renovação automática
sudo certbot renew --dry-run
```

### 2. Configuração de Firewall
```bash
# Configurar UFW
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw enable
sudo ufw status
```

---

## 🐳 Deploy com Docker

### 1. Dockerfile
```dockerfile
# Criar Dockerfile
FROM python:3.11-slim

# Definir diretório de trabalho
WORKDIR /app

# Copiar arquivos de dependências
COPY requirements.txt .

# Instalar dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY . .

# Expor porta
EXPOSE 8000

# Comando para executar a aplicação
CMD ["uvicorn", "api_vagas_skills:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2. Docker Compose
```yaml
# docker-compose.yml
version: '3.8'

services:
  api-vagas:
    build: .
    ports:
      - "8000:8000"
    environment:
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_SERVICE_KEY=${SUPABASE_SERVICE_KEY}
    env_file:
      - .env
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - api-vagas
    restart: unless-stopped
```

### 3. Comandos Docker
```bash
# Build da imagem
docker build -t api-vagas .

# Executar container
docker run -d --name api-vagas -p 8000:8000 --env-file .env api-vagas

# Usando Docker Compose
docker-compose up -d

# Verificar logs
docker-compose logs -f api-vagas

# Parar serviços
docker-compose down
```

---

## ☁️ Deploy na Nuvem

### 1. Heroku

#### Preparação
```bash
# Instalar Heroku CLI
# Seguir instruções em: https://devcenter.heroku.com/articles/heroku-cli

# Login no Heroku
heroku login
```

#### Arquivos Necessários
**Procfile:**
```
web: uvicorn api_vagas_skills:app --host 0.0.0.0 --port $PORT
```

**runtime.txt:**
```
python-3.11.0
```

#### Deploy
```bash
# Criar app no Heroku
heroku create nome-da-sua-api

# Configurar variáveis de ambiente
heroku config:set SUPABASE_URL=https://sua-url.supabase.co
heroku config:set SUPABASE_SERVICE_KEY=sua_service_role_key

# Deploy
git add .
git commit -m "Deploy inicial"
git push heroku main

# Verificar logs
heroku logs --tail
```

### 2. Railway

#### Deploy
```bash
# Instalar Railway CLI
npm install -g @railway/cli

# Login
railway login

# Inicializar projeto
railway init

# Deploy
railway up

# Configurar variáveis
railway variables set SUPABASE_URL=https://sua-url.supabase.co
railway variables set SUPABASE_SERVICE_KEY=sua_service_role_key
```

### 3. DigitalOcean App Platform

#### Configuração (app.yaml)
```yaml
name: api-vagas-skills
services:
- name: api
  source_dir: /
  github:
    repo: seu-usuario/seu-repositorio
    branch: main
  run_command: uvicorn api_vagas_skills:app --host 0.0.0.0 --port $PORT
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
  envs:
  - key: SUPABASE_URL
    value: https://sua-url.supabase.co
  - key: SUPABASE_SERVICE_KEY
    value: sua_service_role_key
    type: SECRET
  http_port: 8000
```

### 4. AWS EC2

#### Configuração Básica
```bash
# Conectar à instância EC2
ssh -i sua-chave.pem ubuntu@ip-da-instancia

# Seguir passos de "Deploy em Produção" para Ubuntu
# Configurar Security Groups para permitir tráfego HTTP/HTTPS
```

---

## 📊 Monitoramento e Logs

### 1. Configuração de Logs

#### Logs Estruturados
```python
# logging_config.py
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        return json.dumps(log_entry)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    handlers=[
        logging.FileHandler("api.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
handler = logging.FileHandler("api.log")
handler.setFormatter(JSONFormatter())
logger.addHandler(handler)
```

### 2. Health Checks
```python
# Adicionar ao api_vagas_skills.py
@app.get("/health")
async def health_check():
    """Endpoint de health check"""
    try:
        # Testar conexão com Supabase
        response = supabase.table("vagas").select("id").limit(1).execute()
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "database": "connected",
            "version": "1.0.0"
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Service unhealthy: {str(e)}"
        )
```

### 3. Métricas com Prometheus
```python
# metrics.py
from prometheus_client import Counter, Histogram, generate_latest
import time

# Métricas
REQUEST_COUNT = Counter('api_requests_total', 'Total API requests', ['method', 'endpoint'])
REQUEST_DURATION = Histogram('api_request_duration_seconds', 'Request duration')

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    # Registrar métricas
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path
    ).inc()
    
    REQUEST_DURATION.observe(time.time() - start_time)
    
    return response

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

---

## 💾 Backup e Recuperação

### 1. Backup do Supabase
```bash
# Script de backup
#!/bin/bash
# backup_supabase.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"
SUPABASE_PROJECT_ID="seu-project-id"

# Criar diretório de backup
mkdir -p $BACKUP_DIR

# Backup via API (se disponível)
curl -X GET \
  "https://api.supabase.com/v1/projects/$SUPABASE_PROJECT_ID/database/backup" \
  -H "Authorization: Bearer $SUPABASE_ACCESS_TOKEN" \
  -o "$BACKUP_DIR/backup_$DATE.sql"

echo "Backup criado: $BACKUP_DIR/backup_$DATE.sql"
```

### 2. Backup da Aplicação
```bash
#!/bin/bash
# backup_app.sh

DATE=$(date +%Y%m%d_%H%M%S)
APP_DIR="/home/apiuser/api-vagas"
BACKUP_DIR="/backups/app"

mkdir -p $BACKUP_DIR

# Backup do código
tar -czf "$BACKUP_DIR/app_$DATE.tar.gz" \
  --exclude="venv" \
  --exclude="__pycache__" \
  --exclude=".git" \
  $APP_DIR

echo "Backup da aplicação criado: $BACKUP_DIR/app_$DATE.tar.gz"
```

### 3. Automação com Cron
```bash
# Editar crontab
crontab -e

# Adicionar linhas para backup automático
# Backup diário às 2:00 AM
0 2 * * * /home/apiuser/scripts/backup_app.sh

# Backup semanal do banco às 3:00 AM de domingo
0 3 * * 0 /home/apiuser/scripts/backup_supabase.sh
```

---

## 🔧 Troubleshooting

### 1. Problemas Comuns

#### API não inicia
```bash
# Verificar logs
tail -f /var/log/api-vagas.log

# Verificar processo
ps aux | grep uvicorn

# Verificar porta
netstat -tlnp | grep 8000

# Testar configuração
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
print('SUPABASE_URL:', os.getenv('SUPABASE_URL'))
print('SUPABASE_SERVICE_KEY:', 'Configurada' if os.getenv('SUPABASE_SERVICE_KEY') else 'Não configurada')
"
```

#### Erro de conexão com Supabase
```bash
# Testar conectividade
curl -I https://sua-url.supabase.co

# Verificar chaves
python -c "
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()
url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_SERVICE_KEY')

try:
    client = create_client(url, key)
    result = client.table('vagas').select('id').limit(1).execute()
    print('✅ Conexão OK')
except Exception as e:
    print(f'❌ Erro: {e}')
"
```

#### Performance lenta
```bash
# Verificar recursos do sistema
htop
df -h
free -m

# Verificar logs de erro
grep -i error /var/log/api-vagas.log

# Monitorar requisições
tail -f /var/log/nginx/api-vagas-access.log
```

### 2. Scripts de Diagnóstico

#### Script de Verificação Completa
```bash
#!/bin/bash
# diagnostico.sh

echo "🔍 Diagnóstico da API de Vagas e Skills"
echo "======================================"

# Verificar serviços
echo "📋 Status dos Serviços:"
sudo systemctl status nginx
sudo supervisorctl status api-vagas

# Verificar conectividade
echo "🌐 Teste de Conectividade:"
curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/ && echo " - API Local: OK" || echo " - API Local: ERRO"

# Verificar logs recentes
echo "📝 Logs Recentes:"
tail -n 5 /var/log/api-vagas.log

# Verificar recursos
echo "💻 Recursos do Sistema:"
echo "  CPU: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | awk -F'%' '{print $1}')% usado"
echo "  RAM: $(free | grep Mem | awk '{printf "%.1f%%", $3/$2 * 100.0}')"
echo "  Disco: $(df -h / | awk 'NR==2{printf "%s", $5}')"

echo "✅ Diagnóstico concluído"
```

### 3. Comandos Úteis

#### Reiniciar Serviços
```bash
# Reiniciar API
sudo supervisorctl restart api-vagas

# Reiniciar Nginx
sudo systemctl restart nginx

# Reiniciar tudo
sudo supervisorctl restart all
sudo systemctl restart nginx
```

#### Verificar Logs
```bash
# Logs da API
tail -f /var/log/api-vagas.log

# Logs do Nginx
tail -f /var/log/nginx/api-vagas-access.log
tail -f /var/log/nginx/api-vagas-error.log

# Logs do sistema
journalctl -u nginx -f
```

#### Atualizar Aplicação
```bash
# Como usuário apiuser
cd /home/apiuser/api-vagas
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
sudo supervisorctl restart api-vagas
```

---

## 🚨 Troubleshooting - Problemas Comuns

### ❌ Erro de Rust/Pydantic no Render

**Erro:**
```
error: failed to create directory `/usr/local/cargo/registry/cache/index.crates.io-1949cf8c6b5b557f`
Caused by: Read-only file system (os error 30)
💥 maturin failed
```

**Causa:** Pydantic v2 usa dependências Rust que não conseguem ser compiladas em sistemas de arquivos somente leitura do Render.

**✅ Solução:**

1. **Use o arquivo de requirements COM SUPABASE:**
```bash
# No Render Dashboard, configure:
Build Command: pip install -r requirements-render-supabase.txt
Start Command: uvicorn api_vagas_skills:app --host 0.0.0.0 --port $PORT
```

**🔄 Alternativa se ainda der erro:**
```bash
# Use a versão ultra-simples:
Build Command: pip install -r requirements-render-ultra-simple.txt
Start Command: uvicorn api_vagas_skills:app --host 0.0.0.0 --port $PORT
```

2. **Ou use o arquivo render.yaml automático:**
```yaml
# render.yaml (já criado no projeto)
services:
  - type: web
    name: api-vagas-skills
    env: python
    buildCommand: pip install -r requirements-render-supabase.txt
    startCommand: gunicorn api_vagas_skills:app --bind 0.0.0.0:$PORT
    envVars:
      - key: SUPABASE_URL
        sync: false
      - key: SUPABASE_SERVICE_KEY
        sync: false
```

3. **Configurar variáveis de ambiente no Render:**
   - `SUPABASE_URL`: https://sua-url.supabase.co
   - `SUPABASE_SERVICE_KEY`: sua_service_role_key

**📋 Arquivos de Requirements Disponíveis:**
- `requirements.txt`: Versão completa (desenvolvimento local)
- `requirements-render-supabase.txt`: **🔥 USE ESTE para Render** (COM Supabase, sem Rust)
- `requirements-render-ultra-simple.txt`: **🚨 BACKUP GARANTIDO** (versões antigas mas funcionais)
- `requirements-render-fixed.txt`: Alternativa (pode ter conflitos)
- `requirements-render-simple.txt`: Alternativa sem Supabase SDK
- `requirements-render-minimal.txt`: Versão ultra-mínima
- `requirements-render.txt`: ❌ Versão antiga (conflitos)
- `requirements-simple.txt`: Alternativa simples
- `requirements-minimal.txt`: Versão mínima

### ❌ Erro de Conflito de Dependências

**Erro:**
```
ERROR: Cannot install -r requirements-render.txt (line 5), pydantic==1.10.12 and supabase because these package versions have conflicting dependencies.
The conflict is caused by:
    The user requested pydantic==1.10.12
    fastapi 0.68.0 depends on pydantic!=1.7, !=1.7.1, !=1.7.2, !=1.7.3, !=1.8, !=1.8.1, <2.0.0 and >=1.6.2
    gotrue 1.0.3 depends on pydantic<3.0 and >=2.1
```

**Causa:** Conflito entre versões do Pydantic - Supabase 2.x requer Pydantic 2.x, mas o arquivo antigo usava Pydantic 1.x. <mcreference link="https://pip.pypa.io/en/latest/topics/dependency-resolution/#dealing-with-dependency-conflicts" index="0">0</mcreference>

**✅ Solução:**
```bash
# Use o arquivo CORRIGIDO:
Build Command: pip install -r requirements-render-fixed.txt
```

**Alternativa se ainda houver problemas:**
```bash
# Use a versão simples sem Supabase SDK:
Build Command: pip install -r requirements-render-simple.txt
```

### ❌ Outros Problemas Comuns

#### 1. **Erro de Módulo Não Encontrado**
```bash
ModuleNotFoundError: No module named 'fastapi'
```
**Solução:** Verificar se o arquivo de requirements está correto e todas as dependências estão listadas.

#### 2. **Erro de Conexão com Supabase**
```bash
HTTPException: 401 Unauthorized
```
**Solução:** 
- Verificar se `SUPABASE_URL` e `SUPABASE_SERVICE_KEY` estão configurados
- Usar `SUPABASE_SERVICE_KEY` (não a chave pública)

#### 3. **Erro de Porta**
```bash
Error: [Errno 98] Address already in use
```
**Solução:** 
- Usar `$PORT` no comando de start
- Configurar `--bind 0.0.0.0:$PORT` no gunicorn

#### 4. **Timeout de Build**
**Solução:** 
- Usar `requirements-render.txt` (mais rápido)
- Remover dependências desnecessárias

### 🔧 Comandos de Debug

```bash
# Testar localmente com as mesmas dependências do Render
pip install -r requirements-render.txt
python api_vagas_skills.py

# Verificar se a API responde
curl http://localhost:8000/

# Testar conexão com Supabase
python -c "
import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()
url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_SERVICE_KEY')

if url and key:
    client = create_client(url, key)
    print('✅ Conexão OK')
else:
    print('❌ Configuração incompleta')
"
```

---

## 📞 Suporte

### Contatos
- **Documentação**: `API_VAGAS_SKILLS_DOCUMENTATION.md`
- **Exemplos**: `exemplos_uso_api.py`
- **Issues**: Criar issue no repositório

### Recursos Adicionais
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **Supabase Docs**: https://supabase.com/docs
- **Uvicorn Docs**: https://www.uvicorn.org/

---

**📅 Última Atualização:** Janeiro 2024  
**🔧 Versão do Guia:** 1.0.0  
**📋 Status:** Produção Ready