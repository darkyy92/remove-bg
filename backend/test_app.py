import io
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    """Test that the health check endpoint returns status ok."""
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_missing_file():
    """Test that the API returns a 422 when no file is provided."""
    response = client.post("/api/remove-bg")
    assert response.status_code == 422

def test_invalid_file_type():
    """Test that the API returns a 400 when a non-image file is provided."""
    response = client.post(
        "/api/remove-bg",
        files={"file": ("test.txt", io.BytesIO(b"This is a test"), "text/plain")}
    )
    assert response.status_code == 400
    assert "File must be an image" in response.text

# This test requires a real image and rembg to be installed
# Uncomment and run manually when needed
# def test_successful_background_removal():
#     """Test successful background removal with a real image."""
#     with open("test_image.jpg", "rb") as f:
#         image_data = f.read()
#     
#     response = client.post(
#         "/api/remove-bg",
#         files={"file": ("test_image.jpg", io.BytesIO(image_data), "image/jpeg")}
#     )
#     assert response.status_code == 200
#     assert response.headers["content-type"] == "image/png"