import pytest

from requests import session
from tests.pages.rollups import sign_in

from tests.utils import (
    create_temp_csv,
    get_email_body,
    remove_all_emails,
    get_sms_via_heroku
)

from tests.pages import UploadCsvPage


def _get_email_message(config):
    try:
        return get_email_body(config.FUNCTIONAL_TEST_EMAIL,
                              config.FUNCTIONAL_TEST_PASSWORD,
                              config.EMAIL_NOTIFICATION_LABEL)
    except:
        pytest.fail("Couldn't get notification email")
    finally:
        remove_all_emails(email_folder=config.EMAIL_NOTIFICATION_LABEL)


def test_send_notifications_from_csv(driver, base_url, profile):

    sign_in(driver, profile)

    # go to upload csv for email notification page
    upload_csv_page = UploadCsvPage(driver)
    upload_csv_page.go_to_upload_csv_for_service_and_template(profile['service_id'],
                                                              profile['email_template_id'])

    # create csv file to use for email notification
    directory, filename = create_temp_csv(profile['email'], 'email address')

    upload_csv_page.upload_csv(directory, filename)

    email_body = _get_email_message(profile['config'])
    assert "The quick brown fox jumped over the lazy dog" in email_body

    # go to upload csv for sms notification page
    upload_csv_page.go_to_upload_csv_for_service_and_template(profile['service_id'],
                                                              profile['sms_template_id'])

    # create csv file to use for sms notification
    directory, filename = create_temp_csv(profile['mobile'], 'phone number')
    upload_csv_page.upload_csv(directory, filename)

    message = get_sms_via_heroku(session(), profile['config'].ENVIRONMENT)
    assert "The quick brown fox jumped over the lazy dog" in message
    upload_csv_page.sign_out()
