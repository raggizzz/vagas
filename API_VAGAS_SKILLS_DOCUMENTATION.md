# API de Vagas e Skills - Documentação Completa

## 📋 Visão Geral

A **API de Vagas e Skills** é uma API REST desenvolvida em FastAPI que permite consultar vagas de emprego conectadas ao Supabase. A API oferece endpoints para listar vagas, filtrar por critérios específicos e analisar estatísticas de skills por setor.

### ℹ️ Informações Básicas
- **Versão**: 1.0.0
- **Framework**: FastAPI
- **Banco de Dados**: Supabase (PostgreSQL)
- **Porta Padrão**: 8000
- **Host**: 0.0.0.0
- **Arquivo Principal**: `api_vagas_skills.py`

---

## 🔧 Configuração e Instalação

### Variáveis de Ambiente
A API requer as seguintes variáveis de ambiente no arquivo `.env`:

```env
# Configurações obrigatórias do Supabase
SUPABASE_URL=https://sua-url.supabase.co
SUPABASE_SERVICE_KEY=sua_service_role_key_aqui

# Alternativa para a chave (aceita ambas)
SUPABASE_KEY=sua_chave_aqui
```

### Dependências
```txt
fastapi>=0.100.0
supabase>=1.0.0
uvicorn[standard]>=0.23.0
pydantic>=2.0.0
python-dotenv>=1.0.0
```

### Instalação
```bash
# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
cp .env.example .env
# Editar .env com suas credenciais do Supabase

# Executar a API
python api_vagas_skills.py
```

---

## 🗄️ Estrutura do Banco de Dados

### Tabela `vagas`
A API utiliza a tabela `vagas` no Supabase com a seguinte estrutura:

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | integer | ID único da vaga (chave primária) |
| `titulo` | text | Título da vaga |
| `empresa` | text | Nome da empresa |
| `setor` | text | Setor da empresa/vaga |
| `regime_contratacao` | text | Tipo de contratação (CLT, PJ, etc.) |
| `modalidade` | text | Modalidade de trabalho (Presencial, Remoto, Híbrido) |
| `localidade` | text | Localização da vaga |
| `salario` | text | Faixa salarial |
| `descricao` | text | Descrição completa da vaga |
| `habilidades` | text | Habilidades requeridas (separadas por vírgula/ponto-e-vírgula) |
| `requisitos` | text | Requisitos da vaga (separados por vírgula/ponto-e-vírgula) |
| `data_publicacao` | text | Data de publicação da vaga |

---

## 🔗 Endpoints da API

### 1. **GET /** - Informações da API
Retorna informações básicas sobre a API.

**Resposta:**
```json
{
  "message": "API de Vagas conectada ao Supabase",
  "version": "1.0.0",
  "endpoints": ["/jobs", "/jobs-filtered", "/skills-by-sector"]
}
```

---

### 2. **GET /jobs** - Listar Vagas
Lista todas as vagas com paginação.

**Parâmetros de Query:**
- `limit` (int, opcional): Número máximo de vagas a retornar (padrão: 50)
- `offset` (int, opcional): Número de vagas a pular para paginação (padrão: 0)

**Exemplo de Requisição:**
```bash
GET /jobs?limit=10&offset=0
```

**Resposta:**
```json
[
  {
    "id": 1,
    "titulo": "Desenvolvedor Python",
    "empresa": "Tech Company",
    "setor": "Tecnologia",
    "regime_contratacao": "CLT",
    "modalidade": "Remoto",
    "localidade": "São Paulo, SP",
    "salario": "R$ 8.000 - R$ 12.000",
    "descricao": "Desenvolvedor Python sênior...",
    "habilidades": ["Python", "Django", "PostgreSQL"],
    "requisitos": ["3+ anos experiência", "Inglês intermediário"],
    "publicada_em": "2024-01-15"
  }
]
```

---

### 3. **GET /jobs-filtered** - Filtrar Vagas
Filtra vagas por critérios específicos.

**Parâmetros de Query:**
- `setor` (string, opcional): Filtrar por setor
- `localidade` (string, opcional): Filtrar por localidade
- `modalidade` (string, opcional): Filtrar por modalidade de trabalho
- `regime` (string, opcional): Filtrar por regime de contratação
- `limit` (int, opcional): Número máximo de vagas (padrão: 50)

**Exemplo de Requisição:**
```bash
GET /jobs-filtered?setor=Tecnologia&modalidade=Remoto&limit=20
```

