const scanBtn = document.getElementById('scanBtn');
const targetInput = document.getElementById('targetInput');
const resultsGrid = document.getElementById('resultsGrid');
const statusPill = document.getElementById('statusPill');

function getSelectedModules() {
  return Array.from(document.querySelectorAll('input[type="checkbox"]'))
    .filter((checkbox) => checkbox.checked)
    .map((checkbox) => checkbox.value);
}

function renderModuleCard(title, data) {
  const card = document.createElement('div');
  card.className = 'result-card';

  const header = document.createElement('div');
  header.className = 'result-card-header';

  const h4 = document.createElement('h4');
  h4.textContent = title;

  const kind = document.createElement('span');
  kind.textContent = 'Report';

  header.appendChild(h4);
  header.appendChild(kind);

  const body = document.createElement('div');
  body.className = 'result-content';

  const pre = document.createElement('pre');
  pre.textContent = JSON.stringify(data, null, 2);

  body.appendChild(pre);
  card.appendChild(header);
  card.appendChild(body);
  return card;
}

function clearResults() {
  resultsGrid.innerHTML = '';
}

async function runScan() {
  const target = targetInput.value.trim();
  if (!target) {
    clearResults();
    resultsGrid.innerHTML = '<div class="empty-state">Please enter a target.</div>';
    statusPill.textContent = 'Invalid input';
    return;
  }

  const selectedModules = getSelectedModules();
  clearResults();
  resultsGrid.innerHTML = '<div class="empty-state">Running scan...</div>';
  statusPill.textContent = 'Scanning';

  const requestBody = {
    target,
    modules: selectedModules,
    options: {}
  };

  try {
    const response = await fetch('/api/scan', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(requestBody)
    });

    const data = await response.json();

    if (!response.ok) {
      clearResults();
      resultsGrid.innerHTML = `<div class="empty-state">${data.detail || 'Scan failed.'}</div>`;
      statusPill.textContent = 'Failed';
      return;
    }

    const resultEntries = data.results || {};
    clearResults();

    if (!Object.keys(resultEntries).length) {
      resultsGrid.innerHTML = '<div class="empty-state">No results returned.</div>';
      statusPill.textContent = 'No data';
      return;
    }

    Object.entries(resultEntries).forEach(([key, value]) => {
      resultsGrid.appendChild(renderModuleCard(key.toUpperCase(), value));
    });

    statusPill.textContent = 'Success';
  } catch (error) {
    clearResults();
    resultsGrid.innerHTML = `<div class="empty-state">Request failed: ${error.message}</div>`;
    statusPill.textContent = 'Error';
  }
}

scanBtn.addEventListener('click', runScan);
