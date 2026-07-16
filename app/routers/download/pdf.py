import logging
import os
from io import BytesIO

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Table, TableStyle

from app.schemas.report_schemas import ReportRequest
from app.services.aggregator import DataAggregator
from app.services.cleaner import DataCleaner
from app.services.outlier import OutlierDetector
from app.services.utils import get_uploaded_file_path, read_uploaded_file
from app.services.validators import DataValidator

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/report/download", tags=["Report"])


@router.post("/pdf")
async def download_pdf(request: ReportRequest):
    try:
        file_path = get_uploaded_file_path()
        if not file_path:
            raise HTTPException(
                status_code=404,
                detail="No file uploaded yet."
            )

        if request.sheet_name and file_path.endswith(('.xlsx', '.xls')):
            df = read_uploaded_file(file_path, sheet_name=request.sheet_name)
        else:
            df = read_uploaded_file(file_path)

        df.columns = df.columns.str.replace('"', '').str.strip()
        df = DataCleaner.clean_data(df)

        DataValidator.validate_aggregation_params(
            df,
            request.group_by,
            request.aggregate_column
        )

        if request.filter_column and request.filter_value:
            df = DataAggregator.filter_data(
                df,
                request.filter_column,
                request.filter_value
            )

        if request.detect_outliers:
            df = OutlierDetector.detect_outliers(df, request.aggregate_column)

        agg_list = [a.value for a in request.aggregation]
        result = DataAggregator.aggregate_data(
            df,
            request.group_by,
            request.aggregate_column,
            agg_list
        )

        if request.sort_by == 'asc':
            result = result.sort_values(by=request.group_by, ascending=True)
        elif request.sort_by == 'desc':
            result = result.sort_values(by=request.group_by, ascending=False)

        if request.detect_outliers:
            result = OutlierDetector.highlight_outliers(result, 'sum')
            result = result.drop(columns=['_style'], errors='ignore')

        os.makedirs("generated_reports", exist_ok=True)
        output_path = "generated_reports/report.pdf"

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        elements = []

        styles = getSampleStyleSheet()
        title = Paragraph("Report Summary", styles['Title'])
        elements.append(title)
        elements.append(Paragraph(" ", styles['Normal']))

        table_data = [result.columns.tolist()] + result.values.tolist()
        table = Table(table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
        ]))
        elements.append(table)

        doc.build(elements)

        with open(output_path, 'wb') as f:
            f.write(buffer.getvalue())

        return FileResponse(
            path=output_path,
            filename="report.pdf",
            media_type="application/pdf"
        )
    except Exception as e:
        logger.error(f"PDF generation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
