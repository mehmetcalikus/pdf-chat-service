from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_file_upload():
    test_file = "sample.pdf"
    files = {"file": (test_file, open(test_file, "rb"), "application/pdf")}
    response = client.post("/v1/pdf", files=files)
    assert response.status_code == 200
    assert "pdf_id" in response.json()

def test_ask_question():
    test_file = "sample.pdf"
    files = {"file": (test_file, open(test_file, "rb"), "application/pdf")}
    response = client.post("/v1/pdf", files=files)
    assert response.status_code == 200
    assert "pdf_id" in response.json()

    pdf_id = response.json()["pdf_id"]
    question = "What is the text?"
    response = client.post(f"/v1/pdf/{pdf_id}", json={"message": question})
    assert response.status_code == 200
    assert "response" in response.json()