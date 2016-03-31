from requests import session

from config import Config
from tests.utils import get_sms_via_heroku
from notifications_python_client.notifications import NotificationsAPIClient


def test_python_client():
    client = NotificationsAPIClient(
        Config.NOTIFY_API_URL,
        Config.FUNCTIONAL_SERVICE_ID,
        Config.FUNCTIONAL_API_KEY)
    resp_json = client.send_sms_notification(
        Config.TWILIO_TEST_NUMBER,
        Config.FUNCTIONAL_TEMPLATE_ID)
    assert 'result' not in resp_json['data']
    notification_id = resp_json['data']['notification']['id']
    message = get_sms_via_heroku(session())
    assert "The quick brown fox jumped over the lazy dog" in message
    resp_json = client.get_notification_by_id(notification_id)
    assert resp_json['data']['notification']['status'] == 'sent'
