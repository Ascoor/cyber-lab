const apiBase = '';

function escapeHtml(value) {
  return String(value ?? '').replace(/[&<>"']/g, (char) => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  }[char]));
}

async function requestJson(url, options = {}) {
  const response = await fetch(apiBase + url, {
    headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
    ...options,
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data.detail || data.message || `HTTP ${response.status}`);
  }
  return data;
}

function showMessage(type, message) {
  const box = document.getElementById('messageBox');
  box.className = `message ${type}`;
  box.textContent = message;
  box.classList.remove('hidden');
}

async function checkHealth() {
  const result = document.getElementById('healthResult');
  const status = document.getElementById('backendStatus');
  result.textContent = 'Loading...';
  try {
    const data = await requestJson('/health');
    result.textContent = JSON.stringify(data, null, 2);
    status.textContent = 'Backend: ok';
    status.className = 'status-pill ok';
  } catch (error) {
    result.textContent = error.message;
    status.textContent = 'Backend: error';
    status.className = 'status-pill error';
  }
}

async function loadTargets() {
  try {
    const data = await requestJson('/targets');
    renderTargets(data.targets || []);
  } catch (error) {
    showMessage('error', `فشل تحميل الأهداف: ${error.message}`);
  }
}

async function addTarget() {
  const payload = {
    name: document.getElementById('targetName').value,
    target: document.getElementById('targetValue').value,
    authorized: document.getElementById('targetAuthorized').checked,
    scope_notes: document.getElementById('targetScopeNotes').value || null,
  };
  try {
    await requestJson('/targets', { method: 'POST', body: JSON.stringify(payload) });
    showMessage('success', 'تمت إضافة الهدف بنجاح.');
    document.getElementById('targetForm').reset();
    await loadTargets();
  } catch (error) {
    showMessage('error', `فشل إضافة الهدف: ${error.message}`);
  }
}

async function toggleAuthorization(targetId, currentValue) {
  try {
    await requestJson(`/targets/${targetId}/authorization`, {
      method: 'PATCH',
      body: JSON.stringify({ authorized: !currentValue }),
    });
    showMessage('success', 'تم تحديث حالة التصريح.');
    await loadTargets();
  } catch (error) {
    showMessage('error', `فشل تحديث التصريح: ${error.message}`);
  }
}

async function deleteTarget(targetId) {
  if (!confirm(`هل تريد حذف الهدف رقم ${targetId}؟`)) return;
  try {
    await requestJson(`/targets/${targetId}`, { method: 'DELETE' });
    showMessage('success', 'تم حذف الهدف.');
    await loadTargets();
  } catch (error) {
    showMessage('error', `فشل حذف الهدف: ${error.message}`);
  }
}

async function runNmapBasic(targetId) {
  const container = document.getElementById('nmapResult');
  container.textContent = 'Loading... تشغيل Nmap Basic على target_id فقط.';
  try {
    const result = await requestJson('/scans/nmap/basic', {
      method: 'POST',
      body: JSON.stringify({ target_id: targetId }),
    });
    renderNmapResult(result);
  } catch (error) {
    container.textContent = `Error: ${error.message}`;
  }
}

function renderTargets(targets) {
  const body = document.getElementById('targetsTableBody');
  if (!targets.length) {
    body.innerHTML = '<tr><td colspan="8">لا توجد أهداف.</td></tr>';
    return;
  }
  body.innerHTML = targets.map((target) => {
    const authorized = Boolean(target.authorized);
    return `<tr>
      <td>${target.id}</td>
      <td>${escapeHtml(target.name)}</td>
      <td>${escapeHtml(target.target)}</td>
      <td>${escapeHtml(target.target_type)}</td>
      <td><span class="badge ${authorized ? 'ok' : 'no'}">${authorized}</span></td>
      <td>${escapeHtml(target.scope_notes || '')}</td>
      <td>${escapeHtml(target.created_at)}</td>
      <td><div class="actions">
        <button class="btn warning" onclick="toggleAuthorization(${target.id}, ${authorized})">Toggle Authorized</button>
        <button class="btn danger" onclick="deleteTarget(${target.id})">Delete</button>
        <button class="btn primary" ${authorized ? '' : 'disabled title="authorized=false"'} onclick="runNmapBasic(${target.id})">Run Nmap Basic</button>
      </div></td>
    </tr>`;
  }).join('');
}

function renderNmapResult(result) {
  const container = document.getElementById('nmapResult');
  container.innerHTML = `<div class="result-grid">
    <div><strong>success</strong><pre>${escapeHtml(result.success)}</pre></div>
    <div><strong>target</strong><pre>${escapeHtml(result.target)}</pre></div>
    <div><strong>command_used</strong><pre>${escapeHtml((result.command_used || []).join(' '))}</pre></div>
    <div><strong>report_file</strong><pre>${escapeHtml(result.report_file)}</pre></div>
    <div class="wide"><strong>summary</strong><pre>${escapeHtml(JSON.stringify(result.summary || null, null, 2))}</pre></div>
    <div class="wide"><strong>parsed_result</strong><pre>${escapeHtml(JSON.stringify(result.parsed_result || null, null, 2))}</pre></div>
    <div class="wide"><strong>stdout</strong><textarea class="output" readonly>${escapeHtml(result.stdout || '')}</textarea></div>
    <div class="wide"><strong>stderr</strong><pre>${escapeHtml(result.stderr || '')}</pre></div>
  </div>`;
}

document.getElementById('targetForm').addEventListener('submit', (event) => {
  event.preventDefault();
  addTarget();
});

document.addEventListener('DOMContentLoaded', () => {
  checkHealth();
  loadTargets();
});
