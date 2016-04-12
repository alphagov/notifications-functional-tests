from requests import session

from config import Config

from tests.pages.rollups import sign_in

from tests.utils import (
    create_temp_csv,
    get_sms_via_heroku
)

from tests.pages import (
    DashboardPage,
    SendSmsTemplatePage,
    EditSmsTemplatePage,
    UploadCsvPage
)


def test_create_sms_template_and_send_from_csv(driver, base_url, test_profile):

    sign_in(driver, test_profile)

    dashboard_page = DashboardPage(driver)
    dashboard_page.click_sms_templates()

    sms_template_page = SendSmsTemplatePage(driver)
    sms_template_page.click_add_new_template()

    new_sms_template = EditSmsTemplatePage(driver)
    new_sms_template.create_template()

    send_sms_page = SendSmsTemplatePage(driver)
    send_sms_page.click_send_from_csv_link()

    directory, filename = create_temp_csv(Config.TWILIO_TEST_NUMBER, 'phone number')

    upload_csv_page = UploadCsvPage(driver)
    upload_csv_page.upload_csv(directory, filename)

    # check we are on jobs page and status is sending?
    # assert '/jobs' in post_check_sms.url

    message = get_sms_via_heroku(session())
    assert "The quick brown fox jumped over the lazy dog" in message
    upload_csv_page.sign_out()
