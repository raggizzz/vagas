# 🚀 Integração com Supabase - Dados de Vagas Catho

Este projeto integra os dados extraídos das vagas do Catho com o Supabase para estruturação e análise dos dados.

## 📋 Pré-requisitos

- Python 3.8+
- Conta no Supabase (gratuita)
- Dados extraídos pelo `master_extractor.py`

## 🛠️ Configuração

### 1. Criar Projeto no Supabase

1. Acesse [supabase.com](https://supabase.com)
2. Crie uma conta gratuita
3. Clique em "New Project"
4. Escolha uma organização
5. Configure:
   - **Name**: `catho-jobs-data` (ou nome de sua escolha)
   - **Database Password**: Crie uma senha forte
   - **Region**: `South America (São Paulo)` (recomendado)
6. Clique em "Create new project"
7. Aguarde a criação (2-3 minutos)

### 2. Obter Credenciais

No painel do Supabase:

1. Vá em **Settings** → **API**
2. Copie as seguintes informações:
   - **Project URL** (ex: `https://xxxxx.supabase.co`)
   - **anon public** key (chave pública)
   - **service_role** key (chave de serviço - mais permissões)

### 3. Configurar Variáveis de Ambiente

1. Copie o arquivo de exemplo:
   ```bash
   copy .env.example .env
   ```

2. Edite o arquivo `.env` com suas credenciais:
   ```env
   SUPABASE_URL=https://seu-projeto.supabase.co
   SUPABASE_KEY=sua_chave_publica_aqui
   SUPABASE_SERVICE_KEY=sua_chave_de_servico_aqui
   DATABASE_URL=postgresql://postgres:sua_senha@db.seu-projeto.supabase.co:5432/postgres
   ```

### 4. Criar Schema do Banco

1. No painel Supabase, vá em **SQL Editor**
2. Clique em "New query"
3. Copie todo o conteúdo do arquivo `supabase_schema.sql`
4. Cole no editor e clique em "Run"
5. Verifique se todas as tabelas foram criadas em **Table Editor**

## 🚀 Uso

### Teste da Integração

Antes de fazer upload dos dados reais, teste a configuração:

```bash
python test_supabase.py
```

Este script irá:
- ✅ Testar conexão com Supabase
- ✅ Fazer upload de dados de amostra
- ✅ Executar consultas de teste
- ✅ Mostrar estatísticas do banco
- 🧹 Opcionalmente limpar dados de teste

### Upload dos Dados Reais

Após confirmar que os testes passaram:

```bash
python supabase_uploader.py
```

Este script irá:
- 📂 Carregar `catho_worker3_master_extraction.json`
- 🏢 Criar/atualizar empresas
- 👔 Inserir vagas com todos os dados relacionados
- 📊 Mostrar progresso e estatísticas

## 📊 Estrutura do Banco de Dados

### Tabelas Principais

- **`companies`** - Empresas únicas
- **`jobs`** - Vagas principais
- **`job_salaries`** - Informações salariais
- **`job_responsibilities`** - Responsabilidades da vaga
- **`job_benefits`** - Benefícios oferecidos
- **`job_education`** - Requisitos educacionais
- **`job_skills`** - Habilidades necessárias
- **`job_experience`** - Requisitos de experiência

### View Completa

- **`jobs_complete`** - View que une todas as informações

## 📈 Análise dos Dados

### Consultas Úteis

```sql
-- Top 10 empresas com mais vagas
SELECT company_name, COUNT(*) as total_vagas
FROM jobs 
WHERE company_name IS NOT NULL
GROUP BY company_name 
ORDER BY total_vagas DESC 
LIMIT 10;

-- Distribuição salarial
SELECT 
  salary_type,
  COUNT(*) as quantidade,
  AVG(min_salary) as salario_min_medio,
  AVG(max_salary) as salario_max_medio
FROM job_salaries 
GROUP BY salary_type;

-- Vagas por localização
SELECT location, COUNT(*) as total_vagas
FROM jobs 
WHERE location IS NOT NULL
GROUP BY location 
ORDER BY total_vagas DESC 
LIMIT 15;

-- Habilidades mais demandadas
SELECT skill, COUNT(*) as demanda
FROM job_skills 
GROUP BY skill 
ORDER BY demanda DESC 
LIMIT 20;
```

### Dashboard no Supabase

1. Vá em **SQL Editor**
2. Execute as consultas acima
3. Use **Charts** para criar visualizações
4. Salve como **Saved queries** para reutilizar

## 🔧 Troubleshooting

### Erro de Conexão
```
❌ Erro na conexão: Invalid API key
```
**Solução**: Verifique se as credenciais no `.env` estão corretas.

### Erro de Schema
```
❌ relation "jobs" does not exist
```
**Solução**: Execute o arquivo `supabase_schema.sql` no SQL Editor.

### Erro de Permissão
```
❌ insufficient_privilege
```
**Solução**: Use a `service_role` key no lugar da `anon` key.

### Upload Lento
```
⚡ Processando lote muito devagar...
```
**Solução**: 
- Reduza o `batch_size` no código
- Verifique sua conexão de internet
- Use região mais próxima no Supabase

## 📁 Arquivos do Projeto

- `supabase_schema.sql` - Schema completo do banco
- `supabase_uploader.py` - Script principal de upload
- `test_supabase.py` - Testes de integração
- `.env.example` - Exemplo de configuração
- `requirements.txt` - Dependências Python

## 🎯 Próximos Passos

1. **Análise Avançada**: Criar dashboards no Grafana/Metabase
2. **API REST**: Usar a API automática do Supabase
3. **Automação**: Agendar uploads periódicos
4. **Machine Learning**: Análise de tendências salariais
5. **Frontend**: Criar interface web para consultas

## 📞 Suporte

Em caso de problemas:

1. Execute `test_supabase.py` para diagnóstico
2. Verifique logs detalhados nos scripts
3. Consulte documentação do Supabase
4. Verifique se todas as dependências estão instaladas

---

**Desenvolvido para estruturação e análise de dados de vagas do Catho** 🚀