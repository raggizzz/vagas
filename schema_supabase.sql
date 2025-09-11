
-- Schema SQL para criar a tabela 'vagas' no Supabase

CREATE TABLE IF NOT EXISTS vagas (
    id BIGINT PRIMARY KEY,
    setor TEXT,
    empresa_principal TEXT,
    titulo_vaga TEXT,
    modalidade TEXT,
    nivel_experiencia TEXT,
    tipo_contrato TEXT,
    salario_informado TEXT,
    beneficios JSONB,
    
    -- Localização
    estado TEXT,
    cidade_extraida TEXT,
    regiao TEXT,
    localizacao_completa TEXT,
    
    -- Descrição
    texto_completo TEXT,
    responsabilidades JSONB,
    habilidades_requeridas JSONB,
    empresas_mencionadas JSONB,
    
    -- Metadados
    data_upload TIMESTAMP DEFAULT NOW(),
    versao_dados TEXT,
    
    -- Índices para consultas rápidas
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Índices para melhor performance
CREATE INDEX IF NOT EXISTS idx_vagas_setor ON vagas(setor);
CREATE INDEX IF NOT EXISTS idx_vagas_empresa ON vagas(empresa_principal);
CREATE INDEX IF NOT EXISTS idx_vagas_cidade ON vagas(cidade_extraida);
CREATE INDEX IF NOT EXISTS idx_vagas_estado ON vagas(estado);
CREATE INDEX IF NOT EXISTS idx_vagas_modalidade ON vagas(modalidade);

-- RLS (Row Level Security) - opcional
ALTER TABLE vagas ENABLE ROW LEVEL SECURITY;

-- Política para permitir leitura pública (ajuste conforme necessário)
CREATE POLICY "Permitir leitura pública" ON vagas
    FOR SELECT USING (true);
