-- Script SQL para criar tabela de vagas com classificação por setor no Supabase
-- Execute este script no SQL Editor do Supabase

-- Criar tabela de setores
CREATE TABLE IF NOT EXISTS public.setores (
    id SERIAL PRIMARY KEY,
    sector_key VARCHAR(50) UNIQUE NOT NULL,
    sector_name VARCHAR(100) NOT NULL,
    description TEXT,
    keywords TEXT[], -- Array de palavras-chave
    catho_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Criar tabela principal de vagas
CREATE TABLE IF NOT EXISTS public.vagas (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    company VARCHAR(200),
    location VARCHAR(200),
    description TEXT,
    link TEXT,
    salary_min DECIMAL(10,2),
    salary_max DECIMAL(10,2),
    salary_text VARCHAR(100),
    
    -- Informações de setor
    source_sector VARCHAR(50), -- Setor da URL de origem
    source_sector_name VARCHAR(100),
    classified_sector VARCHAR(50), -- Setor classificado pelo algoritmo
    classified_sector_name VARCHAR(100),
    sector_confidence INTEGER DEFAULT 0, -- Pontuação de confiança da classificação
    
    -- Metadados de extração
    extraction_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    extraction_method VARCHAR(50) DEFAULT 'catho_sectors',
    page_number INTEGER,
    source_url TEXT,
    
    -- Campos de qualidade
    data_quality_score DECIMAL(3,2),
    has_salary BOOLEAN DEFAULT FALSE,
    has_description BOOLEAN DEFAULT FALSE,
    has_location BOOLEAN DEFAULT FALSE,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Índices e constraints
    CONSTRAINT fk_source_sector FOREIGN KEY (source_sector) REFERENCES setores(sector_key),
    CONSTRAINT fk_classified_sector FOREIGN KEY (classified_sector) REFERENCES setores(sector_key)
);

-- Inserir dados dos setores do Catho
INSERT INTO public.setores (sector_key, sector_name, description, keywords, catho_url) VALUES
('administracao', 'Administração', 'Vagas relacionadas à gestão, administração e coordenação', 
 ARRAY['administração', 'administrativo', 'gestão', 'gerência', 'coordenação', 'supervisão', 'direção'],
 'https://www.catho.com.br/vagas/?area_id%5B0%5D=1&area_id%5B1%5D=3&area_id%5B2%5D=12&area_id%5B3%5D=20&area_id%5B4%5D=47&area_id%5B5%5D=67&area_id%5B6%5D=69&area_id%5B7%5D=73&area_id%5B8%5D=74&area_id%5B9%5D=75&area_id%5B10%5D=1906&area_id%5B11%5D=1937'),

('comercial_vendas', 'Comercial e Vendas', 'Vagas de vendas, comercial e relacionamento com clientes',
 ARRAY['vendas', 'comercial', 'consultor', 'representante', 'vendedor', 'closer', 'negociação'],
 'https://www.catho.com.br/vagas/area-comercial-vendas/'),

('comercio_exterior', 'Comércio Exterior', 'Vagas relacionadas a importação, exportação e comércio internacional',
 ARRAY['comércio exterior', 'importação', 'exportação', 'aduaneiro', 'desembaraço', 'trading'],
 'https://www.catho.com.br/vagas/?area_id%5B0%5D=15&area_id%5B1%5D=70'),

('educacao', 'Educação', 'Vagas na área de ensino e educação',
 ARRAY['professor', 'educação', 'ensino', 'pedagógico', 'instrutor', 'coordenador pedagógico'],
 'https://www.catho.com.br/vagas/?area_id%5B0%5D=24&area_id%5B1%5D=87'),

('financeira', 'Financeira', 'Vagas nas áreas financeira, contábil e controladoria',
 ARRAY['financeiro', 'contábil', 'tesouraria', 'controladoria', 'analista financeiro', 'contador'],
 'https://www.catho.com.br/vagas/?area_id%5B0%5D=2&area_id%5B1%5D=11&area_id%5B2%5D=19&area_id%5B3%5D=23&area_id%5B4%5D=40&area_id%5B5%5D=76'),

('hotelaria_turismo', 'Hotelaria e Turismo', 'Vagas em hotelaria, turismo e gastronomia',
 ARRAY['hotelaria', 'turismo', 'hotel', 'restaurante', 'cozinheiro', 'garçom', 'recepcionista'],
 'https://www.catho.com.br/vagas/?area_id%5B0%5D=48&area_id%5B1%5D=72'),

('informatica', 'Informática', 'Vagas em tecnologia da informação e desenvolvimento',
 ARRAY['desenvolvedor', 'programador', 'ti', 'tecnologia', 'software', 'sistemas', 'java', 'python'],
 'https://www.catho.com.br/vagas/?area_id%5B0%5D=51&area_id%5B1%5D=52'),

('saude', 'Saúde', 'Vagas na área da saúde e medicina',
 ARRAY['médico', 'enfermeiro', 'farmacêutico', 'fisioterapeuta', 'dentista', 'saúde', 'hospital'],
 'https://www.catho.com.br/vagas/?area_id%5B0%5D=13&area_id%5B1%5D=26&area_id%5B2%5D=39&area_id%5B3%5D=41&area_id%5B4%5D=43&area_id%5B5%5D=45&area_id%5B6%5D=46&area_id%5B7%5D=58&area_id%5B8%5D=61&area_id%5B9%5D=62&area_id%5B10%5D=65&area_id%5B11%5D=1902'),

('suprimentos', 'Suprimentos', 'Vagas em compras, suprimentos e logística',
 ARRAY['compras', 'suprimentos', 'logística', 'almoxarifado', 'estoque', 'procurement'],
 'https://www.catho.com.br/vagas/?area_id%5B0%5D=55&area_id%5B1%5D=88'),

('agricultura_pecuaria_veterinaria', 'Agricultura, Pecuária e Veterinária', 'Vagas no agronegócio e medicina veterinária',
 ARRAY['veterinário', 'agricultura', 'pecuária', 'agronegócio', 'zootecnia', 'agrônomo'],
 'https://www.catho.com.br/vagas/?area_id%5B0%5D=1858&area_id%5B1%5D=1859&area_id%5B2%5D=1904&area_id%5B3%5D=1943'),

('artes_arquitetura_design', 'Artes, Arquitetura e Design', 'Vagas criativas em arte, arquitetura e design',
 ARRAY['arquiteto', 'designer', 'arte', 'criativo', 'design gráfico', 'ux', 'ui'],
 'https://www.catho.com.br/vagas/?area_id%5B0%5D=5&area_id%5B1%5D=6&area_id%5B2%5D=7&area_id%5B3%5D=21&area_id%5B4%5D=60'),

('comunicacao_marketing', 'Comunicação e Marketing', 'Vagas em marketing, comunicação e publicidade',
 ARRAY['marketing', 'comunicação', 'publicidade', 'social media', 'digital', 'conteúdo'],
 'https://www.catho.com.br/vagas/?area_id%5B0%5D=53&area_id%5B1%5D=57&area_id%5B2%5D=66&area_id%5B3%5D=71&area_id%5B4%5D=1965'),

('engenharia', 'Engenharia', 'Vagas em diversas áreas da engenharia',
 ARRAY['engenheiro', 'engenharia', 'civil', 'mecânico', 'elétrico', 'químico', 'produção'],
 'https://www.catho.com.br/vagas/?area_id%5B0%5D=18&area_id%5B1%5D=29&area_id%5B2%5D=30&area_id%5B3%5D=31&area_id%5B4%5D=32&area_id%5B5%5D=34&area_id%5B6%5D=35&area_id%5B7%5D=36&area_id%5B8%5D=37&area_id%5B9%5D=38&area_id%5B10%5D=483&area_id%5B11%5D=484'),

('industrial', 'Industrial', 'Vagas na área industrial e de produção',
 ARRAY['industrial', 'produção', 'operador', 'técnico', 'manufatura', 'fábrica'],
 'https://www.catho.com.br/vagas/?area_id%5B0%5D=9&area_id%5B1%5D=10&area_id%5B2%5D=25&area_id%5B3%5D=50&area_id%5B4%5D=56'),

('juridica', 'Jurídica', 'Vagas na área jurídica e legal',
 ARRAY['advogado', 'jurídico', 'direito', 'legal', 'compliance', 'contrato'],
 'https://www.catho.com.br/vagas/area-juridica/'),

('tecnica', 'Técnica', 'Vagas técnicas e de manutenção',
 ARRAY['técnico', 'manutenção', 'instalação', 'reparo', 'assistência técnica'],
 'https://www.catho.com.br/vagas/?area_id%5B0%5D=79&area_id%5B1%5D=80'),

('telemarketing', 'Telemarketing', 'Vagas em telemarketing e atendimento ao cliente',
 ARRAY['telemarketing', 'call center', 'atendimento', 'sac', 'operador', 'televendas'],
 'https://www.catho.com.br/vagas/area-atendimento-ao-cliente-call-center-telemarketing/'),

('telecomunicacoes', 'Telecomunicações', 'Vagas em telecomunicações e redes',
 ARRAY['telecomunicações', 'telecom', 'redes', 'fibra óptica', 'telefonia'],
 'https://www.catho.com.br/vagas/area-telecomunicacoes-engenharia-de-telecomunicacoes/'),

('servico_social', 'Serviço Social', 'Vagas em serviço social e assistência',
 ARRAY['assistente social', 'serviço social', 'social', 'assistência'],
 'https://www.catho.com.br/vagas/area-servico-social/'),

('outros', 'Outros', 'Vagas que não se encaixam nas categorias específicas',
 ARRAY['outros', 'geral', 'diversas'],
 NULL)

ON CONFLICT (sector_key) DO UPDATE SET
    sector_name = EXCLUDED.sector_name,
    description = EXCLUDED.description,
    keywords = EXCLUDED.keywords,
    catho_url = EXCLUDED.catho_url,
    updated_at = NOW();

-- Criar índices para melhor performance
CREATE INDEX IF NOT EXISTS idx_vagas_title ON public.vagas USING gin(to_tsvector('portuguese', title));
CREATE INDEX IF NOT EXISTS idx_vagas_company ON public.vagas (company);
CREATE INDEX IF NOT EXISTS idx_vagas_location ON public.vagas (location);
CREATE INDEX IF NOT EXISTS idx_vagas_source_sector ON public.vagas (source_sector);
CREATE INDEX IF NOT EXISTS idx_vagas_classified_sector ON public.vagas (classified_sector);
CREATE INDEX IF NOT EXISTS idx_vagas_extraction_date ON public.vagas (extraction_date);
CREATE INDEX IF NOT EXISTS idx_vagas_data_quality ON public.vagas (data_quality_score);
CREATE INDEX IF NOT EXISTS idx_vagas_salary ON public.vagas (salary_min, salary_max);

-- Criar função para atualizar timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Criar triggers para atualizar timestamp automaticamente
CREATE TRIGGER update_setores_updated_at BEFORE UPDATE ON public.setores
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_vagas_updated_at BEFORE UPDATE ON public.vagas
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Criar views úteis
CREATE OR REPLACE VIEW public.vagas_por_setor AS
SELECT 
    s.sector_name,
    s.sector_key,
    COUNT(v.id) as total_vagas,
    COUNT(CASE WHEN v.has_salary THEN 1 END) as vagas_com_salario,
    COUNT(CASE WHEN v.has_description THEN 1 END) as vagas_com_descricao,
    AVG(v.data_quality_score) as qualidade_media,
    MAX(v.extraction_date) as ultima_extracao
FROM public.setores s
LEFT JOIN public.vagas v ON s.sector_key = v.classified_sector
GROUP BY s.sector_key, s.sector_name
ORDER BY total_vagas DESC;

CREATE OR REPLACE VIEW public.vagas_recentes AS
SELECT 
    v.*,
    s.sector_name as setor_nome
FROM public.vagas v
JOIN public.setores s ON v.classified_sector = s.sector_key
WHERE v.extraction_date >= NOW() - INTERVAL '7 days'
ORDER BY v.extraction_date DESC;

-- Comentários nas tabelas
COMMENT ON TABLE public.setores IS 'Tabela de setores/categorias de vagas do Catho';
COMMENT ON TABLE public.vagas IS 'Tabela principal de vagas extraídas com classificação por setor';
COMMENT ON VIEW public.vagas_por_setor IS 'View com estatísticas de vagas agrupadas por setor';
COMMENT ON VIEW public.vagas_recentes IS 'View com vagas extraídas nos últimos 7 dias';

-- Habilitar RLS (Row Level Security) se necessário
-- ALTER TABLE public.setores ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE public.vagas ENABLE ROW LEVEL SECURITY;

SELECT 'Tabelas criadas com sucesso!' as status;