-- 📊 QUERIES DE ANÁLISE - DADOS DE VAGAS CATHO
-- Execute estas queries no SQL Editor do Supabase para análise dos dados

-- ============================================================================
-- 📈 ESTATÍSTICAS GERAIS
-- ============================================================================

-- Resumo geral do dataset
SELECT 
    'Total de Vagas' as metrica,
    COUNT(*) as valor
FROM jobs
UNION ALL
SELECT 
    'Total de Empresas' as metrica,
    COUNT(DISTINCT company_name) as valor
FROM jobs
WHERE company_name IS NOT NULL
UNION ALL
SELECT 
    'Vagas com Salário' as metrica,
    COUNT(*) as valor
FROM jobs j
INNER JOIN job_salaries s ON j.id = s.job_id
UNION ALL
SELECT 
    'Vagas Remotas' as metrica,
    COUNT(*) as valor
FROM jobs
WHERE work_model ILIKE '%remoto%';

-- ============================================================================
-- 🏢 ANÁLISE DE EMPRESAS
-- ============================================================================

-- Top 20 empresas com mais vagas
SELECT 
    company_name,
    COUNT(*) as total_vagas,
    COUNT(CASE WHEN js.job_id IS NOT NULL THEN 1 END) as vagas_com_salario,
    ROUND(
        COUNT(CASE WHEN js.job_id IS NOT NULL THEN 1 END) * 100.0 / COUNT(*), 
        1
    ) as perc_com_salario
FROM jobs j
LEFT JOIN job_salaries js ON j.id = js.job_id
WHERE company_name IS NOT NULL
GROUP BY company_name
HAVING COUNT(*) >= 5
ORDER BY total_vagas DESC
LIMIT 20;

-- Empresas com melhores salários médios (min 5 vagas)
SELECT 
    j.company_name,
    COUNT(*) as total_vagas,
    ROUND(AVG(js.min_salary), 0) as salario_min_medio,
    ROUND(AVG(js.max_salary), 0) as salario_max_medio,
    ROUND(AVG((js.min_salary + js.max_salary) / 2), 0) as salario_medio
FROM jobs j
INNER JOIN job_salaries js ON j.id = js.job_id
WHERE j.company_name IS NOT NULL
    AND js.min_salary > 0
    AND js.max_salary > 0
GROUP BY j.company_name
HAVING COUNT(*) >= 5
ORDER BY salario_medio DESC
LIMIT 15;

-- ============================================================================
-- 💰 ANÁLISE SALARIAL
-- ============================================================================

-- Distribuição salarial geral
SELECT 
    salary_type,
    COUNT(*) as quantidade,
    ROUND(AVG(min_salary), 0) as salario_min_medio,
    ROUND(AVG(max_salary), 0) as salario_max_medio,
    ROUND(MIN(min_salary), 0) as salario_min_minimo,
    ROUND(MAX(max_salary), 0) as salario_max_maximo
FROM job_salaries 
WHERE min_salary > 0 AND max_salary > 0
GROUP BY salary_type
ORDER BY quantidade DESC;

-- Faixas salariais (baseado no salário médio)
WITH salary_ranges AS (
    SELECT 
        j.id,
        j.title,
        j.company_name,
        (js.min_salary + js.max_salary) / 2 as salario_medio,
        CASE 
            WHEN (js.min_salary + js.max_salary) / 2 <= 2000 THEN 'Até R$ 2.000'
            WHEN (js.min_salary + js.max_salary) / 2 <= 4000 THEN 'R$ 2.001 - R$ 4.000'
            WHEN (js.min_salary + js.max_salary) / 2 <= 6000 THEN 'R$ 4.001 - R$ 6.000'
            WHEN (js.min_salary + js.max_salary) / 2 <= 8000 THEN 'R$ 6.001 - R$ 8.000'
            WHEN (js.min_salary + js.max_salary) / 2 <= 12000 THEN 'R$ 8.001 - R$ 12.000'
            WHEN (js.min_salary + js.max_salary) / 2 <= 20000 THEN 'R$ 12.001 - R$ 20.000'
            ELSE 'Acima de R$ 20.000'
        END as faixa_salarial
    FROM jobs j
    INNER JOIN job_salaries js ON j.id = js.job_id
    WHERE js.min_salary > 0 AND js.max_salary > 0
)
SELECT 
    faixa_salarial,
    COUNT(*) as quantidade_vagas,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) as percentual
