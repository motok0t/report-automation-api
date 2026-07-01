from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_upload():
    with open("data/homes.csv", "rb") as f:
        response = client.post(
            "/upload/",
            files={"file": ("homes.csv", f, "text/csv")}
        )
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "homes.csv"
    assert data["rows"] == 50
    assert "column_names" in data


def test_report_summary():
    payload = {
        "group_by": " \"Beds\"",
        "aggregate_column": " \"Taxes\"",
        "aggregation": "sum"
    }
    response = client.post("/report/summary", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["total_rows"] == 4
    assert "summary" in data
