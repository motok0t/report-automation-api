from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import report, upload

app = FastAPI(
    title="Report Automation API",
    description="API для автоматической обработки данных и генерации отчётов",
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
app.include_router(report.router)


@app.get("/")
async def root():
    return {"message": "Report Automation API is running"}
