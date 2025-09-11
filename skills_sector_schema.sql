-- Schema SQL para tabelas de skills agregadas e mapeamento de setores
-- Execute este script no SQL Editor do Supabase

-- Tabela de taxonomia de skills
CREATE TABLE IF NOT EXISTS skills_taxonomy (
    id SERIAL PRIMARY KEY,
    skill_name VARCHAR(255) NOT NULL UNIQUE,
    category VARCHAR(100),
    subcategory VARCHAR(100),
    skill_type VARCHAR(50), -- technical, soft, language, etc.
    description TEXT,
    synonyms TEXT[], -- array de sinônimos
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices para skills_taxonomy
CREATE INDEX IF NOT EXISTS idx_skills_taxonomy_name ON skills_taxonomy(skill_name);
CREATE INDEX IF NOT EXISTS idx_skills_taxonomy_category ON skills_taxonomy(category);
CREATE INDEX IF NOT EXISTS idx_skills_taxonomy_type ON skills_taxonomy(skill_type);

-- Tabela de estatísticas agregadas de skills
CREATE TABLE IF NOT EXISTS skills_statistics (
    id SERIAL PRIMARY KEY,
    skill_name VARCHAR(255) NOT NULL,
    total_jobs INTEGER DEFAULT 0,
    percentage DECIMAL(5,2) DEFAULT 0.00,
    avg_salary_min DECIMAL(10,2),
    avg_salary_max DECIMAL(10,2),
    top_locations TEXT[], -- array das principais localizações
    top_companies TEXT[], -- array das principais empresas
    growth_trend VARCHAR(20), -- increasing, stable, decreasing
    last_updated DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices para skills_statistics
CREATE INDEX IF NOT EXISTS idx_skills_stats_name ON skills_statistics(skill_name);
CREATE INDEX IF NOT EXISTS idx_skills_stats_jobs ON skills_statistics(total_jobs DESC);
CREATE INDEX IF NOT EXISTS idx_skills_stats_percentage ON skills_statistics(percentage DESC);

-- Tabela de mapeamento de setores
CREATE TABLE IF NOT EXISTS sector_mapping (
    id SERIAL PRIMARY KEY,
    sector_original VARCHAR(255) NOT NULL,
    sector_normalized VARCHAR(100) NOT NULL,
    sector_category VARCHAR(50), -- primary, secondary, tertiary
    industry_group VARCHAR(100),
    description TEXT,
    keywords TEXT[], -- palavras-chave para identificação
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices para sector_mapping
CREATE INDEX IF NOT EXISTS idx_sector_mapping_original ON sector_mapping(sector_original);
CREATE INDEX IF NOT EXISTS idx_sector_mapping_normalized ON sector_mapping(sector_normalized);
CREATE INDEX IF NOT EXISTS idx_sector_mapping_category ON sector_mapping(sector_category);

-- Tabela de cobertura de setores
CREATE TABLE IF NOT EXISTS sector_coverage (
    id SERIAL PRIMARY KEY,
    sector_name VARCHAR(100) NOT NULL,
    total_jobs INTEGER DEFAULT 0,
    percentage DECIMAL(5,2) DEFAULT 0.00,
    avg_skills_per_job DECIMAL(4,1) DEFAULT 0.0,
    top_skills TEXT[], -- array das principais skills do setor
    avg_salary_min DECIMAL(10,2),
    avg_salary_max DECIMAL(10,2),
    main_locations TEXT[], -- principais localizações do setor
    job_growth_rate DECIMAL(5,2), -- taxa de crescimento de vagas
    last_updated DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices para sector_coverage
CREATE INDEX IF NOT EXISTS idx_sector_coverage_name ON sector_coverage(sector_name);
CREATE INDEX IF NOT EXISTS idx_sector_coverage_jobs ON sector_coverage(total_jobs DESC);
CREATE INDEX IF NOT EXISTS idx_sector_coverage_percentage ON sector_coverage(percentage DESC);

-- Função para atualizar timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers para atualizar updated_at automaticamente
CREATE TRIGGER update_skills_taxonomy_updated_at
    BEFORE UPDATE ON skills_taxonomy
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_skills_statistics_updated_at
    BEFORE UPDATE ON skills_statistics
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_sector_mapping_updated_at
    BEFORE UPDATE ON sector_mapping
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_sector_coverage_updated_at
    BEFORE UPDATE ON sector_coverage
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- View para estatísticas completas de skills
CREATE OR REPLACE VIEW skills_complete_stats AS
SELECT 
    st.skill_name,
    st.category,
    st.subcategory,
    st.skill_type,
    st.description,
    ss.total_jobs,
    ss.percentage,
    ss.avg_salary_min,
    ss.avg_salary_max,
    ss.top_locations,
    ss.top_companies,
    ss.growth_trend,
    ss.last_updated
FROM skills_taxonomy st
LEFT JOIN skills_statistics ss ON st.skill_name = ss.skill_name;

-- View para análise de setores
CREATE OR REPLACE VIEW sectors_analysis AS
SELECT 
    sm.sector_normalized,
    sm.sector_category,
    sm.industry_group,
    sc.total_jobs,
    sc.percentage,
    sc.avg_skills_per_job,
    sc.top_skills,
    sc.avg_salary_min,
    sc.avg_salary_max,
    sc.main_locations,
    sc.job_growth_rate
FROM sector_mapping sm
LEFT JOIN sector_coverage sc ON sm.sector_normalized = sc.sector_name;

-- Comentários nas tabelas
COMMENT ON TABLE skills_taxonomy IS 'Taxonomia padronizada de skills com categorização';
COMMENT ON TABLE skills_statistics IS 'Estatísticas agregadas de demanda por skills';
COMMENT ON TABLE sector_mapping IS 'Mapeamento e normalização de setores industriais';
COMMENT ON TABLE sector_coverage IS 'Cobertura e estatísticas por setor';

-- Inserir alguns dados de exemplo (opcional)
INSERT INTO skills_taxonomy (skill_name, category, subcategory, skill_type) VALUES
('Python', 'Programação', 'Linguagens', 'technical'),
('JavaScript', 'Programação', 'Linguagens', 'technical'),
('SQL', 'Banco de Dados', 'Query Languages', 'technical'),
('Comunicação', 'Soft Skills', 'Interpessoal', 'soft'),
('Liderança', 'Soft Skills', 'Gestão', 'soft')
ON CONFLICT (skill_name) DO NOTHING;

INSERT INTO sector_mapping (sector_original, sector_normalized, sector_category) VALUES
('Tecnologia da Informação', 'TI', 'tertiary'),
('Desenvolvimento de Software', 'TI', 'tertiary'),
('Indústria Automobilística', 'Automotivo', 'secondary'),
('Saúde e Medicina', 'Saúde', 'tertiary'),
('Educação', 'Educação', 'tertiary')
ON CONFLICT DO NOTHING;

-- Função para recalcular estatísticas de skills
CREATE OR REPLACE FUNCTION recalculate_skills_stats()
RETURNS void AS $$
BEGIN
    -- Limpar estatísticas antigas
    DELETE FROM skills_statistics;
    
    -- Recalcular baseado nos dados atuais
    INSERT INTO skills_statistics (skill_name, total_jobs, percentage)
    SELECT 
        jrm.requirement as skill_name,
        COUNT(*) as total_jobs,
        ROUND((COUNT(*) * 100.0 / (SELECT COUNT(*) FROM jobs)), 2) as percentage
    FROM job_requirements_must jrm
    JOIN jobs j ON jrm.job_id = j.id
    GROUP BY jrm.requirement
    ORDER BY total_jobs DESC;
    
    -- Atualizar salários médios
    UPDATE skills_statistics ss
    SET 
        avg_salary_min = subq.avg_min,
        avg_salary_max = subq.avg_max
    FROM (
        SELECT 
            jrm.requirement,
            AVG(j.salary_min) as avg_min,
            AVG(j.salary_max) as avg_max
        FROM job_requirements_must jrm
        JOIN jobs j ON jrm.job_id = j.id
        WHERE j.salary_min IS NOT NULL OR j.salary_max IS NOT NULL
        GROUP BY jrm.requirement
    ) subq
    WHERE ss.skill_name = subq.requirement;
END;
$$ LANGUAGE plpgsql;

-- Função para recalcular cobertura de setores
CREATE OR REPLACE FUNCTION recalculate_sector_coverage()
RETURNS void AS $$
BEGIN
    -- Limpar dados antigos
    DELETE FROM sector_coverage;
    
    -- Recalcular baseado nos dados atuais
    INSERT INTO sector_coverage (sector_name, total_jobs, percentage, avg_skills_per_job)
    SELECT 
        COALESCE(j.industry, 'Não especificado') as sector_name,
        COUNT(*) as total_jobs,
        ROUND((COUNT(*) * 100.0 / (SELECT COUNT(*) FROM jobs)), 2) as percentage,
        AVG(skill_counts.skill_count) as avg_skills_per_job
    FROM jobs j
    LEFT JOIN (
        SELECT job_id, COUNT(*) as skill_count
        FROM job_requirements_must
        GROUP BY job_id
    ) skill_counts ON j.id = skill_counts.job_id
    GROUP BY j.industry
    ORDER BY total_jobs DESC;
END;
$$ LANGUAGE plpgsql;

SELECT 'Schema criado com sucesso! Execute as funções recalculate_skills_stats() e recalculate_sector_coverage() para popular as tabelas.' as status;