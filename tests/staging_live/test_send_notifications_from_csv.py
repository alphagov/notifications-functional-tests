import pytest

from tests.pages.rollups import sign_in

from tests.utils import (
    create_temp_csv,
    get_email_body,
    remove_all_emails
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


def test_send_email_from_csv_live(driver, base_url, profile):

    sign_in(driver, profile)

    upload_csv_page = UploadCsvPage(driver)
    upload_csv_page.go_to_upload_csv_for_service_and_template(profile['service_id'],
                                                              profile['email_template_id'])

    # create csv file with to use for notification
    directory, filename = create_temp_csv(profile['email'], 'email address')

    upload_csv_page.upload_csv(directory, filename)

    email_body = _get_email_message(profile['config'])
    assert "The quick brown fox jumped over the lazy dog" in email_body
    upload_csv_page.sign_out()
