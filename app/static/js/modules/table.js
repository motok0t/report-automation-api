export function renderTable(data) {
    if (!data || data.length === 0) return '<p>No data to display.</p>';
    const keys = Object.keys(data[0]);
    const hiddenKeys = ['is_outlier'];
    const displayKeys = keys.filter(k => !hiddenKeys.includes(k));

    let html = '<table><thead><tr>';
    displayKeys.forEach(k => {
        const header = k === 'has_outliers' ? 'Anomalies' : k;
        html += `<th>${header}</th>`;
    });
    html += '</tr></thead><tbody>';
    data.forEach(row => {
        html += '<tr>';
        displayKeys.forEach((k) => {
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
