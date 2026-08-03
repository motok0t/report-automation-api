import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.routers import report_suggest, report_summary, upload
from app.routers.download import csv, excel, pdf

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Report Automation API",
    description="API for automated data processing and report generation",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router)
app.include_router(report_summary.router)
app.include_router(report_suggest.router)
app.include_router(csv.router)
app.include_router(excel.router)
app.include_router(pdf.router)

app.mount("/", StaticFiles(directory="app/static", html=True), name="static")


@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {"message": "Report Automation API is running"}
