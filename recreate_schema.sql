-- Script para recriar o schema com correções
-- Execute este script no SQL Editor do Supabase

-- Remove tabelas existentes (cuidado: isso apaga todos os dados!)
DROP VIEW IF EXISTS jobs_complete;
DROP TABLE IF EXISTS job_experience CASCADE;
DROP TABLE IF EXISTS job_skills CASCADE;
DROP TABLE IF EXISTS job_education CASCADE;
DROP TABLE IF EXISTS job_benefits CASCADE;
DROP TABLE IF EXISTS job_responsibilities CASCADE;
DROP TABLE IF EXISTS job_salaries CASCADE;
DROP TABLE IF EXISTS jobs CASCADE;
DROP TABLE IF EXISTS companies CASCADE;

-- Remove função se existir
DROP FUNCTION IF EXISTS update_updated_at_column();

-- Agora recria tudo com o schema correto

-- Tabela principal de empresas
CREATE TABLE companies (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índice para busca rápida por nome da empresa
CREATE INDEX idx_companies_name ON companies(name);

-- Tabela principal de vagas
CREATE TABLE jobs (
    id SERIAL PRIMARY KEY,
    external_id TEXT UNIQUE, -- ID do sistema original (agora TEXT)
    title VARCHAR(500) NOT NULL,
    company_id INTEGER REFERENCES companies(id),
    company_name VARCHAR(255), -- Fallback se não houver company_id
    location VARCHAR(255),
    work_type VARCHAR(100), -- remoto, presencial, híbrido
    contract_type VARCHAR(100), -- CLT, PJ, estágio, etc.
    work_model VARCHAR(100),
    description TEXT,
    description_raw TEXT,
    link VARCHAR(1000),
    published_date DATE,
    extraction_timestamp TIMESTAMP WITH TIME ZONE,
    data_quality_score DECIMAL(3,1),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices para otimização de consultas
CREATE INDEX idx_jobs_external_id ON jobs(external_id);
CREATE INDEX idx_jobs_title ON jobs(title);
CREATE INDEX idx_jobs_location ON jobs(location);
CREATE INDEX idx_jobs_work_type ON jobs(work_type);
CREATE INDEX idx_jobs_published_date ON jobs(published_date);
CREATE INDEX idx_jobs_quality_score ON jobs(data_quality_score);

-- Tabela de informações salariais
CREATE TABLE job_salaries (
    id SERIAL PRIMARY KEY,
    job_id INTEGER REFERENCES jobs(id) ON DELETE CASCADE,
    min_salary DECIMAL(10,2),
    max_salary DECIMAL(10,2),
    salary_type VARCHAR(50), -- 'faixa salarial', 'valor mínimo', 'a combinar'
    commission VARCHAR(100), -- percentual ou 'sim'
    currency VARCHAR(10) DEFAULT 'BRL',
    period VARCHAR(20) DEFAULT 'mensal', -- mensal, hora, semanal, diario
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices para consultas salariais
CREATE INDEX idx_salaries_min ON job_salaries(min_salary);
CREATE INDEX idx_salaries_max ON job_salaries(max_salary);
CREATE INDEX idx_salaries_type ON job_salaries(salary_type);

-- Tabela de responsabilidades
CREATE TABLE job_responsibilities (
    id SERIAL PRIMARY KEY,
    job_id INTEGER REFERENCES jobs(id) ON DELETE CASCADE,
    responsibility TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabela de benefícios
CREATE TABLE job_benefits (
    id SERIAL PRIMARY KEY,
    job_id INTEGER REFERENCES jobs(id) ON DELETE CASCADE,
    benefit VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índice para busca de benefícios
CREATE INDEX idx_benefits_name ON job_benefits(benefit);

-- Tabela de formação acadêmica
CREATE TABLE job_education (
    id SERIAL PRIMARY KEY,
    job_id INTEGER REFERENCES jobs(id) ON DELETE CASCADE,
    education_level VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabela de habilidades
CREATE TABLE job_skills (
    id SERIAL PRIMARY KEY,
    job_id INTEGER REFERENCES jobs(id) ON DELETE CASCADE,
    skill VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índice para busca de habilidades
CREATE INDEX idx_skills_name ON job_skills(skill);

-- Tabela de experiência
CREATE TABLE job_experience (
    id SERIAL PRIMARY KEY,
    job_id INTEGER REFERENCES jobs(id) ON DELETE CASCADE,
    experience_description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- View para consulta completa de vagas
CREATE VIEW jobs_complete AS
SELECT 
    j.*,
    c.name as company_full_name,
    js.min_salary,
    js.max_salary,
    js.salary_type,
    js.commission,
    js.currency,
    js.period,
    je.experience_description,
    ARRAY_AGG(DISTINCT jb.benefit) FILTER (WHERE jb.benefit IS NOT NULL) as benefits,
    ARRAY_AGG(DISTINCT jr.responsibility) FILTER (WHERE jr.responsibility IS NOT NULL) as responsibilities,
    ARRAY_AGG(DISTINCT jed.education_level) FILTER (WHERE jed.education_level IS NOT NULL) as education,
    ARRAY_AGG(DISTINCT jsk.skill) FILTER (WHERE jsk.skill IS NOT NULL) as skills
FROM jobs j
LEFT JOIN companies c ON j.company_id = c.id
LEFT JOIN job_salaries js ON j.id = js.job_id
LEFT JOIN job_experience je ON j.id = je.job_id
LEFT JOIN job_benefits jb ON j.id = jb.job_id
LEFT JOIN job_responsibilities jr ON j.id = jr.job_id
LEFT JOIN job_education jed ON j.id = jed.job_id
LEFT JOIN job_skills jsk ON j.id = jsk.job_id
GROUP BY j.id, c.name, js.min_salary, js.max_salary, js.salary_type, js.commission, js.currency, js.period, je.experience_description;

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
COMMENT ON TABLE jobs IS 'Tabela principal de vagas de emprego';
COMMENT ON TABLE job_salaries IS 'Informações salariais das vagas';
COMMENT ON TABLE job_responsibilities IS 'Responsabilidades e atividades das vagas';
COMMENT ON TABLE job_benefits IS 'Benefícios oferecidos pelas vagas';
COMMENT ON TABLE job_education IS 'Requisitos de formação acadêmica';
COMMENT ON TABLE job_skills IS 'Habilidades e competências requeridas';
COMMENT ON TABLE job_experience IS 'Requisitos de experiência profissional';

-- Mensagem de sucesso
SELECT 'Schema recriado com sucesso! Agora external_id é TEXT.' as status;