const uploadBtn = document.getElementById('uploadBtn');
const reportBtn = document.getElementById('reportBtn');
const downloadCsvBtn = document.getElementById('downloadCsvBtn');
const downloadExcelBtn = document.getElementById('downloadExcelBtn');

const uploadResult = document.getElementById('uploadResult');
const reportResult = document.getElementById('reportResult');

const fileInput = document.getElementById('fileInput');
const fileChosen = document.getElementById('fileChosen');

fileInput.addEventListener('change', () => {
    if (fileInput.files.length > 0) {
        fileChosen.textContent = fileInput.files[0].name;
    } else {
        fileChosen.textContent = 'No file chosen';
    }
});

function showLoading(container) {
    container.style.display = 'block';
    container.innerHTML = '<div class="spinner"></div> Loading...';
}

function showError(container, message) {
    container.style.display = 'block';
    container.innerHTML = `<div class="error">⚠️ ${message}</div>`;
}

function renderTable(data) {
    if (!data || data.length === 0) return '<p>No data to display.</p>';
    const keys = Object.keys(data[0]);
    let html = '<table><thead><tr>';
    keys.forEach(k => html += `<th>${k}</th>`);
    html += '</tr></thead><tbody>';
    data.forEach(row => {
        html += '<tr>';
        keys.forEach(k => html += `<td>${row[k] ?? ''}</td>`);
        html += '</tr>';
    });
    html += '</tbody></table>';
    return html;
}

async function postJson(url, data) {
    const res = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });
    return res;
}

uploadBtn.onclick = async () => {
    const file = fileInput.files[0];
    if (!file) { showError(uploadResult, 'Select a file first.'); return; }
    showLoading(uploadResult);
    const form = new FormData();
    form.append('file', file);
    try {
        const res = await fetch('/upload/', { method: 'POST', body: form });
        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || 'Upload failed');
        }
        const json = await res.json();
        uploadResult.style.display = 'block';
        uploadResult.innerHTML = `
            <p><strong>✅ File uploaded successfully</strong></p>
            <p><span class="badge ok">${json.rows} rows</span>
            <span class="badge ok">${json.columns} columns</span></p>
            <p><strong>Preview:</strong></p>
            ${renderTable(json.preview)}
        `;
    } catch (e) {
        showError(uploadResult, e.message);
    }
};

const getParams = () => ({
    group_by: document.getElementById('groupBy').value,
    aggregate_column: document.getElementById('aggCol').value,
    aggregation: document.getElementById('aggList').value.split(',').map(s => s.trim()).filter(Boolean),
    detect_outliers: document.getElementById('detectOutliers').checked
});

reportBtn.onclick = async () => {
    showLoading(reportResult);
    try {
        const res = await postJson('/report/summary', getParams());
        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || 'Report generation failed');
        }
        const json = await res.json();
        reportResult.style.display = 'block';
        let html = `<p><strong>✅ Report generated</strong> (${json.total_rows} rows)</p>`;
        if (json.summary) {
            const s = json.summary;
            html += `<p><span class="badge ok">Total rows: ${s.total_rows}</span>
                     <span class="badge ok">Groups: ${s.groups}</span>
                     ${s.has_outliers !== undefined ? (s.has_outliers ? '<span class="badge warn">⚠️ Outliers detected</span>' : '<span class="badge ok">✅ No outliers</span>') : ''}</p>`;
        }
        html += renderTable(json.data);
        reportResult.innerHTML = html;
    } catch (e) {
        showError(reportResult, e.message);
    }
};

async function downloadFile(endpoint, filename) {
    try {
        const res = await postJson(endpoint, getParams());
        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || 'Download failed');
        }
        const blob = await res.blob();
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = filename;
        link.click();
    } catch (e) {
        showError(reportResult, e.message);
    }
}

downloadCsvBtn.onclick = () => downloadFile('/report/download/csv', 'report.csv');
downloadExcelBtn.onclick = () => downloadFile('/report/download/excel', 'report.xlsx');
