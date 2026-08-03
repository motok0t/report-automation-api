import { showLoading, showError } from './utils.js';
import { renderTable } from './table.js';

export function setupUpload() {
    const uploadBtn = document.getElementById('uploadBtn');
    const uploadResult = document.getElementById('uploadResult');
    const fileInput = document.getElementById('fileInput');
    const fileChosen = document.getElementById('fileChosen');
    const sheetSelect = document.getElementById('sheetSelect');
    const groupBySelect = document.getElementById('groupBy');
    const aggColSelect = document.getElementById('aggCol');

    fileInput.addEventListener('change', () => {
        if (fileInput.files.length > 0) {
            fileChosen.textContent = fileInput.files[0].name;
        } else {
            fileChosen.textContent = 'No file chosen';
        }
    });

    function fillSelects(columns, keepValues = false) {
        const gVal = groupBySelect.value;
        const aVal = aggColSelect.value;

        groupBySelect.innerHTML = '<option value="">— Select —</option>';
        aggColSelect.innerHTML = '<option value="">— Select —</option>';

        columns.forEach(col => {
            const opt1 = document.createElement('option');
            opt1.value = col;
            opt1.textContent = col;
            groupBySelect.appendChild(opt1);

            const opt2 = document.createElement('option');
            opt2.value = col;
            opt2.textContent = col;
            aggColSelect.appendChild(opt2);
        });

        if (keepValues) {
            groupBySelect.value = gVal;
            aggColSelect.value = aVal;
        }

        updateDisabledOptions();
    }

    function updateDisabledOptions() {
        const gVal = groupBySelect.value;
        const aVal = aggColSelect.value;

        Array.from(aggColSelect.options).forEach(opt => {
            opt.disabled = opt.value && opt.value === gVal;
        });

        Array.from(groupBySelect.options).forEach(opt => {
            opt.disabled = opt.value && opt.value === aVal;
        });

        if (aggColSelect.value === gVal && gVal) {
            const first = Array.from(aggColSelect.options).find(
                opt => !opt.disabled
            );
            if (first) {
                aggColSelect.value = first.value;
            }
        }

        if (groupBySelect.value === aVal && aVal) {
            const first = Array.from(groupBySelect.options).find(
                opt => !opt.disabled
            );
            if (first) {
                groupBySelect.value = first.value;
            }
        }
    }

    groupBySelect.addEventListener('change', updateDisabledOptions);
    aggColSelect.addEventListener('change', updateDisabledOptions);

    uploadBtn.onclick = async () => {
        const file = fileInput.files[0];

        if (!file) {
            showError(uploadResult, 'Select a file first.');
            return;
        }

        sheetSelect.innerHTML =
            '<option value="">Upload Excel to see sheets</option>';
        uploadResult.style.display = 'none';
        uploadResult.innerHTML = '';
        groupBySelect.innerHTML = '<option value="">— Select —</option>';
        aggColSelect.innerHTML = '<option value="">— Select —</option>';
        document.getElementById('reportResult').style.display = 'none';
        document.getElementById('reportResult').innerHTML = '';
        document.getElementById('reportHint').style.display = 'none';
        document.querySelectorAll('.metric-check').forEach(
            el => (el.checked = false)
        );
        document.getElementById('detectOutliers').checked = false;
        document.getElementById('outlierMetricRow').style.display = 'none';

        showLoading(uploadResult);

        const form = new FormData();
        form.append('file', file);

        try {
            const res = await fetch('/upload/', {
                method: 'POST',
                body: form
            });

            if (!res.ok) {
                const err = await res.json();
                throw new Error(err.detail || 'Upload failed');
            }

            const json = await res.json();

            uploadResult.style.display = 'block';
            uploadResult.innerHTML = `
                <p><strong>✅ File uploaded successfully</strong></p>
                <p>
                    <span class="badge ok">${json.rows} rows</span>
                    <span class="badge ok">${json.columns} columns</span>
                </p>
                <p><strong>Preview:</strong></p>
                ${renderTable(json.preview)}
            `;

            fillSelects(json.column_names);

            const isExcel =
                file.name.endsWith('.xlsx') || file.name.endsWith('.xls');

            if (isExcel) {
                try {
                    const sheetRes = await fetch('/upload/sheets');

                    if (sheetRes.ok) {
                        const sheetData = await sheetRes.json();

                        sheetSelect.innerHTML = '';

                        sheetData.sheets.forEach(name => {
                            const opt = document.createElement('option');
                            opt.value = name;
                            opt.textContent = name;
                            sheetSelect.appendChild(opt);
                        });

                        if (sheetData.sheets.length > 0) {
                            const firstSheet = sheetData.sheets[0];
                            sheetSelect.value = firstSheet;

                            const colsRes = await fetch(
                                `/upload/columns?sheet=${firstSheet}`
                            );
                            if (colsRes.ok) {
                                const colsData = await colsRes.json();
                                fillSelects(colsData.columns);
                            }

                            const previewRes = await fetch(
                                `/upload/preview?sheet=${firstSheet}`
                            );
                            if (previewRes.ok) {
                                const previewData = await previewRes.json();
                                uploadResult.style.display = 'block';
                                uploadResult.innerHTML = `
                                    <p><strong>Preview for sheet: ${firstSheet}</strong></p>
                                    ${renderTable(previewData.preview)}
                                `;
                            }
                        }
                    }
                } catch {
                    sheetSelect.innerHTML =
                        '<option value="">No sheets found</option>';
                }
            } else {
                sheetSelect.innerHTML =
                    '<option value="">No sheets available</option>';
            }
        } catch (e) {
            showError(uploadResult, e.message);
        }
    };
}
