-- Script SQL para criar todas as tabelas no Supabase
-- Cole este código diretamente no SQL Editor do Supabase

-- =====================================================
-- TABELA DE EMPRESAS
-- =====================================================
CREATE TABLE IF NOT EXISTS companies (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    industry VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices para empresas
CREATE INDEX IF NOT EXISTS idx_companies_name ON companies(name);
CREATE INDEX IF NOT EXISTS idx_companies_industry ON companies(industry);

-- =====================================================
-- TABELA PRINCIPAL DE VAGAS
-- =====================================================
CREATE TABLE IF NOT EXISTS jobs (
    id SERIAL PRIMARY KEY,
    external_id TEXT,
    title VARCHAR(500) NOT NULL,
    seniority VARCHAR(50),
    area VARCHAR(100),
    company_id INTEGER REFERENCES companies(id),
    company_name VARCHAR(255),
    industry VARCHAR(100),
    employment_type VARCHAR(50),
    work_schedule TEXT,
    modality VARCHAR(50),
    location_city VARCHAR(100),
    location_state VARCHAR(10),
    location_region VARCHAR(100),
    salary_min DECIMAL(10,2),
    salary_max DECIMAL(10,2),
    salary_currency VARCHAR(10) DEFAULT 'BRL',
    salary_period VARCHAR(20) DEFAULT 'month',
    education_level VARCHAR(100),
    pcd BOOLEAN DEFAULT FALSE,
    source_name VARCHAR(50),
    source_url TEXT,
    raw_excerpt TEXT,
    confidence DECIMAL(3,2),
    parsed_at DATE,
    description TEXT,
    description_raw TEXT,
    published_date DATE,
    extraction_timestamp TIMESTAMP WITH TIME ZONE,
    data_quality_score DECIMAL(3,1),
    sector VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices para jobs
CREATE INDEX IF NOT EXISTS idx_jobs_title ON jobs(title);
CREATE INDEX IF NOT EXISTS idx_jobs_sector ON jobs(sector);
CREATE INDEX IF NOT EXISTS idx_jobs_company_name ON jobs(company_name);
CREATE INDEX IF NOT EXISTS idx_jobs_location_city ON jobs(location_city);
CREATE INDEX IF NOT EXISTS idx_jobs_modality ON jobs(modality);
CREATE INDEX IF NOT EXISTS idx_jobs_seniority ON jobs(seniority);
CREATE INDEX IF NOT EXISTS idx_jobs_employment_type ON jobs(employment_type);
CREATE INDEX IF NOT EXISTS idx_jobs_published_date ON jobs(published_date);
CREATE INDEX IF NOT EXISTS idx_jobs_salary_min ON jobs(salary_min);
CREATE INDEX IF NOT EXISTS idx_jobs_salary_max ON jobs(salary_max);

-- =====================================================
-- TABELA DE BENEFÍCIOS
-- =====================================================
CREATE TABLE IF NOT EXISTS job_benefits (
    id SERIAL PRIMARY KEY,
    job_id INTEGER REFERENCES jobs(id) ON DELETE CASCADE,
    benefit VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_benefits_job_id ON job_benefits(job_id);
CREATE INDEX IF NOT EXISTS idx_benefits_benefit ON job_benefits(benefit);

-- =====================================================
-- TABELA DE RESPONSABILIDADES
-- =====================================================
CREATE TABLE IF NOT EXISTS job_responsibilities (
    id SERIAL PRIMARY KEY,
    job_id INTEGER REFERENCES jobs(id) ON DELETE CASCADE,
    responsibility TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_responsibilities_job_id ON job_responsibilities(job_id);

-- =====================================================
-- TABELA DE REQUISITOS OBRIGATÓRIOS
-- =====================================================
CREATE TABLE IF NOT EXISTS job_requirements_must (
    id SERIAL PRIMARY KEY,
    job_id INTEGER REFERENCES jobs(id) ON DELETE CASCADE,
    requirement TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_requirements_must_job_id ON job_requirements_must(job_id);

-- =====================================================
-- TABELA DE REQUISITOS DESEJÁVEIS
-- =====================================================
CREATE TABLE IF NOT EXISTS job_requirements_nice (
    id SERIAL PRIMARY KEY,
    job_id INTEGER REFERENCES jobs(id) ON DELETE CASCADE,
    requirement TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_requirements_nice_job_id ON job_requirements_nice(job_id);

-- =====================================================
-- TABELA DE RECOMPENSAS
-- =====================================================
CREATE TABLE IF NOT EXISTS job_rewards (
    id SERIAL PRIMARY KEY,
    job_id INTEGER REFERENCES jobs(id) ON DELETE CASCADE,
    reward VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_rewards_job_id ON job_rewards(job_id);
CREATE INDEX IF NOT EXISTS idx_rewards_reward ON job_rewards(reward);

-- =====================================================
-- TABELA DE TAGS
-- =====================================================
CREATE TABLE IF NOT EXISTS job_tags (
    id SERIAL PRIMARY KEY,
    job_id INTEGER REFERENCES jobs(id) ON DELETE CASCADE,
    tag VARCHAR(100) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_tags_job_id ON job_tags(job_id);
CREATE INDEX IF NOT EXISTS idx_tags_name ON job_tags(tag);

-- =====================================================
-- FUNÇÃO PARA ATUALIZAR TIMESTAMP
-- =====================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- =====================================================
-- TRIGGERS PARA ATUALIZAR TIMESTAMPS
-- =====================================================
CREATE TRIGGER update_companies_updated_at 
    BEFORE UPDATE ON companies 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_jobs_updated_at 
    BEFORE UPDATE ON jobs 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- VIEW PARA CONSULTAS COMPLETAS
-- =====================================================
CREATE OR REPLACE VIEW jobs_complete_view AS
SELECT 
    j.*,
    c.name as company_full_name,
    c.industry as company_industry,
    ARRAY_AGG(DISTINCT jb.benefit) FILTER (WHERE jb.benefit IS NOT NULL) as benefits,
    ARRAY_AGG(DISTINCT jr.responsibility) FILTER (WHERE jr.responsibility IS NOT NULL) as responsibilities,
    ARRAY_AGG(DISTINCT jrm.requirement) FILTER (WHERE jrm.requirement IS NOT NULL) as requirements_must,
    ARRAY_AGG(DISTINCT jrn.requirement) FILTER (WHERE jrn.requirement IS NOT NULL) as requirements_nice,
    ARRAY_AGG(DISTINCT jrew.reward) FILTER (WHERE jrew.reward IS NOT NULL) as rewards,
    ARRAY_AGG(DISTINCT jt.tag) FILTER (WHERE jt.tag IS NOT NULL) as tags
FROM jobs j
LEFT JOIN companies c ON j.company_id = c.id
LEFT JOIN job_benefits jb ON j.id = jb.job_id
LEFT JOIN job_responsibilities jr ON j.id = jr.job_id
LEFT JOIN job_requirements_must jrm ON j.id = jrm.job_id
LEFT JOIN job_requirements_nice jrn ON j.id = jrn.job_id
LEFT JOIN job_rewards jrew ON j.id = jrew.job_id
LEFT JOIN job_tags jt ON j.id = jt.job_id
GROUP BY j.id, c.name, c.industry;

-- =====================================================
-- FUNÇÃO PARA INSERIR VAGA COMPLETA
-- =====================================================
CREATE OR REPLACE FUNCTION insert_job_complete(
    p_title VARCHAR(500),
    p_company_name VARCHAR(255),
    p_sector VARCHAR(100),
    p_seniority VARCHAR(50) DEFAULT NULL,
    p_area VARCHAR(100) DEFAULT NULL,
    p_industry VARCHAR(100) DEFAULT NULL,
    p_employment_type VARCHAR(50) DEFAULT NULL,
    p_work_schedule TEXT DEFAULT NULL,
    p_modality VARCHAR(50) DEFAULT NULL,
    p_location_city VARCHAR(100) DEFAULT NULL,
    p_location_state VARCHAR(10) DEFAULT NULL,
    p_location_region VARCHAR(100) DEFAULT NULL,
    p_salary_min DECIMAL(10,2) DEFAULT NULL,
    p_salary_max DECIMAL(10,2) DEFAULT NULL,
    p_education_level VARCHAR(100) DEFAULT NULL,
    p_pcd BOOLEAN DEFAULT FALSE,
    p_source_name VARCHAR(50) DEFAULT NULL,
    p_source_url TEXT DEFAULT NULL,
    p_description TEXT DEFAULT NULL,
    p_published_date DATE DEFAULT NULL,
    p_benefits TEXT[] DEFAULT NULL,
    p_responsibilities TEXT[] DEFAULT NULL,
    p_requirements_must TEXT[] DEFAULT NULL,
    p_requirements_nice TEXT[] DEFAULT NULL,
    p_rewards TEXT[] DEFAULT NULL,
    p_tags TEXT[] DEFAULT NULL
)
RETURNS INTEGER AS $$
DECLARE
    v_company_id INTEGER;
    v_job_id INTEGER;
    v_benefit TEXT;
    v_responsibility TEXT;
    v_requirement TEXT;
    v_reward TEXT;
    v_tag TEXT;
BEGIN
    -- Inserir ou obter empresa
    INSERT INTO companies (name, industry)
    VALUES (p_company_name, p_industry)
    ON CONFLICT (name) DO UPDATE SET
        industry = COALESCE(EXCLUDED.industry, companies.industry),
        updated_at = NOW()
    RETURNING id INTO v_company_id;
    
    IF v_company_id IS NULL THEN
        SELECT id INTO v_company_id FROM companies WHERE name = p_company_name;
    END IF;
    
    -- Inserir vaga
    INSERT INTO jobs (
        title, company_id, company_name, sector, seniority, area, industry,
        employment_type, work_schedule, modality, location_city, location_state,
        location_region, salary_min, salary_max, education_level, pcd,
        source_name, source_url, description, published_date
    ) VALUES (
        p_title, v_company_id, p_company_name, p_sector, p_seniority, p_area,
        p_industry, p_employment_type, p_work_schedule, p_modality, p_location_city,
        p_location_state, p_location_region, p_salary_min, p_salary_max,
        p_education_level, p_pcd, p_source_name, p_source_url, p_description,
        p_published_date
    ) RETURNING id INTO v_job_id;
    
    -- Inserir benefícios
    IF p_benefits IS NOT NULL THEN
        FOREACH v_benefit IN ARRAY p_benefits
        LOOP
            IF v_benefit IS NOT NULL AND trim(v_benefit) != '' THEN
                INSERT INTO job_benefits (job_id, benefit) VALUES (v_job_id, trim(v_benefit));
            END IF;
        END LOOP;
    END IF;
    
    -- Inserir responsabilidades
    IF p_responsibilities IS NOT NULL THEN
        FOREACH v_responsibility IN ARRAY p_responsibilities
        LOOP
            IF v_responsibility IS NOT NULL AND trim(v_responsibility) != '' THEN
                INSERT INTO job_responsibilities (job_id, responsibility) VALUES (v_job_id, trim(v_responsibility));
            END IF;
        END LOOP;
    END IF;
    
    -- Inserir requisitos obrigatórios
    IF p_requirements_must IS NOT NULL THEN
        FOREACH v_requirement IN ARRAY p_requirements_must
        LOOP
            IF v_requirement IS NOT NULL AND trim(v_requirement) != '' THEN
                INSERT INTO job_requirements_must (job_id, requirement) VALUES (v_job_id, trim(v_requirement));
            END IF;
        END LOOP;
    END IF;
    
    -- Inserir requisitos desejáveis
    IF p_requirements_nice IS NOT NULL THEN
        FOREACH v_requirement IN ARRAY p_requirements_nice
        LOOP
            IF v_requirement IS NOT NULL AND trim(v_requirement) != '' THEN
                INSERT INTO job_requirements_nice (job_id, requirement) VALUES (v_job_id, trim(v_requirement));
            END IF;
        END LOOP;
    END IF;
    
    -- Inserir recompensas
    IF p_rewards IS NOT NULL THEN
        FOREACH v_reward IN ARRAY p_rewards
        LOOP
            IF v_reward IS NOT NULL AND trim(v_reward) != '' THEN
                INSERT INTO job_rewards (job_id, reward) VALUES (v_job_id, trim(v_reward));
            END IF;
        END LOOP;
    END IF;
    
    -- Inserir tags
    IF p_tags IS NOT NULL THEN
        FOREACH v_tag IN ARRAY p_tags
        LOOP
            IF v_tag IS NOT NULL AND trim(v_tag) != '' THEN
                INSERT INTO job_tags (job_id, tag) VALUES (v_job_id, trim(v_tag));
            END IF;
        END LOOP;
    END IF;
    
    RETURN v_job_id;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- COMENTÁRIOS FINAIS
-- =====================================================
-- Este script cria:
-- 1. Tabela companies (empresas)
-- 2. Tabela jobs (vagas principais)
-- 3. Tabelas relacionadas: benefits, responsibilities, requirements_must, requirements_nice, rewards, tags
-- 4. Índices para otimização de consultas
-- 5. Triggers para atualização automática de timestamps
-- 6. View para consultas completas
-- 7. Função para inserir vagas completas com dados relacionados
--
-- Para usar a função de inserção:
-- SELECT insert_job_complete(
--     'Desenvolvedor Python',
--     'Empresa XYZ',
--     'Tecnologia',
--     'Pleno',
--     'Desenvolvimento',
--     'TI',
--     'CLT',
--     'Segunda a Sexta',
--     'Remoto',
--     'São Paulo',
--     'SP',
--     'Sudeste',
--     5000.00,
--     8000.00,
--     'Superior',
--     false,
--     'Catho',
--     'https://catho.com.br/vaga/123',
--     'Descrição da vaga...',
--     '2024-01-15',
--     ARRAY['Vale Refeição', 'Plano de Saúde'],
--     ARRAY['Desenvolver aplicações', 'Manter código'],
--     ARRAY['Python', 'Django'],
--     ARRAY['React', 'AWS'],
--     ARRAY['Bônus por performance'],
--     ARRAY['python', 'backend', 'web']
-- );