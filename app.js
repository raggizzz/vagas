// Variáveis globais
let currentPage = 1;
let totalJobs = 0;
let currentFilters = {
    search: '',
    location: '',
    company: '',
    minSalary: '',
    maxSalary: ''
};

// Inicialização da aplicação
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    setupEventListeners();
    loadJobs();
    loadStatistics();
}

// Configurar event listeners
function setupEventListeners() {
    // Busca
    const searchInput = document.getElementById('searchInput');
    const searchButton = document.getElementById('searchButton');
    
    if (searchInput) {
        searchInput.addEventListener('input', debounce(handleSearch, CONFIG.DEBOUNCE_DELAY));
    }
    
    if (searchButton) {
        searchButton.addEventListener('click', handleSearch);
    }

    // Filtros
    const locationFilter = document.getElementById('locationFilter');
    const companyFilter = document.getElementById('companyFilter');
    const minSalaryFilter = document.getElementById('minSalaryFilter');
    const maxSalaryFilter = document.getElementById('maxSalaryFilter');
    const clearFiltersBtn = document.getElementById('clearFilters');
    
    if (locationFilter) locationFilter.addEventListener('change', handleFilterChange);
    if (companyFilter) companyFilter.addEventListener('change', handleFilterChange);
    if (minSalaryFilter) minSalaryFilter.addEventListener('input', handleFilterChange);
    if (maxSalaryFilter) maxSalaryFilter.addEventListener('input', handleFilterChange);
    if (clearFiltersBtn) clearFiltersBtn.addEventListener('click', clearFilters);

    // Modal
    const closeModal = document.getElementById('closeModal');
    const jobModal = document.getElementById('jobModal');
    
    if (closeModal) closeModal.addEventListener('click', closeJobModal);
    if (jobModal) {
        jobModal.addEventListener('click', function(e) {
            if (e.target === this) closeJobModal();
        });
    }
}

// Carregar vagas
async function loadJobs(page = 1) {
    try {
        showLoading(true);
        
        let query = supabase
            .from('jobs')
            .select(`
                *,
                companies(name),
                job_salaries(min_salary, max_salary, currency)
            `);

        // Aplicar filtros
        if (currentFilters.search) {
            query = query.or(`title.ilike.%${currentFilters.search}%,description.ilike.%${currentFilters.search}%`);
        }
        
        if (currentFilters.location) {
            query = query.ilike('location', `%${currentFilters.location}%`);
        }
        
        if (currentFilters.company) {
            query = query.eq('companies.name', currentFilters.company);
        }

        // Paginação
        const startIndex = (page - 1) * CONFIG.ITEMS_PER_PAGE;
        query = query.range(startIndex, startIndex + CONFIG.ITEMS_PER_PAGE - 1);

        const { data: jobs, error, count } = await query;

        if (error) throw error;

        totalJobs = count;
        currentPage = page;
        
        displayJobs(jobs);
        updatePagination();
        
    } catch (error) {
        console.error('Erro ao carregar vagas:', error);
        showError('Erro ao carregar vagas. Tente novamente.');
    } finally {
        showLoading(false);
    }
}

// Exibir vagas
function displayJobs(jobs) {
    const container = document.getElementById('jobsContainer');
    
    if (!jobs || jobs.length === 0) {
        container.innerHTML = '<div class="no-jobs">Nenhuma vaga encontrada.</div>';
        return;
    }

    container.innerHTML = jobs.map(job => createJobCard(job)).join('');
}

// Criar card de vaga
function createJobCard(job) {
    const salary = job.job_salaries?.[0];
    const salaryText = salary ? 
        `${salary.currency || 'R$'} ${formatCurrency(salary.min_salary)} - ${formatCurrency(salary.max_salary)}` : 
        'Salário não informado';

    return `
        <div class="job-card" onclick="openJobModal(${job.id})">
            <div class="job-header">
                <h3 class="job-title">${job.title}</h3>
                <span class="job-company">${job.companies?.name || job.company_name || 'Empresa não informada'}</span>
            </div>
            <div class="job-info">
                <div class="job-location">
                    <i class="icon-location"></i>
                    ${job.location || 'Localização não informada'}
                </div>
                <div class="job-salary">
                    <i class="icon-money"></i>
                    ${salaryText}
                </div>
            </div>
            <div class="job-description">
                ${truncateText(job.description, 150)}
            </div>
            <div class="job-footer">
                <span class="job-date">${formatDate(job.created_at)}</span>
                <button class="btn-view-details">Ver detalhes</button>
            </div>
        </div>
    `;
}

