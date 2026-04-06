console.log('Script loaded');

let selectedPresets = [];
let currentCategory = 'all';
let searchQuery = '';

window.switchTab = function(tabName) {
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
  document.querySelector(`[onclick="switchTab('${tabName}')"]`).classList.add('active');
  document.getElementById(`${tabName}-tab`).classList.add('active');
  if (tabName === 'huggingface') switchHFMethod('url');
}

window.switchHFMethod = function(method) {
  document.querySelectorAll('#huggingface-tab > .tabs .tab').forEach(t => t.classList.remove('active'));
  document.querySelector(`#huggingface-tab [onclick="switchHFMethod('${method}')"]`).classList.add('active');
  document.getElementById('hf-url-form').style.display = method === 'url' ? 'block' : 'none';
  document.getElementById('hf-repo-form').style.display = method === 'repo' ? 'block' : 'none';
}

window.togglePreset = function(presetId) {
  const card = document.querySelector(`[data-preset="${presetId}"]`);
  if (selectedPresets.includes(presetId)) {
    selectedPresets = selectedPresets.filter(p => p !== presetId);
    card.classList.remove('selected');
  } else {
    selectedPresets.push(presetId);
    card.classList.add('selected');
  }
  const btn = document.getElementById('download-presets-btn');
  btn.disabled = selectedPresets.length === 0;
  btn.textContent = selectedPresets.length > 0
    ? `📥 Скачать выбранные пресеты (${selectedPresets.length})`
    : '📥 Скачать выбранные пресеты';
}

window.filterByCategory = function(category, event) {
  currentCategory = category;
  document.querySelectorAll('.category-filter').forEach(f => f.classList.remove('active'));
  if (event && event.target) event.target.closest('.category-filter').classList.add('active');
  applyFilters();
}

window.filterPresets = function() {
  searchQuery = document.getElementById('preset-search').value.toLowerCase().trim();
  applyFilters();
}

window.applyFilters = function() {
  document.querySelectorAll('.preset-card').forEach(card => {
    const catMatch = currentCategory === 'all' || card.dataset.category === currentCategory;
    const name = card.querySelector('.preset-name').textContent.toLowerCase();
    const desc = card.querySelector('.preset-desc').textContent.toLowerCase();
    const searchMatch = !searchQuery || name.includes(searchQuery) || desc.includes(searchQuery);
    card.classList.toggle('hidden', !(catMatch && searchMatch));
  });
}

window.downloadPresets = function() {
  if (selectedPresets.length === 0) return;
  const progress = document.getElementById('preset-progress');
  const result = document.getElementById('preset-result');
  const btn = document.getElementById('download-presets-btn');
  progress.style.display = 'block';
  result.textContent = '';
  btn.disabled = true;
  btn.textContent = 'Загрузка...';
  const fd = new FormData();
  fd.append('presets', selectedPresets.join(','));
  fetch('/download_presets', { method: 'POST', body: fd })
    .then(r => r.json())
    .then(data => {
      result.textContent = data.message;
      if (data.task_id) pollStatus(data.task_id);
      else { progress.style.display = 'none'; btn.disabled = false; btn.textContent = '📥 Скачать выбранные пресеты'; }
    })
    .catch(e => { result.textContent = '❌ ' + e.message; progress.style.display = 'none'; btn.disabled = false; btn.textContent = '📥 Скачать выбранные пресеты'; });
}

window.pollStatus = function(taskId) {
  fetch(`/status/${taskId}`)
    .then(r => r.json())
    .then(data => {
      const result = document.getElementById('preset-result');
      const fill = document.getElementById('preset-progress-fill');
      const text = document.getElementById('preset-progress-text');
      const btn = document.getElementById('download-presets-btn');
      result.textContent = data.message || '';
      if (data.status === 'completed' || data.status === 'error') {
        document.getElementById('preset-progress').style.display = 'none';
        btn.disabled = false;
        btn.textContent = '📥 Скачать выбранные пресеты';
      } else {
        fill.style.width = (data.progress || 0) + '%';
        text.textContent = data.message || 'Загрузка...';
        setTimeout(() => pollStatus(taskId), 500);
      }
    });
}

// HuggingFace forms
document.addEventListener('DOMContentLoaded', function() {
  const urlForm = document.getElementById('hf-url-form');
  const repoForm = document.getElementById('hf-repo-form');

  urlForm.addEventListener('submit', function(e) {
    e.preventDefault();
    const url = document.getElementById('hf_url').value;
    const folder = document.getElementById('hf_url_folder').value;
    startHFDownload('/download_url', { url, folder });
  });

  repoForm.addEventListener('submit', function(e) {
    e.preventDefault();
    const repo = document.getElementById('hf_repo').value;
    const filename = document.getElementById('hf_file').value;
    const token = document.getElementById('hf_token').value;
    const folder = document.getElementById('hf_folder').value;
    startHFDownload('/download_hf', { repo, filename, token, folder });
  });
});

function startHFDownload(endpoint, params) {
  const progress = document.getElementById('hf-progress');
  const result = document.getElementById('hf-result');
  progress.style.display = 'block';
  result.textContent = '';
  const fd = new FormData();
  Object.entries(params).forEach(([k, v]) => fd.append(k, v));
  fetch(endpoint, { method: 'POST', body: fd })
    .then(r => r.json())
    .then(data => {
      result.textContent = data.message;
      if (data.task_id) pollHFStatus(data.task_id);
      else progress.style.display = 'none';
    })
    .catch(e => { result.textContent = '❌ ' + e.message; progress.style.display = 'none'; });
}

function pollHFStatus(taskId) {
  fetch(`/status/${taskId}`)
    .then(r => r.json())
    .then(data => {
      document.getElementById('hf-result').textContent = data.message || '';
      document.getElementById('hf-progress-fill').style.width = (data.progress || 0) + '%';
      document.getElementById('hf-progress-text').textContent = data.message || 'Загрузка...';
      if (data.status === 'completed' || data.status === 'error') {
        document.getElementById('hf-progress').style.display = 'none';
      } else {
        setTimeout(() => pollHFStatus(taskId), 500);
      }
    });
}
