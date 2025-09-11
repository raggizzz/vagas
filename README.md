# API de Vagas e Skills

API para análise de vagas de emprego e extração de habilidades reais organizadas por setor.

## 🚀 Funcionalidades

- **Listagem de Vagas**: Acesso completo aos dados das vagas sem modificações
- **Análise de Skills por Setor**: Extração automática de habilidades técnicas e soft skills das descrições reais das vagas
- **Análise Avançada**: Uso de regex patterns para identificação precisa de tecnologias e competências
- **Filtros de Qualidade**: Apenas skills com pelo menos 2 ocorrências e setores com mínimo de 3 vagas

## 📋 Endpoints

### `GET /`
Informações básicas da API e lista de endpoints disponíveis.

### `GET /jobs`
Retorna todas as vagas da base de dados.

**Parâmetros:**
- `limit` (opcional): Número máximo de vagas (padrão: 100)
- `offset` (opcional): Número de vagas a pular (padrão: 0)

### `GET /skills-by-sector`
Retorna habilidades mais requisitadas organizadas por setor, extraídas automaticamente das descrições reais das vagas.

**Funcionalidades:**
- Extração de skills técnicas (Python, Java, JavaScript, SQL, etc.)
- Identificação de soft skills (Comunicação, Liderança, etc.)
- Análise com padrões regex para maior precisão
- Filtros de qualidade automáticos

## 🛠️ Tecnologias

- **FastAPI**: Framework web moderno e rápido
- **Supabase**: Base de dados PostgreSQL
- **Pydantic**: Validação de dados
- **Uvicorn/Gunicorn**: Servidor ASGI para produção

## 📦 Instalação Local

1. Clone o repositório:
```bash
git clone https://github.com/SEU_USUARIO/vagas-skills-api.git
cd vagas-skills-api
```

2. Instale as dependências:
```bash
# Para desenvolvimento local
pip install -r requirements.txt

# Para deploy (se houver problemas de compilação)
pip install -r requirements-simple.txt
```

3. Configure as variáveis de ambiente:
```bash
cp .env.example .env
# Edite o arquivo .env com suas credenciais do Supabase
```

4. Execute a API:
```bash
python api_vagas_skills.py
```

A API estará disponível em `http://localhost:8000`

## 🚀 Deploy

### Heroku

1. Crie uma conta no [Heroku](https://heroku.com)
2. Instale o [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)
3. Faça login no Heroku:
```bash
heroku login
```

4. Crie uma nova aplicação:
```bash
heroku create nome-da-sua-app
```

5. Configure as variáveis de ambiente:
```bash
heroku config:set SUPABASE_URL=sua_url_supabase
heroku config:set SUPABASE_KEY=sua_chave_supabase
```

6. Faça o deploy:
```bash
git add .
git commit -m "Deploy inicial"
git push heroku main
```

### Railway

1. Conecte seu repositório GitHub ao [Railway](https://railway.app)
2. Configure as variáveis de ambiente no painel do Railway
3. O deploy será automático a cada push

### Render

1. Conecte seu repositório ao [Render](https://render.com)
2. Configure o serviço web com:
   - **Build Command**: `pip install -r requirements-ultra-simple.txt` (RECOMENDADO)
   - **Start Command**: `gunicorn api_vagas_skills:app --bind 0.0.0.0:$PORT`
3. Configure as variáveis de ambiente

⚠️ **Troubleshooting Deploy:**

**Erro de Compilação pydantic-core no Render:**
- **Causa:** Sistema de arquivos somente leitura impede compilação de dependências Rust
- **Solução 1:** `requirements-simple.txt` (versões modernas com wheels)
- **Solução 2:** `requirements-minimal.txt` (versões mais antigas)
- **Solução 3 (RECOMENDADA - USE ESTA):** `requirements-ultra-simple.txt` (sem dependências Rust - Pydantic 1.x)
  - Esta é a solução definitiva para o erro de compilação Rust
- **Build Command:** `pip install -r requirements-ultra-simple.txt`
- **Start Command:** `gunicorn api_vagas_skills:app --bind 0.0.0.0:$PORT`
- **Arquivos disponíveis (em ordem de compatibilidade):**
  - `requirements-ultra-simple.txt`: **RECOMENDADO** - Pydantic 1.10.12 (sem Rust)
  - `requirements-simple.txt`: Pydantic 2.0.3 (pode falhar)
  - `requirements-minimal.txt`: Versões alternativas

## 🔧 Configuração

### Variáveis de Ambiente

Crie um arquivo `.env` com:

```env
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_KEY=sua-chave-publica-supabase
```

### Estrutura da Base de Dados

A API espera uma tabela `jobs` com as seguintes colunas:
- `id`: Identificador único
- `titulo`: Título da vaga
- `descricao`: Descrição completa
- `setor`: Setor da vaga
- `requisitos`: Requisitos da vaga
- `habilidades`: Habilidades necessárias
- `beneficios`: Benefícios oferecidos
- `horario`: Horário de trabalho
- `regime_contratacao`: Tipo de contratação
- `created_at`: Data de criação
- `updated_at`: Data de atualização

## 📊 Exemplo de Resposta

### Skills por Setor
```json
{
  "sectors": [
    {
      "sector": "Tecnologia",
      "total_jobs": 45,
      "average_salary": null,
      "top_skills": [
        {
          "skill": "Python",
          "percentage": 67.5,
          "job_count": 30
        },
        {
          "skill": "JavaScript",
          "percentage": 45.2,
          "job_count": 20
        }
      ]
    }
  ],
  "total_jobs_analyzed": 150,
  "last_updated": "2024-01-15T14:30:00"
}
```

## 🤝 Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 📞 Contato

Seu Nome - seu.email@exemplo.com

Link do Projeto: [https://github.com/SEU_USUARIO/vagas-skills-api](https://github.com/SEU_USUARIO/vagas-skills-api)