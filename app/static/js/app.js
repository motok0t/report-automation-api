const uploadBtn = document.getElementById('uploadBtn');
const reportBtn = document.getElementById('reportBtn');
const downloadCsvBtn = document.getElementById('downloadCsvBtn');
const downloadExcelBtn = document.getElementById('downloadExcelBtn');

const uploadResult = document.getElementById('uploadResult');
const reportResult = document.getElementById('reportResult');

const fileInput = document.getElementById('fileInput');
const fileChosen = document.getElementById('fileChosen');

const sheetSelect = document.getElementById('sheetSelect');

fileInput.addEventListener('change', () => {
    if (fileInput.files.length > 0) {
        fileChosen.textContent = fileInput.files[0].name;
    } else {
        fileChosen.textContent = 'No file chosen';
    }
});

sheetSelect.addEventListener('change', async function() {
    const sheetName = this.value;
    const previewContainer = document.getElementById('uploadResult');
    if (!sheetName) {
        previewContainer.style.display = 'none';
        return;
    }
    try {
        const res = await fetch(`/upload/columns?sheet=${sheetName}`);
        if (res.ok) {
            const data = await res.json();
            const groupBySelect = document.getElementById('groupBy');
            const aggColSelect = document.getElementById('aggCol');
            groupBySelect.innerHTML = '';
            aggColSelect.innerHTML = '';
            data.columns.forEach(col => {
                const opt1 = document.createElement('option');
                opt1.value = col;
                opt1.textContent = col;
                groupBySelect.appendChild(opt1);

                const opt2 = document.createElement('option');
                opt2.value = col;
                opt2.textContent = col;
                aggColSelect.appendChild(opt2);
            });
        }
        const previewRes = await fetch(`/upload/preview?sheet=${sheetName}`);
        if (previewRes.ok) {
            const previewData = await previewRes.json();
            previewContainer.style.display = 'block';
            previewContainer.innerHTML = `
                <p><strong>Preview for sheet: ${sheetName}</strong></p>
                ${renderTable(previewData.preview)}
            `;
        }
    } catch (e) {
        console.error('Failed to load data:', e);
        previewContainer.innerHTML = '<p>Error loading preview</p>';
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
    const columnNames = keys.map(k => {
        if (k === 'has_outliers') return 'Anomalies';
        return k;
    });
    let html = '<table><thead><tr>';
    columnNames.forEach(k => html += `<th>${k}</th>`);
    html += '</tr></thead><tbody>';
    data.forEach(row => {
        html += '<tr>';
        keys.forEach((k, index) => {
            let value = row[k] ?? '';
            if (k === 'has_outliers' && value === true) {
                value = '⚠️';
            } else if (k === 'has_outliers' && value === false) {
                value = '✅';
            }
            if (typeof value === 'number') {
                if (!isFinite(value)) {
                    value = 'N/A';
                } else {
                    value = value.toFixed(2);
                }
            }
            html += `<td>${value}</td>`;
        });
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
    
    document.getElementById('reportResult').style.display = 'none';
    document.getElementById('reportResult').innerHTML = '';
    document.getElementById('reportHint').style.display = 'none';
    document.querySelectorAll('.metric-check').forEach(el => el.checked = false);
    document.getElementById('detectOutliers').checked = false;
    
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

        const groupBySelect = document.getElementById('groupBy');
        const aggColSelect = document.getElementById('aggCol');
        groupBySelect.innerHTML = '';
        aggColSelect.innerHTML = '';
        json.column_names.forEach(col => {
            const opt1 = document.createElement('option');
            opt1.value = col;
            opt1.textContent = col;
            groupBySelect.appendChild(opt1);

            const opt2 = document.createElement('option');
            opt2.value = col;
            opt2.textContent = col;
            aggColSelect.appendChild(opt2);
        });

        if (file.name.endsWith('.xlsx') || file.name.endsWith('.xls')) {
            const sheetSelect = document.getElementById('sheetSelect');
            sheetSelect.innerHTML = '<option value="">Loading sheets...</option>';
            try {
                const sheetRes = await fetch('/upload/sheets');
                if (sheetRes.ok) {
                    const sheetData = await sheetRes.json();
                    sheetSelect.innerHTML = '<option value="">Select sheet...</option>';
                    sheetData.sheets.forEach(name => {
                        const opt = document.createElement('option');
                        opt.value = name;
                        opt.textContent = name;
                        sheetSelect.appendChild(opt);
                    });
                } else {
                    sheetSelect.innerHTML = '<option value="">No sheets found</option>';
                }
            } catch (e) {
                sheetSelect.innerHTML = '<option value="">Error loading sheets</option>';
            }
        } else {
            const sheetSelect = document.getElementById('sheetSelect');
            sheetSelect.innerHTML = '<option value="">No sheets available</option>';
        }
    } catch (e) {
        showError(uploadResult, e.message);
    }
};

const getParams = () => {
    const selected = [];
    document.querySelectorAll('.metric-check:checked').forEach(el => {
        selected.push(el.value);
    });
    return {
        group_by: document.getElementById('groupBy').value,
        aggregate_column: document.getElementById('aggCol').value,
        aggregation: selected.length ? selected : ['sum', 'mean', 'count'],
        detect_outliers: document.getElementById('detectOutliers').checked,
        sheet_name: document.getElementById('sheetSelect').value || null,
        sort_by: document.getElementById('sortBy').value
    };
};

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

        document.getElementById('reportHint').style.display = 'block';
        document.getElementById('hintGroupBy').textContent = getParams().group_by;
        document.getElementById('hintAggregate').textContent = getParams().aggregate_column;
        document.getElementById('hintMetrics').textContent = getParams().aggregation.join(', ');
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
