-- Schema avançado para estruturar dados de vagas de emprego no Supabase
-- Baseado na estrutura do arquivo vagas_industrial_estruturado_avancado.json
-- Execute este script no SQL Editor do Supabase

-- Tabela principal de empresas
CREATE TABLE IF NOT EXISTS companies (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    industry VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índice para busca rápida por nome da empresa
CREATE INDEX IF NOT EXISTS idx_companies_name ON companies(name);
CREATE INDEX IF NOT EXISTS idx_companies_industry ON companies(industry);

-- Tabela principal de vagas
CREATE TABLE IF NOT EXISTS jobs (
    id SERIAL PRIMARY KEY,
    external_id TEXT, -- ID do sistema original
    title VARCHAR(500) NOT NULL,
    seniority VARCHAR(50), -- Junior, Pleno, Senior, etc.
    area VARCHAR(100), -- Manutenção, Desenvolvimento, etc.
    company_id INTEGER REFERENCES companies(id),
    company_name VARCHAR(255), -- Fallback se não houver company_id
    industry VARCHAR(100), -- Industrial, Tecnologia, etc.
    employment_type VARCHAR(50), -- CLT, PJ, Estágio, etc.
    work_schedule TEXT, -- Horário de trabalho detalhado
    modality VARCHAR(50), -- Presencial, Remoto, Híbrido
    location_city VARCHAR(100),
    location_state VARCHAR(10),
    location_region VARCHAR(100),
    salary_min DECIMAL(10,2),
    salary_max DECIMAL(10,2),
    salary_currency VARCHAR(10) DEFAULT 'BRL',
    salary_period VARCHAR(20) DEFAULT 'month', -- month, hour, day
    education_level VARCHAR(100), -- Fundamental, Médio, Superior, etc.
    pcd BOOLEAN DEFAULT FALSE, -- Vaga para PCD
    source_name VARCHAR(50), -- Catho, LinkedIn, etc.
    source_url TEXT,
    raw_excerpt TEXT,
    confidence DECIMAL(3,2), -- Score de confiança da extração
    parsed_at DATE,
    description TEXT,
    description_raw TEXT,
    published_date DATE,
    extraction_timestamp TIMESTAMP WITH TIME ZONE,
    data_quality_score DECIMAL(3,1),
    sector VARCHAR(100), -- Setor da vaga (Informatica, Saude, etc.)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices para otimização de consultas
CREATE INDEX IF NOT EXISTS idx_jobs_title ON jobs(title);
CREATE INDEX IF NOT EXISTS idx_jobs_seniority ON jobs(seniority);
CREATE INDEX IF NOT EXISTS idx_jobs_area ON jobs(area);
CREATE INDEX IF NOT EXISTS idx_jobs_industry ON jobs(industry);
CREATE INDEX IF NOT EXISTS idx_jobs_employment_type ON jobs(employment_type);
CREATE INDEX IF NOT EXISTS idx_jobs_modality ON jobs(modality);
CREATE INDEX IF NOT EXISTS idx_jobs_location_city ON jobs(location_city);
CREATE INDEX IF NOT EXISTS idx_jobs_location_state ON jobs(location_state);
CREATE INDEX IF NOT EXISTS idx_jobs_education_level ON jobs(education_level);
CREATE INDEX IF NOT EXISTS idx_jobs_pcd ON jobs(pcd);
CREATE INDEX IF NOT EXISTS idx_jobs_source_name ON jobs(source_name);
CREATE INDEX IF NOT EXISTS idx_jobs_published_date ON jobs(published_date);
CREATE INDEX IF NOT EXISTS idx_jobs_quality_score ON jobs(data_quality_score);
CREATE INDEX IF NOT EXISTS idx_jobs_sector ON jobs(sector);
CREATE INDEX IF NOT EXISTS idx_jobs_salary_min ON jobs(salary_min);
CREATE INDEX IF NOT EXISTS idx_jobs_salary_max ON jobs(salary_max);

-- Tabela de benefícios
CREATE TABLE IF NOT EXISTS job_benefits (
    id SERIAL PRIMARY KEY,
    job_id INTEGER REFERENCES jobs(id) ON DELETE CASCADE,
    benefit VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índice para busca de benefícios
CREATE INDEX IF NOT EXISTS idx_benefits_job_id ON job_benefits(job_id);
CREATE INDEX IF NOT EXISTS idx_benefits_name ON job_benefits(benefit);

-- Tabela de recompensas/prêmios
CREATE TABLE IF NOT EXISTS job_rewards (
    id SERIAL PRIMARY KEY,
    job_id INTEGER REFERENCES jobs(id) ON DELETE CASCADE,
    reward TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índice para busca de recompensas
CREATE INDEX IF NOT EXISTS idx_rewards_job_id ON job_rewards(job_id);

-- Tabela de requisitos obrigatórios
CREATE TABLE IF NOT EXISTS job_requirements_must (
    id SERIAL PRIMARY KEY,
    job_id INTEGER REFERENCES jobs(id) ON DELETE CASCADE,
    requirement TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índice para busca de requisitos obrigatórios
CREATE INDEX IF NOT EXISTS idx_requirements_must_job_id ON job_requirements_must(job_id);

-- Tabela de requisitos desejáveis
CREATE TABLE IF NOT EXISTS job_requirements_nice (
    id SERIAL PRIMARY KEY,
    job_id INTEGER REFERENCES jobs(id) ON DELETE CASCADE,
    requirement TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índice para busca de requisitos desejáveis
CREATE INDEX IF NOT EXISTS idx_requirements_nice_job_id ON job_requirements_nice(job_id);

-- Tabela de responsabilidades
CREATE TABLE IF NOT EXISTS job_responsibilities (
    id SERIAL PRIMARY KEY,
    job_id INTEGER REFERENCES jobs(id) ON DELETE CASCADE,
    responsibility TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índice para busca de responsabilidades
CREATE INDEX IF NOT EXISTS idx_responsibilities_job_id ON job_responsibilities(job_id);

-- Tabela de tags
CREATE TABLE IF NOT EXISTS job_tags (
    id SERIAL PRIMARY KEY,
    job_id INTEGER REFERENCES jobs(id) ON DELETE CASCADE,
    tag VARCHAR(100) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índice para busca de tags
CREATE INDEX IF NOT EXISTS idx_tags_job_id ON job_tags(job_id);
CREATE INDEX IF NOT EXISTS idx_tags_name ON job_tags(tag);

-- View para consulta completa de vagas
CREATE OR REPLACE VIEW jobs_complete_advanced AS
SELECT 
    j.*,
    c.name as company_full_name,
    c.industry as company_industry,
    ARRAY_AGG(DISTINCT jb.benefit) FILTER (WHERE jb.benefit IS NOT NULL) as benefits,
    ARRAY_AGG(DISTINCT jr.reward) FILTER (WHERE jr.reward IS NOT NULL) as rewards,
    ARRAY_AGG(DISTINCT jrm.requirement) FILTER (WHERE jrm.requirement IS NOT NULL) as requirements_must,
    ARRAY_AGG(DISTINCT jrn.requirement) FILTER (WHERE jrn.requirement IS NOT NULL) as requirements_nice,
    ARRAY_AGG(DISTINCT jresp.responsibility) FILTER (WHERE jresp.responsibility IS NOT NULL) as responsibilities,
    ARRAY_AGG(DISTINCT jt.tag) FILTER (WHERE jt.tag IS NOT NULL) as tags
FROM jobs j
LEFT JOIN companies c ON j.company_id = c.id
LEFT JOIN job_benefits jb ON j.id = jb.job_id
LEFT JOIN job_rewards jr ON j.id = jr.job_id
LEFT JOIN job_requirements_must jrm ON j.id = jrm.job_id
LEFT JOIN job_requirements_nice jrn ON j.id = jrn.job_id
LEFT JOIN job_responsibilities jresp ON j.id = jresp.job_id
LEFT JOIN job_tags jt ON j.id = jt.job_id
GROUP BY j.id, c.name, c.industry;

-- Função para atualizar timestamp de updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers para atualizar updated_at automaticamente
CREATE TRIGGER update_companies_updated_at BEFORE UPDATE ON companies
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_jobs_updated_at BEFORE UPDATE ON jobs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Comentários nas tabelas
COMMENT ON TABLE companies IS 'Tabela de empresas que publicam vagas';
COMMENT ON TABLE jobs IS 'Tabela principal de vagas de emprego com estrutura avançada';
COMMENT ON TABLE job_benefits IS 'Benefícios oferecidos pelas vagas';
COMMENT ON TABLE job_rewards IS 'Recompensas e prêmios oferecidos pelas vagas';
COMMENT ON TABLE job_requirements_must IS 'Requisitos obrigatórios das vagas';
COMMENT ON TABLE job_requirements_nice IS 'Requisitos desejáveis das vagas';
COMMENT ON TABLE job_responsibilities IS 'Responsabilidades e atividades das vagas';
COMMENT ON TABLE job_tags IS 'Tags e palavras-chave das vagas';

-- Função para inserir vaga completa com dados relacionados
CREATE OR REPLACE FUNCTION insert_job_complete(
    p_title VARCHAR(500),
    p_seniority VARCHAR(50),
    p_area VARCHAR(100),
    p_company_name VARCHAR(255),
    p_industry VARCHAR(100),
    p_employment_type VARCHAR(50),
    p_work_schedule TEXT,
    p_modality VARCHAR(50),
    p_location_city VARCHAR(100),
    p_location_state VARCHAR(10),
    p_location_region VARCHAR(100),
    p_salary_min DECIMAL(10,2),
    p_salary_max DECIMAL(10,2),
    p_salary_currency VARCHAR(10),
    p_salary_period VARCHAR(20),
    p_education_level VARCHAR(100),
    p_pcd BOOLEAN,
    p_source_name VARCHAR(50),
    p_source_url TEXT,
    p_raw_excerpt TEXT,
    p_confidence DECIMAL(3,2),
    p_parsed_at DATE,
    p_sector VARCHAR(100),
    p_benefits TEXT[],
    p_rewards TEXT[],
    p_requirements_must TEXT[],
    p_requirements_nice TEXT[],
    p_responsibilities TEXT[],
    p_tags TEXT[]
)
RETURNS INTEGER AS $$
DECLARE
    v_company_id INTEGER;
    v_job_id INTEGER;
    v_benefit TEXT;
    v_reward TEXT;
    v_requirement TEXT;
    v_responsibility TEXT;
    v_tag TEXT;
BEGIN
    -- Inserir ou buscar empresa
    INSERT INTO companies (name, industry)
    VALUES (p_company_name, p_industry)
    ON CONFLICT (name) DO UPDATE SET industry = EXCLUDED.industry
    RETURNING id INTO v_company_id;
    
    IF v_company_id IS NULL THEN
        SELECT id INTO v_company_id FROM companies WHERE name = p_company_name;
    END IF;
    
    -- Inserir vaga
    INSERT INTO jobs (
        title, seniority, area, company_id, company_name, industry,
        employment_type, work_schedule, modality, location_city,
        location_state, location_region, salary_min, salary_max,
        salary_currency, salary_period, education_level, pcd,
        source_name, source_url, raw_excerpt, confidence,
        parsed_at, sector
    ) VALUES (
        p_title, p_seniority, p_area, v_company_id, p_company_name, p_industry,
        p_employment_type, p_work_schedule, p_modality, p_location_city,
        p_location_state, p_location_region, p_salary_min, p_salary_max,
        p_salary_currency, p_salary_period, p_education_level, p_pcd,
        p_source_name, p_source_url, p_raw_excerpt, p_confidence,
        p_parsed_at, p_sector
    ) RETURNING id INTO v_job_id;
    
    -- Inserir benefícios
    IF p_benefits IS NOT NULL THEN
        FOREACH v_benefit IN ARRAY p_benefits
        LOOP
            INSERT INTO job_benefits (job_id, benefit) VALUES (v_job_id, v_benefit);
        END LOOP;
    END IF;
    
    -- Inserir recompensas
    IF p_rewards IS NOT NULL THEN
        FOREACH v_reward IN ARRAY p_rewards
        LOOP
            INSERT INTO job_rewards (job_id, reward) VALUES (v_job_id, v_reward);
        END LOOP;
    END IF;
    
    -- Inserir requisitos obrigatórios
    IF p_requirements_must IS NOT NULL THEN
        FOREACH v_requirement IN ARRAY p_requirements_must
        LOOP
            INSERT INTO job_requirements_must (job_id, requirement) VALUES (v_job_id, v_requirement);
        END LOOP;
    END IF;
    
    -- Inserir requisitos desejáveis
    IF p_requirements_nice IS NOT NULL THEN
        FOREACH v_requirement IN ARRAY p_requirements_nice
        LOOP
            INSERT INTO job_requirements_nice (job_id, requirement) VALUES (v_job_id, v_requirement);
        END LOOP;
    END IF;
    
    -- Inserir responsabilidades
    IF p_responsibilities IS NOT NULL THEN
        FOREACH v_responsibility IN ARRAY p_responsibilities
        LOOP
            INSERT INTO job_responsibilities (job_id, responsibility) VALUES (v_job_id, v_responsibility);
        END LOOP;
    END IF;
    
    -- Inserir tags
    IF p_tags IS NOT NULL THEN
        FOREACH v_tag IN ARRAY p_tags
        LOOP
            INSERT INTO job_tags (job_id, tag) VALUES (v_job_id, v_tag);
        END LOOP;
    END IF;
    
    RETURN v_job_id;
END;
$$ LANGUAGE plpgsql;