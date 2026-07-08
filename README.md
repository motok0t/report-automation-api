# Report Automation API

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.138-green.svg)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/Docker-27.0-blue.svg)](https://docker.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Report Automation API** is a RESTful service for automated data processing and report generation.

It solves a common business problem: analysts spending hours manually cleaning and aggregating spreadsheets. Instead of copying, grouping, and summing data in Excel, you upload a file and get a ready-to-use report in seconds.

---

## Features

- **Multi-format input**: CSV, Excel (.xlsx), JSON, Parquet
- **Sheet selection**: choose specific sheets in Excel files
- **Data cleaning**: automatic duplicate removal, null value handling, quote cleaning
- **Flexible aggregation**: group by any column, apply multiple metrics (sum, mean, count, min, max) in one request
- **Outlier detection**: flag groups with anomalies (values deviating >2 standard deviations from mean)
- **Sorting**: sort results by Group by column (ascending/descending)
- **Export options**: download reports as CSV or Excel
- **Auto-suggest**: API recommends which columns to group and aggregate
- **Modern stack**: FastAPI, Pandas, Docker
- **Interactive docs**: built-in Swagger UI at `/docs`

---

## Quick Start

### Clone & Run

```bash
git clone https://github.com/motok0t/report-automation-api.git
cd report-automation-api
docker build -t report-automation-api .
docker run -p 8000:8000 report-automation-api
```

Then open: [http://localhost:8000](http://localhost:8000)

### Using Docker Compose

```bash
docker-compose up
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/upload/` | Upload a CSV, Excel, JSON, or Parquet file |
| POST | `/report/summary` | Generate aggregated report with summary statistics |
| POST | `/report/download/csv` | Download report as CSV |
| POST | `/report/download/excel` | Download report as Excel |
| POST | `/report/suggest` | Get column recommendations for grouping/aggregation |

---

## Example Request

### Generate Summary Report

```json
POST /report/summary
{
  "group_by": "region",
  "aggregate_column": "sales",
  "aggregation": ["sum", "mean", "count"],
  "detect_outliers": true
}
```

### Response

```json
{
  "status": "success",
  "data": [
    { "region": "North", "sum": 15000, "mean": 3750, "count": 4 },
    { "region": "South", "sum": 22000, "mean": 4400, "count": 5 }
  ],
  "total_rows": 2,
  "summary": {
    "total_rows": 50,
    "groups": 2,
    "min_value": 1200,
    "max_value": 8200,
    "mean_value": 4100,
    "std_value": 1800,
    "has_outliers": true
  }
}
```

---

## Tech Stack

- **Python** 3.11+
- **FastAPI** - modern async web framework
- **Pandas** - data manipulation and analysis
- **Pydantic** - data validation
- **Docker** - containerization
- **Pytest** - testing

---

## Project Structure

```
report_automation_api/
├── app/
│   ├── routers/         # API endpoints
│   ├── services/        # Business logic
│   ├── schemas/         # Pydantic models
│   ├── utils/           # Helpers and validators
│   └── static/          # Frontend interface
├── data/                # Sample datasets
├── tests/               # Pytest tests
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

---

## Why This Project Matters

Data rarely comes clean. It lands in different formats — CSV, Excel, JSON, Parquet — from different systems, often with missing values, duplicates, or inconsistent structure. Getting it ready for analysis usually means hours of manual work: filtering, merging, reformatting. It's repetitive, error-prone, and pulls focus from the actual analysis.

I've dealt with this firsthand. In my work with financial data, I saw how much time gets lost on preparation rather than insight. This project automates the heavy lifting.

**Why not Power Query?**

Power Query is a great tool — I've used it. But it's desktop-bound and requires Excel or Power BI. This API is different: it's server-side, headless, and designed to be integrated into automated pipelines. You can call it from a script, schedule it with cron, or embed it into a larger data workflow. It's not a replacement — it's a complement for situations where you need programmatic, repeatable data processing without clicking through a GUI.

It's also built with a practical constraint in mind: not every task needs access to sensitive data. By working with open or synthetic datasets, the tool stays portable and demo-friendly — no security clearance required.

---

## License

MIT - free for personal and commercial use.

---

**Built with Python, FastAPI, and Pandas by Elena Kurbatova**  
For questions or collaboration, feel free to reach out.