FROM salary_ranges
GROUP BY faixa_salarial
ORDER BY 
    CASE faixa_salarial
        WHEN 'Até R$ 2.000' THEN 1
        WHEN 'R$ 2.001 - R$ 4.000' THEN 2
        WHEN 'R$ 4.001 - R$ 6.000' THEN 3
        WHEN 'R$ 6.001 - R$ 8.000' THEN 4
        WHEN 'R$ 8.001 - R$ 12.000' THEN 5
        WHEN 'R$ 12.001 - R$ 20.000' THEN 6
        ELSE 7
    END;

-- ============================================================================
-- 📍 ANÁLISE GEOGRÁFICA
-- ============================================================================

-- Distribuição de vagas por localização
SELECT 
    location,
    COUNT(*) as total_vagas,
    COUNT(CASE WHEN js.job_id IS NOT NULL THEN 1 END) as vagas_com_salario,
    ROUND(AVG((js.min_salary + js.max_salary) / 2), 0) as salario_medio
FROM jobs j
LEFT JOIN job_salaries js ON j.id = js.job_id
WHERE location IS NOT NULL
GROUP BY location
HAVING COUNT(*) >= 10
ORDER BY total_vagas DESC
LIMIT 20;

-- Estados com mais vagas (extraindo estado da localização)
WITH estados AS (
    SELECT 
        j.*,
        js.min_salary,
        js.max_salary,
        CASE 
            WHEN location ILIKE '%SP%' OR location ILIKE '%São Paulo%' THEN 'São Paulo'
            WHEN location ILIKE '%RJ%' OR location ILIKE '%Rio de Janeiro%' THEN 'Rio de Janeiro'
            WHEN location ILIKE '%MG%' OR location ILIKE '%Minas Gerais%' THEN 'Minas Gerais'
            WHEN location ILIKE '%RS%' OR location ILIKE '%Rio Grande do Sul%' THEN 'Rio Grande do Sul'
            WHEN location ILIKE '%PR%' OR location ILIKE '%Paraná%' THEN 'Paraná'
            WHEN location ILIKE '%SC%' OR location ILIKE '%Santa Catarina%' THEN 'Santa Catarina'
            WHEN location ILIKE '%BA%' OR location ILIKE '%Bahia%' THEN 'Bahia'
            WHEN location ILIKE '%GO%' OR location ILIKE '%Goiás%' THEN 'Goiás'
            WHEN location ILIKE '%PE%' OR location ILIKE '%Pernambuco%' THEN 'Pernambuco'
            WHEN location ILIKE '%CE%' OR location ILIKE '%Ceará%' THEN 'Ceará'
            ELSE 'Outros'
        END as estado
    FROM jobs j
    LEFT JOIN job_salaries js ON j.id = js.job_id
    WHERE location IS NOT NULL
)
SELECT 
    estado,
    COUNT(*) as total_vagas,
    ROUND(AVG((min_salary + max_salary) / 2), 0) as salario_medio
FROM estados
WHERE estado != 'Outros'
GROUP BY estado
ORDER BY total_vagas DESC;

-- ============================================================================
-- 💼 ANÁLISE DE MODALIDADES DE TRABALHO
-- ============================================================================

-- Distribuição por modelo de trabalho
SELECT 
    COALESCE(work_model, 'Não informado') as modelo_trabalho,
    COUNT(*) as quantidade,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) as percentual
FROM jobs
GROUP BY work_model
ORDER BY quantidade DESC;

