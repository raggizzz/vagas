# 🚀 API de Vagas e Skills

Uma API REST moderna desenvolvida em FastAPI para consulta e análise de vagas de emprego, conectada ao Supabase.

## 📋 Visão Geral

Esta API permite:
- ✅ Listar vagas de emprego com paginação
- 🔍 Filtrar vagas por setor, modalidade, localização e regime
- 📊 Analisar estatísticas de skills por setor
- 🔗 Integração completa com Supabase
- 📚 Documentação interativa (Swagger/ReDoc)

## 🚀 Quick Start

### 1. Instalação Rápida
```bash
# Clone o repositório
git clone <url-do-repositorio>
cd BancoDeDados

# Instalar dependências
pip install fastapi uvicorn supabase python-dotenv

# Configurar ambiente
cp .env.example .env
# Editar .env com suas credenciais do Supabase

# Executar API
python api_vagas_skills.py
```

### 2. Testar API
```bash
# Verificar se está funcionando
curl http://localhost:8000/

# Listar primeiras 10 vagas
curl "http://localhost:8000/jobs?limit=10"

# Filtrar vagas de tecnologia remotas
curl "http://localhost:8000/jobs-filtered?setor=Tecnologia&modalidade=Remoto"
```

### 3. Documentação Interativa
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📁 Estrutura do Projeto

```
BancoDeDados/
├── api_vagas_skills.py              # 🎯 API principal
├── test_api.py                      # 🧪 Testes automatizados
├── exemplos_uso_api.py              # 📝 Exemplos práticos de uso
├── requirements.txt                 # 📦 Dependências
├── .env.example                     # ⚙️ Exemplo de configuração
├── README.md                        # 📖 Este arquivo
├── API_VAGAS_SKILLS_DOCUMENTATION.md # 📚 Documentação técnica completa
├── DEPLOY_GUIDE.md                  # 🚀 Guia de deploy e configuração
└── vagas_para_supabase.json         # 📊 Dados de exemplo
```

## 🔗 Endpoints Principais

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/` | GET | Informações da API |
| `/jobs` | GET | Listar todas as vagas |
| `/jobs-filtered` | GET | Filtrar vagas por critérios |
| `/skills-by-sector` | GET | Estatísticas de skills por setor |

## 📊 Exemplos de Uso

### Python
```python
import requests

# Listar vagas
response = requests.get("http://localhost:8000/jobs?limit=10")
vagas = response.json()

# Filtrar vagas
response = requests.get("http://localhost:8000/jobs-filtered", params={
    "setor": "Tecnologia",
    "modalidade": "Remoto"
})
vagas_filtradas = response.json()
```

### JavaScript
```javascript
// Listar vagas
const response = await fetch('http://localhost:8000/jobs?limit=10');
const vagas = await response.json();

// Filtrar vagas
const filteredResponse = await fetch(
  'http://localhost:8000/jobs-filtered?setor=Tecnologia&modalidade=Remoto'
);
const vagasFiltradas = await filteredResponse.json();
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

## ⚙️ Configuração

### Variáveis de Ambiente (.env)
```env
SUPABASE_URL=https://sua-url.supabase.co
SUPABASE_SERVICE_KEY=sua_service_role_key_aqui
```

### Dependências
- **FastAPI**: Framework web moderno
- **Supabase**: Cliente Python para Supabase
- **Uvicorn**: Servidor ASGI
- **Pydantic**: Validação de dados
- **python-dotenv**: Gerenciamento de variáveis de ambiente

## 🧪 Testes

```bash
# Executar testes automatizados
python test_api.py

# Executar exemplos práticos
python exemplos_uso_api.py
```

## 🚀 Deploy

### Desenvolvimento
```bash
python api_vagas_skills.py
```

### Produção
```bash
uvicorn api_vagas_skills:app --host 0.0.0.0 --port 8000
```

### Docker
```bash
docker build -t api-vagas .
docker run -p 8000:8000 --env-file .env api-vagas
```

