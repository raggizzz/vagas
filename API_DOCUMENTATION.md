# 📚 API de Análise de Vagas e Skills - Documentação

## 🚀 Visão Geral

Esta API fornece endpoints para análise de vagas de emprego e habilidades profissionais baseados em dados reais do Supabase. A API extrai e analisa informações de vagas para identificar tendências de mercado, habilidades mais requisitadas e pontos em comum entre diferentes posições.

## 🔗 URL Base
```
http://localhost:8000
```

## 📋 Endpoints Disponíveis

### 1. **GET /** - Página Inicial
**Descrição:** Retorna informações básicas sobre a API

**Resposta:**
```json
{
  "message": "API de Vagas e Skills",
  "version": "1.0",
  "endpoints": [
    "/jobs",
    "/skills-by-sector"
  ]
}
```

---

### 2. **GET /jobs** - Todas as Vagas
**Descrição:** Retorna todas as vagas exatamente como estão na tabela jobs do banco de dados

**Parâmetros:**
- `limit` (opcional): Número máximo de vagas a retornar (padrão: 100, máximo: 1000)
- `offset` (opcional): Número de registros a pular para paginação (padrão: 0)

**Exemplo de requisição:**
```
GET /jobs?limit=10&offset=0
```

**Resposta:**
```json
{
  "total_jobs": 15,
  "limit": 10,
  "offset": 0,
  "jobs": [
    {
      "id": 1,
      "titulo": "Analista de Dados",
      "empresa": "CANAA TELECOM",
      "localizacao": "Cuiabá, MT",
      "salario": "R$ 3.000,00 - R$ 5.000,00",
      "descricao": "Descrição completa da vaga...",
      "requisitos": "Requisitos da vaga...",
      "habilidades": null,
      "setor": "Informatica",
      "beneficios": "Assistência Médica; Vale Transporte",
      "horario": "Segunda a sexta 08:00 18:00",
      "regime_contratacao": "CLT (Efetivo)",
      "data_publicacao": null,
      "nivel": null,
      "created_at": "2025-09-11T14:28:51.915322+00:00",
      "updated_at": "2025-09-11T14:28:51.915322+00:00"
    }
  ]
}
```

**Códigos de Status:**
- `200`: Sucesso
- `422`: Parâmetros inválidos (limit > 1000)
- `500`: Erro interno do servidor

---

### 3. **GET /skills-by-sector** - Habilidades por Setor (Dados Reais)
**Descrição:** Retorna as habilidades mais requisitadas organizadas por setor, extraídas diretamente das descrições reais das vagas usando análise de texto avançada.

**Funcionalidades:**
- Extração automática de skills técnicas (Python, Java, JavaScript, SQL, etc.)
- Identificação de soft skills (Comunicação, Liderança, etc.)
- Análise de padrões regex para maior precisão
- Filtros de qualidade (mínimo 2 ocorrências por skill, setores com pelo menos 3 vagas)

**Parâmetros:** Nenhum

**Resposta:**
```json
{
  "sectors": [
    {
      "sector": "Informatica",
      "total_jobs": 15,
      "median_salary": null,
      "top_skills": [
        {
          "skill": "Excel",
          "percentage": 46.67
        },
        {
          "skill": "SQL",
          "percentage": 33.33
        }
      ]
    }
  ]
}
```

**Códigos de Status:**
- `200`: Sucesso
- `404`: Nenhuma vaga encontrada
- `500`: Erro interno do servidor

## 🔍 Skills Analisadas

A API identifica automaticamente as seguintes categorias de habilidades:

### 💻 **Tecnologias de Programação**
- Python
- Java
- JavaScript
- SQL
- React

### 🛠️ **Ferramentas e Plataformas**
- Excel
- Power BI
- AWS
- Azure
- Docker
- Git/GitHub/GitLab
- Linux

### 🤝 **Soft Skills**
- Comunicação
- Trabalho em Equipe
- Liderança
- Organização

### 🌐 **Idiomas**
- Inglês

### 📊 **Metodologias**
- Scrum/Agile

## 📊 Estrutura dos Dados

A API analisa os seguintes campos da tabela `jobs`:
- `habilidades`: Habilidades específicas da vaga
- `requisitos`: Requisitos e qualificações necessárias
- `titulo`: Título da vaga
- `setor`: Setor da vaga

## 🚨 Tratamento de Erros

Todos os endpoints retornam erros no formato padrão:

```json
{
  "detail": "Descrição do erro"
}
```

### Códigos de Erro Comuns:
- `404`: Recurso não encontrado
- `422`: Parâmetros inválidos
- `500`: Erro interno do servidor

## 🔧 Como Usar

### Exemplo com cURL:
```bash
# Obter skills por setor
curl http://localhost:8000/skills-by-sector

# Analisar skills comuns com frequência mínima de 3
curl "http://localhost:8000/common-skills?min_frequency=3"

# Obter vagas mais procuradas
curl http://localhost:8000/most-wanted-jobs
```

### Exemplo com PowerShell:
```powershell
# Obter skills comuns
Invoke-RestMethod -Uri "http://localhost:8000/common-skills?min_frequency=2" -Method Get

# Obter skills por setor
Invoke-RestMethod -Uri "http://localhost:8000/skills-by-sector" -Method Get
```

### Exemplo com Python:
```python
import requests

# Analisar skills comuns
response = requests.get("http://localhost:8000/common-skills?min_frequency=3")
data = response.json()

print(f"Total de vagas analisadas: {data['total_jobs_analyzed']}")
for skill in data['common_skills']:
    print(f"{skill['skill']}: {skill['frequency']} vagas ({skill['percentage']}%)")
```

## 🎯 Casos de Uso

1. **Análise de Mercado**: Identificar quais habilidades estão em alta demanda
2. **Planejamento de Carreira**: Descobrir skills essenciais para determinado setor
3. **Recrutamento**: Entender o perfil mais comum de candidatos
4. **Educação**: Adaptar currículos baseados na demanda do mercado

## 📈 Estatísticas Atuais

- **Total de vagas analisadas**: 15
- **Setores disponíveis**: 1 (Informatica)
- **Skills identificadas**: 18 categorias
- **Última atualização**: Dados em tempo real do Supabase

## 🔄 Atualizações

A API consulta dados em tempo real do Supabase, garantindo que as análises sempre reflitam o estado atual da base de dados.

## 📞 Suporte

Para dúvidas ou problemas:
1. Verifique se a API está rodando em `http://localhost:8000`
2. Confirme se as variáveis de ambiente do Supabase estão configuradas
3. Consulte os logs do servidor para detalhes de erros

---

*Documentação gerada automaticamente - Versão 1.0*