// Tab Switching
document.addEventListener('DOMContentLoaded', () => {
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');

    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const tabName = button.dataset.tab;

            // Remove active class from all tabs
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));

            // Add active class to clicked tab
            button.classList.add('active');
            document.getElementById(`${tabName}-tab`).classList.add('active');

            // Clear any previous results/errors
            hideResults();
            hideError();
        });
    });

    // Handle slide mode changes
    const urlSlideMode = document.getElementById('url-slide-mode');
    const urlSlideIndexGroup = document.getElementById('url-slide-index-group');
    const fileSlideMode = document.getElementById('file-slide-mode');
    const fileSlideIndexGroup = document.getElementById('file-slide-index-group');

    urlSlideMode.addEventListener('change', (e) => {
        if (e.target.value === 'single') {
            urlSlideIndexGroup.style.display = 'flex';
        } else {
            urlSlideIndexGroup.style.display = 'none';
        }
    });

    fileSlideMode.addEventListener('change', (e) => {
        if (e.target.value === 'single') {
            fileSlideIndexGroup.style.display = 'flex';
        } else {
            fileSlideIndexGroup.style.display = 'none';
        }
    });

    // URL Form Submit
    const urlForm = document.getElementById('url-form');
    urlForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        await handleUrlSubmit(e.target);
    });

    // File Form Submit
    const fileForm = document.getElementById('file-form');
    fileForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        await handleFileSubmit(e.target);
    });
});

// Handle URL Form Submission
async function handleUrlSubmit(form) {
    const formData = new FormData(form);

    // Validate URL
    const url = formData.get('url');
    if (!url || !url.trim()) {
        showError('Пожалуйста, введите URL');
        return;
    }

    showLoading();
    hideResults();
    hideError();

    try {
        const response = await fetch('/api/analyze-url', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Ошибка при анализе');
        }

        hideLoading();
        displayResults(data);
    } catch (error) {
        hideLoading();
        showError(error.message);
    }
}

// Handle File Form Submission
async function handleFileSubmit(form) {
    const formData = new FormData(form);

    // Validate file
    const file = formData.get('file');
    if (!file || file.size === 0) {
        showError('Пожалуйста, выберите файл');
        return;
    }

    if (!file.name.endsWith('.html')) {
        showError('Только HTML файлы разрешены');
        return;
    }

    showLoading();
    hideResults();
    hideError();

    try {
        const response = await fetch('/api/analyze-file', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Ошибка при анализе');
        }

        hideLoading();
        displayResults(data);
    } catch (error) {
        hideLoading();
        showError(error.message);
    }
}

// Display Results
function displayResults(data) {
    const resultsDiv = document.getElementById('results');
    const resultsContent = document.getElementById('results-content');

    resultsContent.innerHTML = '';

    if (!data.results || data.results.length === 0) {
        resultsContent.innerHTML = '<p>Нет результатов для отображения</p>';
        resultsDiv.classList.remove('hidden');
        return;
    }

    // Create summary card if multiple slides
    if (data.total_slides > 1) {
        const summaryCard = document.createElement('div');
        summaryCard.className = 'result-card';
        summaryCard.innerHTML = `
            <h3>Общая информация</h3>
            <div class="stat">
                <div class="stat-label">Всего слайдов</div>
                <div class="stat-value">${data.total_slides}</div>
            </div>
        `;
        resultsContent.appendChild(summaryCard);
    }

    // Create card for each slide
    data.results.forEach((result, index) => {
        const card = document.createElement('div');
        card.className = 'result-card';

        const summary = result.summary || {};
        const totalEntities = summary.total_entities || 0;
        const passedAA = summary.passed_AA_normal || 0;
        const failedAA = summary.failed_AA_normal || 0;

        card.innerHTML = `
            <h3>Слайд ${result.slide_number}</h3>
            <div class="result-stats">
                <div class="stat">
                    <div class="stat-label">Всего элементов</div>
                    <div class="stat-value">${totalEntities}</div>
                </div>
                <div class="stat">
                    <div class="stat-label">Прошли WCAG AA</div>
                    <div class="stat-value success">${passedAA}</div>
                </div>
                <div class="stat">
                    <div class="stat-label">Не прошли WCAG AA</div>
                    <div class="stat-value danger">${failedAA}</div>
                </div>
            </div>
            <div class="result-actions">
                <a href="${result.report_url}" target="_blank">Открыть отчёт HTML</a>
                <a href="${result.json_url}" target="_blank">Скачать JSON</a>
            </div>
        `;

        resultsContent.appendChild(card);
    });

    resultsDiv.classList.remove('hidden');

    // Scroll to results
    resultsDiv.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// Show Loading
function showLoading() {
    document.getElementById('loading').classList.remove('hidden');
}

// Hide Loading
function hideLoading() {
    document.getElementById('loading').classList.add('hidden');
}

// Show Error
function showError(message) {
    const errorDiv = document.getElementById('error');
    const errorMessage = document.getElementById('error-message');

    errorMessage.textContent = message;
    errorDiv.classList.remove('hidden');

    // Scroll to error
    errorDiv.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// Hide Error
function hideError() {
    document.getElementById('error').classList.add('hidden');
}

// Hide Results
function hideResults() {
    document.getElementById('results').classList.add('hidden');
}