**Resposta:**
```json
[
  {
    "id": 1,
    "titulo": "Desenvolvedor Python",
    "empresa": "Tech Company",
    "setor": "Tecnologia",
    "regime_contratacao": "CLT",
    "modalidade": "Remoto",
    "localidade": "São Paulo, SP",
    "salario": "R$ 8.000 - R$ 12.000",
    "descricao": "Desenvolvedor Python sênior...",
    "habilidades": ["Python", "Django", "PostgreSQL"],
    "requisitos": ["3+ anos experiência", "Inglês intermediário"],
    "publicada_em": "2024-01-15"
  }
]
```

---

### 4. **GET /skills-by-sector** - Estatísticas de Skills por Setor
Retorna estatísticas de skills mais demandadas agrupadas por setor.

**Exemplo de Requisição:**
```bash
GET /skills-by-sector
```

**Resposta:**
```json
{
  "sectors": [
    {
      "sector": "Tecnologia",
      "total_jobs": 150,
      "top_skills": [
        {"skill": "Python", "count": 45},
        {"skill": "JavaScript", "count": 38},
        {"skill": "React", "count": 32},
        {"skill": "SQL", "count": 28},
        {"skill": "Docker", "count": 25}
      ]
    },
    {
      "sector": "Saúde",
      "total_jobs": 80,
      "top_skills": [
        {"skill": "Enfermagem", "count": 25},
        {"skill": "Medicina", "count": 20},
        {"skill": "Fisioterapia", "count": 15}
      ]
    }
  ],
  "last_updated": "2024-01-15T10:30:00"
}
```

---

## 📊 Modelos de Dados

### JobResponse
Modelo de resposta para vagas:

```python
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
```

---

## 🛠️ Funções Auxiliares

### parse_skills(job: Dict) -> List[str]
Extrai e processa skills dos campos `habilidades` e `requisitos` de uma vaga.

**Funcionalidade:**
- Separa skills por vírgula, ponto-e-vírgula ou quebra de linha
- Remove duplicatas
- Remove espaços em branco extras

---

## 🚀 Execução da API

### Desenvolvimento
```bash
python api_vagas_skills.py
```

### Produção
```bash
uvicorn api_vagas_skills:app --host 0.0.0.0 --port 8000
```

### Com Reload (Desenvolvimento)
```bash
uvicorn api_vagas_skills:app --host 0.0.0.0 --port 8000 --reload
```

---

## 📝 Exemplos de Uso

### Python (requests)
```python
import requests

# URL base da API
BASE_URL = "http://localhost:8000"

# Listar primeiras 10 vagas
response = requests.get(f"{BASE_URL}/jobs?limit=10")
vagas = response.json()

# Filtrar vagas de tecnologia remotas
response = requests.get(f"{BASE_URL}/jobs-filtered", params={
    "setor": "Tecnologia",
    "modalidade": "Remoto",
    "limit": 20
})
vagas_filtradas = response.json()

# Obter estatísticas de skills por setor
response = requests.get(f"{BASE_URL}/skills-by-sector")
stats = response.json()
```

### JavaScript (fetch)
```javascript
// Listar vagas
const response = await fetch('http://localhost:8000/jobs?limit=10');
const vagas = await response.json();

// Filtrar vagas
const filteredResponse = await fetch(
  'http://localhost:8000/jobs-filtered?setor=Tecnologia&modalidade=Remoto'
);
const vagasFiltradas = await filteredResponse.json();

// Estatísticas de skills
const statsResponse = await fetch('http://localhost:8000/skills-by-sector');
const stats = await statsResponse.json();
```

### cURL
```bash
# Listar vagas
curl "http://localhost:8000/jobs?limit=10"

# Filtrar vagas
curl "http://localhost:8000/jobs-filtered?setor=Tecnologia&modalidade=Remoto"

# Estatísticas de skills
curl "http://localhost:8000/skills-by-sector"
```

---

## ⚠️ Tratamento de Erros

A API retorna erros HTTP padrão:

### Erro 500 - Internal Server Error
```json
{
  "detail": "Erro ao buscar vagas: [mensagem específica]"
}
```

### Possíveis Causas de Erro:
- Credenciais do Supabase inválidas
- Problemas de conectividade com o banco
- Estrutura da tabela `vagas` incompatível
- Dados corrompidos na tabela

---

## 🔒 Segurança

### CORS
A API está configurada com CORS permissivo para desenvolvimento:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**⚠️ Para produção, configure origins específicos:**
```python
allow_origins=["https://seudominio.com", "https://app.seudominio.com"]
```

