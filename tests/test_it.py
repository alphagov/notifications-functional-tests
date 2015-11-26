import requests


def test_notifications_admin_index():
    # response = requests.request("GET", "http://localhost:6012")
    response = requests.request("GET", "http://notifications-admin.herokuapp.com/")
    assert response.status_code == 200
    assert 'GOV.UK Notify' in response.content