-- Distribuição por tipo de contrato
SELECT 
    COALESCE(contract_type, 'Não informado') as tipo_contrato,
    COUNT(*) as quantidade,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) as percentual
FROM jobs
GROUP BY contract_type
ORDER BY quantidade DESC;

-- Salários por modelo de trabalho
SELECT 
    j.work_model,
    COUNT(*) as total_vagas,
    ROUND(AVG((js.min_salary + js.max_salary) / 2), 0) as salario_medio,
    ROUND(MIN(js.min_salary), 0) as salario_minimo,
    ROUND(MAX(js.max_salary), 0) as salario_maximo
FROM jobs j
INNER JOIN job_salaries js ON j.id = js.job_id
WHERE j.work_model IS NOT NULL
    AND js.min_salary > 0 
    AND js.max_salary > 0
GROUP BY j.work_model
ORDER BY salario_medio DESC;

-- ============================================================================
-- 🎯 ANÁLISE DE HABILIDADES
-- ============================================================================

-- Top 30 habilidades mais demandadas
SELECT 
    skill,
    COUNT(*) as demanda,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(DISTINCT job_id) FROM job_skills), 1) as percentual_vagas
FROM job_skills
GROUP BY skill
ORDER BY demanda DESC
LIMIT 30;

-- Habilidades técnicas vs salário médio
SELECT 
    jsk.skill,
    COUNT(*) as demanda,
    ROUND(AVG((js.min_salary + js.max_salary) / 2), 0) as salario_medio
FROM job_skills jsk
INNER JOIN jobs j ON jsk.job_id = j.id
INNER JOIN job_salaries js ON j.id = js.job_id
WHERE js.min_salary > 0 AND js.max_salary > 0
GROUP BY jsk.skill
HAVING COUNT(*) >= 20
ORDER BY salario_medio DESC
LIMIT 20;

-- ============================================================================
-- 🎓 ANÁLISE DE EDUCAÇÃO
-- ============================================================================

-- Requisitos educacionais mais comuns
SELECT 
    education_level,
    COUNT(*) as quantidade,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(DISTINCT job_id) FROM job_education), 1) as percentual
FROM job_education
GROUP BY education_level
ORDER BY quantidade DESC
LIMIT 15;

-- ============================================================================
-- 🎁 ANÁLISE DE BENEFÍCIOS
-- ============================================================================

-- Benefícios mais oferecidos
SELECT 
    benefit,
    COUNT(*) as quantidade,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(DISTINCT job_id) FROM job_benefits), 1) as percentual_vagas
FROM job_benefits
GROUP BY benefit
ORDER BY quantidade DESC
LIMIT 20;

-- ============================================================================
-- 📊 ANÁLISE TEMPORAL
-- ============================================================================

-- Distribuição de vagas por data de publicação
SELECT 
    published_date,
    COUNT(*) as quantidade_vagas
FROM jobs
WHERE published_date IS NOT NULL
GROUP BY published_date
ORDER BY published_date DESC
LIMIT 10;

-- ============================================================================
-- 🔍 ANÁLISE DE QUALIDADE DOS DADOS
-- ============================================================================

-- Score de qualidade dos dados
SELECT 
    CASE 
        WHEN data_quality_score >= 90 THEN 'Excelente (90-100)'
        WHEN data_quality_score >= 80 THEN 'Boa (80-89)'
        WHEN data_quality_score >= 70 THEN 'Regular (70-79)'
        WHEN data_quality_score >= 60 THEN 'Baixa (60-69)'
        ELSE 'Muito Baixa (<60)'
    END as qualidade,
    COUNT(*) as quantidade,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) as percentual
FROM jobs
WHERE data_quality_score IS NOT NULL
GROUP BY 
    CASE 
        WHEN data_quality_score >= 90 THEN 'Excelente (90-100)'
        WHEN data_quality_score >= 80 THEN 'Boa (80-89)'
        WHEN data_quality_score >= 70 THEN 'Regular (70-79)'
        WHEN data_quality_score >= 60 THEN 'Baixa (60-69)'
        ELSE 'Muito Baixa (<60)'
    END
