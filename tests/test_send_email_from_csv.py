import pytest

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


def _get_email_message(profile):
    try:
        return get_email_body(profile, profile.email_notification_label)
    except Exception as e:
        pytest.fail("Couldn't get notification email")
    finally:
        remove_all_emails(email_folder=profile.email_notification_label)


def test_create_email_template_and_send_from_csv(driver, base_url, profile, login_user):

    dashboard_page = DashboardPage(driver)
    dashboard_page.click_email_templates()

    email_template_page = SendEmailTemplatePage(driver)
    email_template_page.click_add_new_template()

    new_email_template = EditEmailTemplatePage(driver)
    new_email_template.create_template()

    send_email_page = SendEmailTemplatePage(driver)
    send_email_page.click_send_from_csv_link()

    directory, filename = create_temp_csv(profile.email, 'email address')

    upload_csv_page = UploadCsvPage(driver)
    upload_csv_page.upload_csv(directory, filename)

    email_body = _get_email_message(profile)
    assert "The quick brown fox jumped over the lazy dog" in email_body
    upload_csv_page.sign_out()
