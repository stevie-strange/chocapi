"""Tests for the model calculation."""
from fastapi.testclient import TestClient

from .main import app

# create the test client
client = TestClient(app)


def test_cho_model():
    """Test the CHO model."""
    response = client.post(
        "/models/cho",
        json={  "watts": [0, 75, 100, 125, 150, 175, 200, 225, 275],
                "consumption": [21, 38, 50, 63, 83, 104, 121, 142, 250]},
    )
    assert response.status_code == 200

def test_fat_model():
    """Test the FAT model."""
    response = client.post(
        "/models/fat",
        json={  "watts": [0, 125, 150, 175, 200, 225, 250, 275],
                "consumption": [13, 31, 31, 33, 29, 25, 17, 0]},
    )
    assert response.status_code == 200

def test_invalid_model():
    """Test the invalid model."""
    response = client.post(
        "/models/invalid",
        json={  "watts": [0, 75, 100, 125, 150, 175, 200, 225, 275],
                "consumption": [21, 38, 50, 63, 83, 104, 121, 142, 250]},
    )
    assert response.status_code == 422

def test_invalid_data():
    """Test the invalid data not equal length."""
    response = client.post(
        "/models/cho",
        json={  "watts": [0, 75, 100, 125, 150, 175, 200, 225, 275],
                "consumption": [21, 38, 50, 63, 83, 104, 121, 142, 250, 300]},
    )
    assert response.status_code == 422

def test_invalid_data2():
    """Test the invalid data not enough data."""
    response = client.post(
        "/models/cho",
        json={  "watts": [0, 75],
                "consumption": [21, 38, 50, 63, 83, 104, 121, 142]},
    )
    assert response.status_code == 422

def test_invalid_data3():
    """Test the invalid data for values smaller than 0."""
    response = client.post(
        "/models/cho",
        json={  "watts": [0, 75, 100, 125, 150, 175, 200, 225, 275],
                "consumption": [21, 38, 50, 63, 83, 104, 121, 142, -250]},
    )
    assert response.status_code == 422
    