ORDER BY 
    CASE 
        WHEN qualidade = 'Excelente (90-100)' THEN 1
        WHEN qualidade = 'Boa (80-89)' THEN 2
        WHEN qualidade = 'Regular (70-79)' THEN 3
        WHEN qualidade = 'Baixa (60-69)' THEN 4
        ELSE 5
    END;

-- Completude dos dados por campo
SELECT 
    'Título' as campo,
    COUNT(*) as total,
    COUNT(title) as preenchidos,
    ROUND(COUNT(title) * 100.0 / COUNT(*), 1) as completude_perc
FROM jobs
UNION ALL
SELECT 
    'Empresa' as campo,
    COUNT(*) as total,
    COUNT(company_name) as preenchidos,
    ROUND(COUNT(company_name) * 100.0 / COUNT(*), 1) as completude_perc
FROM jobs
UNION ALL
SELECT 
    'Localização' as campo,
    COUNT(*) as total,
    COUNT(location) as preenchidos,
    ROUND(COUNT(location) * 100.0 / COUNT(*), 1) as completude_perc
FROM jobs
UNION ALL
SELECT 
    'Modelo de Trabalho' as campo,
    COUNT(*) as total,
    COUNT(work_model) as preenchidos,
    ROUND(COUNT(work_model) * 100.0 / COUNT(*), 1) as completude_perc
FROM jobs
UNION ALL
SELECT 
    'Salário' as campo,
    COUNT(*) as total,
    (SELECT COUNT(DISTINCT job_id) FROM job_salaries) as preenchidos,
    ROUND((SELECT COUNT(DISTINCT job_id) FROM job_salaries) * 100.0 / COUNT(*), 1) as completude_perc
FROM jobs
ORDER BY completude_perc DESC;

-- ============================================================================
-- 🎯 QUERIES PARA DASHBOARD
-- ============================================================================

-- KPIs principais (para cards de dashboard)
SELECT 
    (SELECT COUNT(*) FROM jobs) as total_vagas,
    (SELECT COUNT(DISTINCT company_name) FROM jobs WHERE company_name IS NOT NULL) as total_empresas,
    (SELECT COUNT(DISTINCT job_id) FROM job_salaries) as vagas_com_salario,
    (SELECT ROUND(AVG((min_salary + max_salary) / 2), 0) FROM job_salaries WHERE min_salary > 0 AND max_salary > 0) as salario_medio_geral,
    (SELECT COUNT(*) FROM jobs WHERE work_model ILIKE '%remoto%') as vagas_remotas;

-- Tendência salarial por faixa (para gráfico)
WITH salary_trend AS (
    SELECT 
        CASE 
            WHEN (min_salary + max_salary) / 2 <= 3000 THEN 'Até 3k'
            WHEN (min_salary + max_salary) / 2 <= 5000 THEN '3k-5k'
            WHEN (min_salary + max_salary) / 2 <= 8000 THEN '5k-8k'
            WHEN (min_salary + max_salary) / 2 <= 12000 THEN '8k-12k'
            ELSE '12k+'
        END as faixa,
        COUNT(*) as quantidade
    FROM job_salaries
    WHERE min_salary > 0 AND max_salary > 0
    GROUP BY 
        CASE 
            WHEN (min_salary + max_salary) / 2 <= 3000 THEN 'Até 3k'
            WHEN (min_salary + max_salary) / 2 <= 5000 THEN '3k-5k'
            WHEN (min_salary + max_salary) / 2 <= 8000 THEN '5k-8k'
            WHEN (min_salary + max_salary) / 2 <= 12000 THEN '8k-12k'
            ELSE '12k+'
        END
)
SELECT * FROM salary_trend
ORDER BY 
    CASE faixa
        WHEN 'Até 3k' THEN 1
        WHEN '3k-5k' THEN 2
        WHEN '5k-8k' THEN 3
        WHEN '8k-12k' THEN 4
        ELSE 5
    END;