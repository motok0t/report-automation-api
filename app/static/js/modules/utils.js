export function showLoading(container) {
    container.style.display = 'block';
    container.innerHTML = '<div class="spinner"></div> Loading...';
}

export function showError(container, message) {
    container.style.display = 'block';
    container.innerHTML = `<div class="error">⚠️ ${message}</div>`;
}

export async function postJson(url, data) {
    const res = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });
    return res;
}

export function getParams() {
    const selected = [];
    document.querySelectorAll('.metric-check:checked').forEach(el => {
        selected.push(el.value);
    });
    return {
        group_by: document.getElementById('groupBy').value,
        aggregate_column: document.getElementById('aggCol').value,
        aggregation: selected.length ? selected : [],
        detect_outliers: document.getElementById('detectOutliers').checked,
        sheet_name: document.getElementById('sheetSelect').value || null,
        sort_by: document.getElementById('sortBy').value
    };
}
