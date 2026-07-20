export function renderTable(data) {
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
        keys.forEach((k) => {
            let value = row[k] ?? '';
            if (k === 'has_outliers' && value === true) {
                value = '🟡';
            } else if (k === 'has_outliers' && value === false) {
                value = '🟢';
            }
            if (typeof value === 'number') {
                if (!isFinite(value)) {
                    value = 'N/A';
                } else if (Number.isInteger(value)) {
                    value = value.toString();
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
