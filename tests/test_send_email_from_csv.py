import pytest

from config import Config

from tests.pages.rollups import sign_in

from tests.utils import (
    create_temp_csv,
    get_email_body,
    remove_all_emails
)

from tests.pages import (
    DashboardPage,
    SendEmailTemplatePage,
    EditEmailTemplatePage,
    UploadCsvPage
)


def _get_email_message():
    try:
        return get_email_body(Config.FUNCTIONAL_TEST_EMAIL,
                              Config.FUNCTIONAL_TEST_PASSWORD,
                              Config.EMAIL_NOTIFICATION_LABEL)
    except:
        pytest.fail("Couldn't get notification email")
    finally:
        remove_all_emails(email_folder=Config.EMAIL_NOTIFICATION_LABEL)


def test_create_email_template_and_send_from_csv(driver, base_url, test_profile):

    sign_in(driver, test_profile)

    dashboard_page = DashboardPage(driver)
    dashboard_page.click_email_templates()

    email_template_page = SendEmailTemplatePage(driver)
    email_template_page.click_add_new_template()

    new_email_template = EditEmailTemplatePage(driver)
    new_email_template.create_template()

    send_email_page = SendEmailTemplatePage(driver)
    send_email_page.click_send_from_csv_link()

    directory, filename = create_temp_csv(test_profile['email'], 'email address')

    upload_csv_page = UploadCsvPage(driver)
    upload_csv_page.upload_csv(directory, filename)

    email_body = _get_email_message()
    assert "The quick brown fox jumped over the lazy dog" in email_body

    upload_csv_page.sign_out()
