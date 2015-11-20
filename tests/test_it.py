import requests


def test_notifications_admin_index():
    response = requests.request("GET", "http://localhost:6012/index")
    assert response.status_code == 200
    assert response.content == 'Hello from notifications-admin'
