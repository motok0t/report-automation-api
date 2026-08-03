import { showLoading, showError, postJson, getParams } from './utils.js';
import { renderTable } from './table.js';

export function setupReport() {
    const reportBtn = document.getElementById('reportBtn');
    const downloadCsvBtn = document.getElementById('downloadCsvBtn');
    const downloadExcelBtn = document.getElementById('downloadExcelBtn');
    const downloadPdfBtn = document.getElementById('downloadPdfBtn');
    const reportResult = document.getElementById('reportResult');
    const reportHint = document.getElementById('reportHint');
    const outlierMetricRow = document.getElementById('outlierMetricRow');
    const outlierMetricSelect = document.getElementById('outlierMetric');
    const detectOutliersCheckbox = document.getElementById('detectOutliers');

    const metricCheckboxes = document.querySelectorAll('.metric-check');

    function updateOutlierMetricOptions() {
        const selected = [];
        metricCheckboxes.forEach(el => {
            if (el.checked) selected.push(el.value);
        });
        outlierMetricSelect.innerHTML = '';
        if (detectOutliersCheckbox.checked && selected.length > 1) {
            outlierMetricRow.style.display = 'flex';
            selected.forEach(val => {
                const opt = document.createElement('option');
                opt.value = val;
                opt.textContent = val.charAt(0).toUpperCase() + val.slice(1);
                outlierMetricSelect.appendChild(opt);
            });
            outlierMetricSelect.value = selected[0];
        } else if (detectOutliersCheckbox.checked && selected.length === 1) {
            outlierMetricRow.style.display = 'flex';
            const val = selected[0];
            const opt = document.createElement('option');
            opt.value = val;
            opt.textContent = val.charAt(0).toUpperCase() + val.slice(1);
            outlierMetricSelect.appendChild(opt);
            outlierMetricSelect.value = val;
        } else {
            outlierMetricRow.style.display = 'none';
        }
    }

    detectOutliersCheckbox.addEventListener('change', updateOutlierMetricOptions);
    metricCheckboxes.forEach(el => {
        el.addEventListener('change', updateOutlierMetricOptions);
    });

    function getFullParams() {
        const params = getParams();
        const outlierMetric = outlierMetricSelect.value;
        return {
            ...params,
            outlier_metric: outlierMetric || null
        };
    }

    async function generateReport() {
        showLoading(reportResult);
        const params = getFullParams();
        if (params.aggregation.length === 0) {
            showError(reportResult, 'Please select at least one metric.');
            return;
        }
        if (params.group_by === params.aggregate_column) {
            showError(reportResult, 'Group by and Aggregate cannot be the same column.');
            return;
        }
        try {
            const res = await postJson('/report/summary', params);
            if (!res.ok) {
                const err = await res.json();
                throw new Error(err.detail || 'Report generation failed');
            }
            const json = await res.json();
            reportResult.style.display = 'block';
            let html = `<p><strong>✅ Report generated</strong> (${json.total_rows} rows)</p>`;
            if (json.summary) {
                const s = json.summary;
                const outlierBadge = s.has_outliers !== undefined
                    ? (s.has_outliers
                        ? '<span class="badge warn">⚠️ Outliers detected</span>'
                        : '<span class="badge ok">✅ No outliers</span>')
                    : '';
                html += `<p><span class="badge ok">Total rows: ${s.total_rows}</span>
                         <span class="badge ok">Groups: ${s.groups}</span>
                         ${outlierBadge}</p>`;
            }
            html += renderTable(json.data);
            reportResult.innerHTML = html;

            reportHint.style.display = 'block';
            const sortLabel = params.sort_by === 'asc' ? 'Ascending' :
                              params.sort_by === 'desc' ? 'Descending' : 'None';
            const outlierInfo = params.detect_outliers
                ? ` | Outlier metric: ${params.outlier_metric || 'N/A'}`
                : '';
            document.getElementById('reportHintText').innerHTML = `
                Group by: ${params.group_by} |
                Aggregate: ${params.aggregate_column} |
                Metrics: ${params.aggregation.join(', ')} |
                Sort by: ${sortLabel} (by ${params.group_by})
                ${outlierInfo}
            `;
        } catch (e) {
            showError(reportResult, e.message);
        }
    }

    async function downloadFile(endpoint, filename) {
        try {
            const res = await postJson(endpoint, getFullParams());
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

    reportBtn.onclick = generateReport;
    downloadCsvBtn.onclick = () => {
        const params = getFullParams();
        if (params.aggregation.length === 0) {
            showError(reportResult, 'Please select at least one metric.');
            return;
        }
        downloadFile('/report/download/csv', 'report.csv');
    };
    downloadExcelBtn.onclick = () => {
        const params = getFullParams();
        if (params.aggregation.length === 0) {
            showError(reportResult, 'Please select at least one metric.');
            return;
        }
        downloadFile('/report/download/excel', 'report.xlsx');
    };
    downloadPdfBtn.onclick = () => {
        const params = getFullParams();
        if (params.aggregation.length === 0) {
            showError(reportResult, 'Please select at least one metric.');
            return;
        }
        downloadFile('/report/download/pdf', 'report.pdf');
    };

    updateOutlierMetricOptions();
}
