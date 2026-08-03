import { renderTable } from './table.js';

export function setupSheetListener() {
    const sheetSelect = document.getElementById('sheetSelect');
    const previewContainer = document.getElementById('uploadResult');
    const groupBySelect = document.getElementById('groupBy');
    const aggColSelect = document.getElementById('aggCol');

    function fillSelects(columns) {
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
    }

    sheetSelect.addEventListener('change', async function() {
        const sheetName = this.value;
        if (!sheetName) {
            previewContainer.style.display = 'none';
            return;
        }
        try {
            const res = await fetch(`/upload/columns?sheet=${sheetName}`);
            if (res.ok) {
                const data = await res.json();
                fillSelects(data.columns);
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
}
