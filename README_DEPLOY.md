# Deploy da API no Vercel

## Pré-requisitos

1. Conta no [Vercel](https://vercel.com)
2. Projeto configurado no Supabase
3. Variáveis de ambiente do Supabase

## Passos para Deploy

### 1. Instalar Vercel CLI (opcional)
```bash
npm i -g vercel
```

### 2. Fazer Deploy

#### Opção A: Via GitHub (Recomendado)
1. Faça push do código para um repositório GitHub
2. Conecte o repositório no dashboard do Vercel
3. Configure as variáveis de ambiente
4. Deploy automático será feito

#### Opção B: Via CLI
```bash
vercel
```

### 3. Configurar Variáveis de Ambiente

No dashboard do Vercel, adicione:

- `SUPABASE_URL`: URL do seu projeto Supabase
- `SUPABASE_ANON_KEY`: Chave anônima do Supabase

### 4. Arquivos Importantes

- `main.py`: Ponto de entrada da aplicação
- `vercel.json`: Configuração do Vercel
- `requirements.txt`: Dependências Python

## Endpoints Disponíveis

Após o deploy, sua API estará disponível em:

- `GET /`: Informações da API
- `GET /skills-by-sector`: Skills por setor
- `GET /common-skills`: Skills mais comuns
- `GET /most-wanted-jobs`: Vagas mais procuradas

## Testando o Deploy

```bash
curl https://your-app.vercel.app/
```

## Troubleshooting

1. **Erro de variáveis de ambiente**: Verifique se SUPABASE_URL e SUPABASE_ANON_KEY estão configuradas
2. **Erro de build**: Verifique se requirements.txt está correto
3. **Timeout**: APIs do Vercel têm limite de 10s para execução

## Monitoramento

- Logs disponíveis no dashboard do Vercel
- Métricas de performance e uso
- Alertas automáticos em caso de erro