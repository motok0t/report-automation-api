import { setupUpload } from './modules/upload.js';
import { setupReport } from './modules/report.js';
import { setupSheetListener } from './modules/sheet.js';

document.addEventListener('DOMContentLoaded', () => {
    setupUpload();
    setupReport();
    setupSheetListener();
});
