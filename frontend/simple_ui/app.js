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
    await loadScanHistory();
  } catch (error) {
    container.textContent = `Error: ${error.message}`;
  }
}

async function runDomainArchive(targetId) {
  const container = document.getElementById('domainArchiveResult');
  container.textContent = 'Loading... تشغيل Domain Archive على target_id فقط.';
  try {
    const result = await requestJson('/scans/domain/archive', {
      method: 'POST',
      body: JSON.stringify({ target_id: targetId }),
    });
    renderDomainArchiveResult(result);
    await loadScanHistory();
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
    const domainArchiveAllowed = authorized && ['domain', 'url'].includes(target.target_type);
    const domainArchiveTitle = domainArchiveAllowed ? '' : 'disabled title="requires authorized domain/url target"';
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
        <button class="btn secondary" ${domainArchiveTitle} onclick="runDomainArchive(${target.id})">Domain Archive</button>
      </div></td>
    </tr>`;
  }).join('');
}


async function loadScanHistory() {
  const body = document.getElementById('scanHistoryTableBody');
  if (body) body.innerHTML = '<tr><td colspan="10">Loading...</td></tr>';
  try {
    const data = await requestJson('/scans');
    renderScanHistory(data.scans || []);
  } catch (error) {
    if (body) body.innerHTML = `<tr><td colspan="10">فشل تحميل سجل الفحوصات: ${escapeHtml(error.message)}</td></tr>`;
  }
}

function renderScanHistory(scans) {
  const body = document.getElementById('scanHistoryTableBody');
  if (!scans.length) {
    body.innerHTML = '<tr><td colspan="10">لا توجد فحوصات.</td></tr>';
    return;
  }
  body.innerHTML = scans.map((scan) => {
    const success = Boolean(scan.success);
    const statusClass = scan.status === 'completed' ? 'ok' : 'no';
    return `<tr>
      <td>${escapeHtml(scan.scan_id || scan.id)}</td>
      <td>${escapeHtml(scan.scan_type)}</td>
      <td>${escapeHtml(scan.target)}</td>
      <td><span class="badge ${success ? 'ok' : 'no'}">${success}</span></td>
      <td><span class="badge ${statusClass}">${escapeHtml(scan.status)}</span></td>
      <td class="summary-cell">${escapeHtml(scan.summary || '')}</td>
      <td>${escapeHtml(scan.started_at || '')}</td>
      <td>${escapeHtml(scan.finished_at || '')}</td>
      <td>${escapeHtml(scan.report_file || '')}</td>
      <td><button class="btn primary" type="button" onclick="viewScanReport(${Number(scan.scan_id || scan.id)})">View Report</button></td>
    </tr>`;
  }).join('');
}

async function viewScanReport(scanId) {
  const viewer = document.getElementById('reportViewer');
  viewer.textContent = `Loading report for scan_id ${scanId}...`;
  try {
    const data = await requestJson(`/scans/${scanId}/report`);
    renderScanReport(data.report || data);
  } catch (error) {
    viewer.textContent = `Error: ${error.message}`;
  }
}

function renderScanReport(report) {
  const viewer = document.getElementById('reportViewer');
  viewer.innerHTML = `<pre class="report-json">${escapeHtml(JSON.stringify(report, null, 2))}</pre>`;
}

function renderWaybackCapturesTable(captures) {
  if (!captures || !captures.length) {
    return '<p class="empty-note">No Wayback captures returned in lite query.</p>';
  }
  const rows = captures.map((capture) => `<tr>
    <td>${escapeHtml(capture.timestamp)}</td>
    <td><a href="${escapeHtml(capture.original)}" target="_blank" rel="noopener noreferrer">${escapeHtml(capture.original)}</a></td>
    <td>${escapeHtml(capture.statuscode)}</td>
    <td>${escapeHtml(capture.mimetype)}</td>
    <td><a href="${escapeHtml(capture.snapshot_url)}" target="_blank" rel="noopener noreferrer">snapshot</a></td>
  </tr>`).join('');
  return `<div class="table-wrap"><table class="captures-table">
    <thead><tr><th>timestamp</th><th>original</th><th>statuscode</th><th>mimetype</th><th>snapshot link</th></tr></thead>
    <tbody>${rows}</tbody>
  </table></div>`;
}

function renderDomainArchiveResult(result) {
  const container = document.getElementById('domainArchiveResult');
  const links = result.source_links || {};
  const rdap = result.rdap_summary || null;
  const wayback = result.wayback_summary || null;
  const linkItems = [
    ['Wayback', links.wayback_url],
    ['crt.sh', links.crtsh_url],
    ['RDAP', links.rdap_url],
    ['WhoisFreaks DNS History', links.whoisfreaks_dns_history_url],
    ['WhoisFreaks WHOIS History', links.whoisfreaks_whois_history_url],
  ].filter(([, href]) => href).map(([label, href]) => (
    `<li><a href="${escapeHtml(href)}" target="_blank" rel="noopener noreferrer">${escapeHtml(label)}</a></li>`
  )).join('');

  container.innerHTML = `<div class="result-grid">
    <div><strong>scan_id</strong><pre>${escapeHtml(result.scan_id)}</pre></div>
    <div><strong>success</strong><pre>${escapeHtml(result.success)}</pre></div>
    <div><strong>domain</strong><pre>${escapeHtml(result.domain)}</pre></div>
    <div><strong>report_file</strong><pre>${escapeHtml(result.report_file)}</pre></div>
    <div class="wide"><strong>summary</strong><pre>${escapeHtml(result.summary || '')}</pre></div>
    <div class="wide result-section"><h3>RDAP Summary</h3><pre>${escapeHtml(JSON.stringify(rdap, null, 2))}</pre></div>
    <div class="wide result-section"><h3>Wayback CDX Lite Summary</h3><pre>${escapeHtml(JSON.stringify(wayback, null, 2))}</pre>${renderWaybackCapturesTable(wayback?.captures || [])}</div>
    <div class="wide"><strong>current_dns</strong><pre>${escapeHtml(JSON.stringify(result.current_dns || null, null, 2))}</pre></div>
    <div class="wide"><strong>source_links</strong><ul class="link-list">${linkItems}</ul><pre>${escapeHtml(JSON.stringify(links, null, 2))}</pre></div>
  </div>`;
}
function renderNmapResult(result) {
  const container = document.getElementById('nmapResult');
  container.innerHTML = `<div class="result-grid">
    <div><strong>scan_id</strong><pre>${escapeHtml(result.scan_id)}</pre></div>
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
  loadScanHistory();
});
