// Global variables
let companies = [];
let currentSymbol = null;

document.addEventListener('DOMContentLoaded', function() {
    loadCompanies();
    setupSearchFilter();
    updateLastUpdatedTime();
});

async function loadCompanies() {
    const loadingEl = document.getElementById('companiesLoading');
    const listEl = document.getElementById('companiesList');
    const errorEl = document.getElementById('companiesError');
    
    try {
        showElement(loadingEl);
        hideElement(listEl);
        hideElement(errorEl);
        
        const response = await fetch('/api/companies');
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        companies = data.companies;
        renderCompaniesList(companies);
        
        hideElement(loadingEl);
        showElement(listEl);
        
    } catch (error) {
        console.error('Error loading companies:', error);
        hideElement(loadingEl);
        showElement(errorEl);
    }
}

// Render the companies list in the sidebar
function renderCompaniesList(companiesToShow) {
    const listEl = document.getElementById('companiesList');
    
    if (!companiesToShow || companiesToShow.length === 0) {
        listEl.innerHTML = '<div class="text-muted text-center py-3">No companies found</div>';
        return;
    }
    
    const html = companiesToShow.map(company => {
        const escapedSymbol = escapeHtml(company.symbol);
        const escapedName = escapeHtml(company.name);
        
        return `
            <div class="company-item" data-symbol="${escapedSymbol}" onclick="selectCompany('${escapedSymbol}', '${escapedName}')">
                <div class="company-symbol">${escapedSymbol}</div>
                <div class="company-name">${escapedName}</div>
            </div>
        `;
    }).join('');
    
    listEl.innerHTML = html;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Handle company selection
async function selectCompany(symbol, name) {
    symbol = symbol ? symbol.toString().trim().toUpperCase() : '';
    name = name ? name.toString().trim() : '';
    
    if (!symbol) {
        showChartError('Invalid company symbol');
        return;
    }
    
    updateSelectedCompany(symbol);
    
    updateChartTitle(symbol, name);
    
    showChartLoading();
    
    updateLastUpdatedTime();
    
    try {
        const stockData = await fetchStockData(symbol);
        
        if (stockData.error) {
            showChartError(stockData.error);
            return;
        }
        
        updateChart(stockData);
        updateStatsCards(stockData);

        updatePredictionCard('--');

        fetchPrediction(symbol).catch(err => {
            console.error('Error fetching prediction:', err);
        });
        
        currentSymbol = symbol;
        
    } catch (error) {
        console.error('Error fetching stock data:', error);
        showChartError('Failed to fetch stock data. Please try again.');
    } finally {
        hideChartLoading();
    }
}

async function fetchStockData(symbol) {
    try {
        const response = await fetch(`/api/stock/${symbol}`);

        if (!response.ok) {
            let detail = '';
            try {
                const errBody = await response.json();
                detail = errBody?.detail || '';
            } catch (_) {
                try { detail = await response.text(); } catch (_) {}
            }

            if (response.status === 429) {
                throw new Error(detail || 'Rate limit reached. Please wait a minute and try again.');
            } else if (response.status === 404) {
                throw new Error(detail || 'Stock symbol not found');
            } else if (response.status === 502) {
                throw new Error(detail || 'Upstream data unavailable. Please try again.');
            } else if (response.status === 503) {
                throw new Error(detail || 'Service temporarily unavailable. Please try again shortly.');
            } else if (response.status >= 500) {
                throw new Error(detail || 'Server error occurred');
            } else if (response.status >= 400) {
                throw new Error(detail || 'Invalid request');
            } else {
                throw new Error('Unexpected response');
            }
        }

        const data = await response.json();
        return data;
    } catch (error) {
        if (error instanceof TypeError && error.message.includes('fetch')) {
            throw new Error('Network connection failed');
        }
        throw error;
    }
}

function updateSelectedCompany(symbol) {
    document.querySelectorAll('.company-item').forEach(item => {
        item.classList.remove('active');
    });
    
    const selectedItem = document.querySelector(`[data-symbol="${symbol}"]`);
    if (selectedItem) {
        selectedItem.classList.add('active');
    }
}

function updateChartTitle(symbol, name) {
    const titleEl = document.getElementById('chartTitle');
    const subtitleEl = document.getElementById('chartSubtitle');
    
    if (titleEl) titleEl.textContent = `${name} (${symbol})`;
    if (subtitleEl) subtitleEl.textContent = 'Historical price data for the last year';
}

function showChartLoading() {
    hideElement(document.getElementById('chartPlaceholder'));
    hideElement(document.getElementById('chartError'));
    showElement(document.getElementById('chartLoading'));
}

function hideChartLoading() {
    hideElement(document.getElementById('chartLoading'));
}

function showChartError(message) {
    const errorEl = document.getElementById('chartError');
    const messageEl = document.getElementById('chartErrorMessage');
    
    if (messageEl) messageEl.textContent = message;
    
    hideElement(document.getElementById('chartPlaceholder'));
    hideElement(document.getElementById('chartLoading'));
    showElement(errorEl);
}

function updateStatsCards(stockData) {
    updateStatCard('latestClose', stockData.latestClose, '$');
    
    updateStatCard('fiftyTwoWeekHigh', stockData.fiftyTwoWeekHigh, '$');
    
    updateStatCard('fiftyTwoWeekLow', stockData.fiftyTwoWeekLow, '$');
    
    updateStatCard('averageVolume', formatVolume(stockData.averageVolume), '');
}

async function fetchPrediction(symbol, days = 30) {
    const response = await fetch(`/api/predict/${symbol}?days=${days}`);
    if (!response.ok) {
        throw new Error(`Prediction request failed with status ${response.status}`);
    }
    const data = await response.json();
    if (data && typeof data.predictedClose === 'number') {
        updatePredictionCard(`$${data.predictedClose}`);
    } else {
        updatePredictionCard('--');
    }
}

function updatePredictionCard(value) {
    updateStatCard('predictedClose', value, value && String(value).startsWith('$') ? '' : '$');
}

function updateStatCard(elementId, value, prefix = '') {
    const element = document.getElementById(elementId);
    if (element) {
        const displayValue = value !== null && value !== undefined ? value : '--';
        element.textContent = `${prefix}${displayValue}`;
    }
}

function formatVolume(volume) {
    if (volume >= 1000000) {
        return (volume / 1000000).toFixed(1) + 'M';
    } else if (volume >= 1000) {
        return (volume / 1000).toFixed(1) + 'K';
    }
    return volume.toLocaleString();
}

function setupSearchFilter() {
    const searchInput = document.getElementById('companySearch');
    if (!searchInput) return;
    
    searchInput.addEventListener('input', function(e) {
        const searchTerm = e.target.value.toLowerCase();
        
        if (searchTerm === '') {
            renderCompaniesList(companies);
        } else {
            const filtered = companies.filter(company => 
                company.name.toLowerCase().includes(searchTerm) ||
                company.symbol.toLowerCase().includes(searchTerm)
            );
            renderCompaniesList(filtered);
        }
    });
}

function updateLastUpdatedTime() {
    const lastUpdatedEl = document.getElementById('lastUpdated');
    if (lastUpdatedEl) {
        const now = new Date();
        lastUpdatedEl.textContent = now.toLocaleTimeString();
    }
}

function showElement(element) {
    if (element) element.style.display = 'block';
}

function hideElement(element) {
    if (element) element.style.display = 'none';
}

function refreshCurrentStock() {
    if (currentSymbol) {
        const companyItem = document.querySelector(`[data-symbol="${currentSymbol}"]`);
        if (companyItem) {
            const companyName = companies.find(c => c.symbol === currentSymbol)?.name || '';
            selectCompany(currentSymbol, companyName);
        }
    }
}

document.addEventListener('keydown', function(e) {
    if (e.key === 'F5' || (e.ctrlKey && e.key === 'r')) {
        e.preventDefault();
        refreshCurrentStock();
    }
    
    if (e.ctrlKey && e.key === 'f') {
        e.preventDefault();
        const searchInput = document.getElementById('companySearch');
        if (searchInput) searchInput.focus();
    }
});