## 📚 Documentação Completa

| Documento | Descrição |
|-----------|-----------|
| [📖 API_VAGAS_SKILLS_DOCUMENTATION.md](API_VAGAS_SKILLS_DOCUMENTATION.md) | Documentação técnica completa da API |
| [🚀 DEPLOY_GUIDE.md](DEPLOY_GUIDE.md) | Guia completo de deploy e configuração |
| [📝 exemplos_uso_api.py](exemplos_uso_api.py) | Exemplos práticos em Python e JavaScript |
| [🧪 test_api.py](test_api.py) | Testes automatizados da API |

## 🔧 Funcionalidades

### ✅ Implementado
- [x] Listagem de vagas com paginação
- [x] Filtros por setor, modalidade, localização e regime
- [x] Estatísticas de skills por setor
- [x] Integração com Supabase
- [x] Documentação interativa (Swagger/ReDoc)
- [x] Tratamento de erros robusto
- [x] Exemplos de uso em múltiplas linguagens
- [x] Testes automatizados
- [x] Guia de deploy completo

### 🔄 Roadmap
- [ ] Busca textual nas descrições
- [ ] Endpoint para vaga específica por ID
- [ ] Filtros avançados (faixa salarial, data)
- [ ] Autenticação e autorização
- [ ] Rate limiting
- [ ] Cache para performance
- [ ] Métricas e monitoramento

## 🛠️ Tecnologias

- **Backend**: FastAPI + Python 3.8+
- **Banco de Dados**: Supabase (PostgreSQL)
- **Servidor**: Uvicorn
- **Documentação**: Swagger UI + ReDoc
- **Deploy**: Docker, Heroku, Railway, DigitalOcean

## 📊 Estrutura do Banco

### Tabela `vagas`
| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | integer | ID único da vaga |
| `titulo` | text | Título da vaga |
| `empresa` | text | Nome da empresa |
| `setor` | text | Setor da empresa |
| `modalidade` | text | Modalidade (Remoto/Presencial/Híbrido) |
| `localidade` | text | Localização da vaga |
| `salario` | text | Faixa salarial |
| `habilidades` | text | Skills requeridas |
| `requisitos` | text | Requisitos da vaga |

## 🔒 Segurança

- ✅ Validação de entrada com Pydantic
- ✅ Tratamento de erros seguro
- ✅ Configuração CORS adequada
- ⚠️ **Produção**: Configure origins específicos no CORS
- ⚠️ **Produção**: Use HTTPS com certificados SSL

## 📈 Performance

- **Paginação**: Limite padrão de 50 vagas por requisição
- **Índices**: Recomendados para campos de filtro
- **Cache**: Considere implementar para `/skills-by-sector`
- **Monitoramento**: Health checks e métricas disponíveis

## 🆘 Suporte

### Problemas Comuns
1. **API não inicia**: Verifique configuração do `.env`
2. **Erro de conexão**: Teste credenciais do Supabase
3. **Performance lenta**: Verifique índices no banco

### Recursos
- **Issues**: Criar issue no repositório
- **Documentação**: Consulte os arquivos `.md`
- **Exemplos**: Execute `exemplos_uso_api.py`

## 🤝 Contribuição

1. Fork o repositório
2. Crie uma branch para sua feature
3. Implemente as mudanças
4. Adicione testes
5. Atualize a documentação
6. Submeta um Pull Request

## 📄 Licença

MIT License - veja o arquivo LICENSE para detalhes.

---

## 🎯 Links Rápidos

- **🌐 API Local**: http://localhost:8000
- **📖 Swagger UI**: http://localhost:8000/docs
- **📚 ReDoc**: http://localhost:8000/redoc
- **🔧 Health Check**: http://localhost:8000/health (se implementado)

---

**📅 Última Atualização:** Janeiro 2024  
**👨‍💻 Desenvolvido com:** FastAPI + Supabase  
**🚀 Status:** Produção Ready  
**📋 Versão:** 1.0.0