// Abrir modal de detalhes da vaga
async function openJobModal(jobId) {
    try {
        showLoading(true);
        
        const { data: job, error } = await supabase
            .from('jobs')
            .select(`
                *,
                companies(name),
                job_salaries(min_salary, max_salary, currency),
                job_responsibilities(responsibility),
                job_benefits(benefit)
            `)
            .eq('id', jobId)
            .single();

        if (error) throw error;

        displayJobDetails(job);
        document.getElementById('jobModal').style.display = 'block';
        
    } catch (error) {
        console.error('Erro ao carregar detalhes da vaga:', error);
        showError('Erro ao carregar detalhes da vaga.');
    } finally {
        showLoading(false);
    }
}

// Exibir detalhes da vaga no modal
function displayJobDetails(job) {
    const modalContent = document.getElementById('modalJobContent');
    
    // Formatar informações salariais
    let salaryInfo = 'Não informado';
    if (job.job_salaries && job.job_salaries.length > 0) {
        const salary = job.job_salaries[0];
        if (salary.min_salary && salary.max_salary) {
            salaryInfo = `${formatCurrency(salary.min_salary)} - ${formatCurrency(salary.max_salary)}`;
        } else if (salary.min_salary) {
            salaryInfo = `A partir de ${formatCurrency(salary.min_salary)}`;
        }
    }

    const experience = job.job_experience?.[0];
    const experienceText = experience ? 
        `${experience.min_years} - ${experience.max_years} anos` : 
        'Não especificado';

    // Formatar responsabilidades
    let responsibilitiesHtml = '';
    if (job.job_responsibilities && job.job_responsibilities.length > 0) {
        responsibilitiesHtml = `
            <div class="job-section">
                <h3>Responsabilidades</h3>
                <ul>
                    ${job.job_responsibilities.map(r => `<li>${r.responsibility}</li>`).join('')}
                </ul>
            </div>
        `;
    }

    // Formatar benefícios
    let benefitsHtml = '';
    if (job.job_benefits && job.job_benefits.length > 0) {
        benefitsHtml = `
            <div class="job-section">
                <h3>Benefícios</h3>
                <ul>
                    ${job.job_benefits.map(b => `<li>${b.benefit}</li>`).join('')}
                </ul>
            </div>
        `;
    }

    modalContent.innerHTML = `
        <h2>${job.title}</h2>
        <div class="job-meta">
            <div class="meta-item">
                <strong>Empresa:</strong> ${job.companies?.name || job.company_name || 'Não informada'}
            </div>
            <div class="meta-item">
                <strong>Localização:</strong> ${job.location || 'Não informada'}
            </div>
            <div class="meta-item">
                <strong>Salário:</strong> ${salaryInfo}
            </div>
            <div class="meta-item">
                <strong>Experiência:</strong> ${experienceText}
            </div>
            <div class="meta-item">
                <strong>Educação:</strong> ${job.job_education?.[0]?.education_level || 'Não especificado'}
            </div>
        </div>
        
        <div class="job-section">
            <h3>Descrição</h3>
            <p>${job.description}</p>
        </div>
        
        ${responsibilitiesHtml}
        ${benefitsHtml}
        
        ${job.job_skills?.length ? `
            <div class="job-section">
                <h3>Habilidades Requeridas</h3>
                <div class="skills-list">
                    ${job.job_skills.map(s => `<span class="skill-tag">${s.skill_name} (${s.required_level})</span>`).join('')}
                </div>
            </div>
        ` : ''}
        
        <div class="job-actions">
            <button class="btn-primary" onclick="window.open('${job.external_url}', '_blank')">Candidatar-se</button>
        </div>
    `;
}

// Fechar modal
function closeJobModal() {
    document.getElementById('jobModal').style.display = 'none';
}

