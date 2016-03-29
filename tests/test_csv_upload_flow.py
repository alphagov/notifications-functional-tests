from requests import session

from config import Config
from tests.utils import (find_csrf_token,
                         get_sms_via_heroku,
                         create_sample_csv_file,
                         sign_in,
                         sign_out)


def test_csv_upload_journey():
    client = session()
    base_url = Config.NOTIFY_ADMIN_URL
    sign_in(
        client,
        base_url,
        Config.FUNCTIONAL_TEST_EMAIL,
        Config.FUNCTIONAL_TEST_PASSWORD)
    csv_upload_url = '{}/services/{}/send/{}'.format(
        base_url,
        Config.FUNCTIONAL_SERVICE_ID,
        Config.FUNCTIONAL_TEMPLATE_ID)
    get_csv_upload = client.get(csv_upload_url)
    next_token = find_csrf_token(get_csv_upload.text)
    csv_file = create_sample_csv_file([[Config.TWILIO_TEST_NUMBER]])
    files = {'file': ("preview_file.csv", csv_file, 'text/csv')}
    data = {'csrf_token': next_token}
    post_csv_upload = client.post(
        csv_upload_url,
        data=data,
        files=files,
        headers=dict(Referer=csv_upload_url))
    assert post_csv_upload.status_code == 200
    assert 'services/{}/sms/check'.format(Config.FUNCTIONAL_SERVICE_ID) in post_csv_upload.url
    next_token = find_csrf_token(post_csv_upload.text)
    data = {'csrf_token': next_token}
    post_check_sms = client.post(
        post_csv_upload.url,
        data=data,
        headers=dict(Referer=post_csv_upload.url))
    assert post_check_sms.status_code == 200
    assert '/jobs' in post_check_sms.url
    message = get_sms_via_heroku(client)

    # Verify the correct sms message was sent
    assert "The quick brown fox jumped over the lazy dog" in message
    sign_out(client, base_url)