### Variáveis de Ambiente
- Nunca commite o arquivo `.env`
- Use `SUPABASE_SERVICE_KEY` para operações administrativas
- Mantenha as chaves seguras e rotacione periodicamente

---

## 📈 Performance e Otimização

### Paginação
- Use `limit` e `offset` para paginar resultados
- Limite padrão: 50 vagas por requisição
- Para grandes volumes, considere implementar cursor-based pagination

### Cache
- Considere implementar cache para `/skills-by-sector` (dados menos voláteis)
- Use Redis ou cache em memória para melhor performance

### Índices no Banco
Recomendados para melhor performance:
```sql
CREATE INDEX idx_vagas_setor ON vagas(setor);
CREATE INDEX idx_vagas_modalidade ON vagas(modalidade);
CREATE INDEX idx_vagas_localidade ON vagas(localidade);
CREATE INDEX idx_vagas_regime ON vagas(regime_contratacao);
```

---

## 🧪 Testes

### Teste Manual
Use o arquivo `test_api.py` incluído no projeto:
```bash
python test_api.py
```

### Teste de Endpoints
```python
import requests

def test_api():
    base_url = "http://localhost:8000"
    
    # Teste endpoint raiz
    response = requests.get(f"{base_url}/")
    assert response.status_code == 200
    
    # Teste listar vagas
    response = requests.get(f"{base_url}/jobs?limit=5")
    assert response.status_code == 200
    assert len(response.json()) <= 5
    
    # Teste filtros
    response = requests.get(f"{base_url}/jobs-filtered?limit=5")
    assert response.status_code == 200
    
    # Teste estatísticas
    response = requests.get(f"{base_url}/skills-by-sector")
    assert response.status_code == 200
    assert "sectors" in response.json()

if __name__ == "__main__":
    test_api()
    print("✅ Todos os testes passaram!")
```

---

## 📚 Documentação Interativa

### Swagger UI
Acesse a documentação interativa em:
```
http://localhost:8000/docs
```

### ReDoc
Documentação alternativa em:
```
http://localhost:8000/redoc
```

### OpenAPI Schema
Schema JSON em:
```
http://localhost:8000/openapi.json
```

---

## 🔄 Versionamento e Changelog

### Versão 1.0.0 (Atual)
- ✅ Endpoint para listar vagas com paginação
- ✅ Endpoint para filtrar vagas por múltiplos critérios
- ✅ Endpoint para estatísticas de skills por setor
- ✅ Integração completa com Supabase
- ✅ Tratamento de erros robusto
- ✅ Documentação completa

### Próximas Versões (Roadmap)
- 🔄 Busca textual nas descrições de vagas
- 🔄 Endpoint para vagas por ID específico
- 🔄 Filtros avançados (faixa salarial, data de publicação)
- 🔄 Autenticação e autorização
- 🔄 Rate limiting
- 🔄 Logs estruturados
- 🔄 Métricas e monitoramento

---

## 🆘 Suporte e Troubleshooting

### Problemas Comuns

#### 1. Erro de Conexão com Supabase
```
ValueError: ⚠️ Configure SUPABASE_URL e SUPABASE_SERVICE_KEY nas variáveis de ambiente.
```
**Solução:** Verifique se o arquivo `.env` está configurado corretamente.

#### 2. Tabela 'vagas' não encontrada
```
HTTPException: Erro ao buscar vagas: relation "vagas" does not exist
```
**Solução:** Certifique-se de que a tabela `vagas` existe no Supabase.

#### 3. Permissões insuficientes
```
HTTPException: Erro ao buscar vagas: permission denied
```
**Solução:** Verifique as políticas RLS (Row Level Security) no Supabase.

### Logs e Debug
Para habilitar logs detalhados:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## 📞 Contato e Contribuição

### Estrutura do Projeto
```
├── api_vagas_skills.py          # API principal
├── test_api.py                  # Testes da API
├── requirements.txt             # Dependências
├── .env.example                 # Exemplo de configuração
├── API_VAGAS_SKILLS_DOCUMENTATION.md  # Esta documentação
└── README.md                    # Documentação geral do projeto
```

### Como Contribuir
1. Fork o repositório
2. Crie uma branch para sua feature
3. Implemente as mudanças
4. Adicione testes
5. Atualize a documentação
6. Submeta um Pull Request

---

**📅 Última Atualização:** Janeiro 2024  
**👨‍💻 Desenvolvido com:** FastAPI + Supabase  
**📄 Licença:** MIT