// Manipular busca
function handleSearch(event) {
    if (event && event.target) {
        currentFilters.search = event.target.value;
    } else {
        currentFilters.search = document.getElementById('searchInput').value;
    }
    currentPage = 1;
    loadJobs();
}

// Manipular mudança de filtros
function handleFilterChange() {
    currentFilters.location = document.getElementById('locationFilter').value;
    currentFilters.company = document.getElementById('companyFilter').value;
    currentFilters.minSalary = document.getElementById('minSalaryFilter').value;
    currentFilters.maxSalary = document.getElementById('maxSalaryFilter').value;
    
    currentPage = 1;
    loadJobs();
}

// Limpar filtros
function clearFilters() {
    currentFilters = {
        search: '',
        location: '',
        company: '',
        minSalary: '',
        maxSalary: ''
    };
    
    document.getElementById('searchInput').value = '';
    document.getElementById('locationFilter').value = '';
    document.getElementById('companyFilter').value = '';
    document.getElementById('minSalaryFilter').value = '';
    document.getElementById('maxSalaryFilter').value = '';
    
    currentPage = 1;
    loadJobs();
}

// Carregar estatísticas
async function loadStatistics() {
    try {
        const [jobsCount, companiesCount, avgSalary] = await Promise.all([
            supabase.from('jobs').select('*', { count: 'exact', head: true }),
            supabase.from('companies').select('*', { count: 'exact', head: true }),
            supabase.from('job_salaries').select('min_salary, max_salary')
        ]);

        document.getElementById('totalJobs').textContent = jobsCount.count || 0;
        document.getElementById('totalCompanies').textContent = companiesCount.count || 0;
        
        if (avgSalary.data && avgSalary.data.length > 0) {
            const salaries = avgSalary.data.filter(s => s.min_salary && s.max_salary);
            if (salaries.length > 0) {
                const avgValue = salaries.reduce((sum, s) => sum + (s.min_salary + s.max_salary) / 2, 0) / salaries.length;
                document.getElementById('avgSalary').textContent = formatCurrency(avgValue);
            } else {
                document.getElementById('avgSalary').textContent = 'N/A';
            }
        } else {
            document.getElementById('avgSalary').textContent = 'N/A';
        }
        
    } catch (error) {
        console.error('Erro ao carregar estatísticas:', error);
        document.getElementById('totalJobs').textContent = '0';
        document.getElementById('totalCompanies').textContent = '0';
        document.getElementById('avgSalary').textContent = 'N/A';
    }
}

// Atualizar paginação
function updatePagination() {
    const totalPages = Math.ceil(totalJobs / CONFIG.ITEMS_PER_PAGE);
    const pagination = document.getElementById('pagination');
    
    let paginationHTML = '';
    
    // Botão anterior
    if (currentPage > 1) {
        paginationHTML += `<button onclick="loadJobs(${currentPage - 1})">Anterior</button>`;
    }
    
    // Números das páginas
    const startPage = Math.max(1, currentPage - 2);
    const endPage = Math.min(totalPages, currentPage + 2);
    
    for (let i = startPage; i <= endPage; i++) {
        const activeClass = i === currentPage ? 'active' : '';
        paginationHTML += `<button class="${activeClass}" onclick="loadJobs(${i})">${i}</button>`;
    }
    
    // Botão próximo
    if (currentPage < totalPages) {
        paginationHTML += `<button onclick="loadJobs(${currentPage + 1})">Próximo</button>`;
    }
    
    pagination.innerHTML = paginationHTML;
}

// Funções utilitárias
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function formatCurrency(value) {
    if (!value) return '0';
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(value).replace('R$', '').trim();
}

function formatDate(dateString) {
    if (!dateString) return '';
    return new Date(dateString).toLocaleDateString('pt-BR');
}

function truncateText(text, maxLength) {
    if (!text) return '';
    return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
}

function showLoading(show) {
    const loading = document.getElementById('loading');
    if (loading) {
        loading.style.display = show ? 'block' : 'none';
    }
}

function showError(message) {
    alert(message); // Pode ser substituído por um sistema de notificação mais sofisticado
}