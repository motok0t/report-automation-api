import { showLoading, showError, postJson, getParams } from './utils.js';
import { renderTable } from './table.js';

export function setupReport() {
    const reportBtn = document.getElementById('reportBtn');
    const downloadCsvBtn = document.getElementById('downloadCsvBtn');
    const downloadExcelBtn = document.getElementById('downloadExcelBtn');
    const downloadPdfBtn = document.getElementById('downloadPdfBtn');
    const reportResult = document.getElementById('reportResult');
    const reportHint = document.getElementById('reportHint');

    async function generateReport() {
        showLoading(reportResult);
        const params = getParams();
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
            document.getElementById('hintGroupBy').textContent = params.group_by;
            document.getElementById('hintAggregate').textContent = params.aggregate_column;
            document.getElementById('hintMetrics').textContent = params.aggregation.join(', ');
            const sortLabel = params.sort_by === 'asc' ? 'Ascending' :
                              params.sort_by === 'desc' ? 'Descending' : 'None';
            document.getElementById('hintSortBy').textContent =
                `${sortLabel} (by ${params.group_by})`;
        } catch (e) {
            showError(reportResult, e.message);
        }
    }

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

    reportBtn.onclick = generateReport;
    downloadCsvBtn.onclick = () => {
        const params = getParams();
        if (params.aggregation.length === 0) {
            showError(reportResult, 'Please select at least one metric.');
            return;
        }
        downloadFile('/report/download/csv', 'report.csv');
    };
    downloadExcelBtn.onclick = () => {
        const params = getParams();
        if (params.aggregation.length === 0) {
            showError(reportResult, 'Please select at least one metric.');
            return;
        }
        downloadFile('/report/download/excel', 'report.xlsx');
    };
    downloadPdfBtn.onclick = () => {
        const params = getParams();
        if (params.aggregation.length === 0) {
            showError(reportResult, 'Please select at least one metric.');
            return;
        }
        downloadFile('/report/download/pdf', 'report.pdf');
    };
}
