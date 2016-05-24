import pytest

from tests.pages import (
    SignInPage,
    TwoFactorPage,
    DashboardPage,
    SendEmailTemplatePage,
    EditEmailTemplatePage,
    SendSmsTemplatePage,
    EditSmsTemplatePage,
    ApiKeyPage
)

from tests.utils import get_verify_code


def sign_in(driver, test_profile):
    try:
        sign_in_page = SignInPage(driver)
        sign_in_page.get()
        assert sign_in_page.is_current()
        sign_in_page.login(test_profile)
        two_factor_page = TwoFactorPage(driver)
        assert two_factor_page.is_current()
        verify_code = get_verify_code()
        two_factor_page.verify(verify_code)
    except Exception as e:
        import pdb
        pdb.set_trace()
        pytest.fail("Unable to log in")


def get_service_templates_and_api_key_for_tests(driver, test_profile):

    sign_in(driver, test_profile)

    dashboard_page = DashboardPage(driver)
    dashboard_page.click_email_templates()
    service_id = dashboard_page.get_service_id()

    email_template_page = SendEmailTemplatePage(driver)
    email_template_page.click_edit_template()

    email_template = EditEmailTemplatePage(driver)
    email_template_id = email_template.get_id()

    dashboard_page = DashboardPage(driver)
    dashboard_page.click_sms_templates()

    sms_template_page = SendSmsTemplatePage(driver)
    sms_template_page.click_edit_template()

    edit_sms_template = EditSmsTemplatePage(driver)
    sms_template_id = edit_sms_template.get_id()

    dashboard_page = DashboardPage(driver)
    dashboard_page.click_api_keys_link()

    api_key_page = ApiKeyPage(driver)
    api_key_page.click_create_key()
    api_key_page.enter_key_name()
    api_key_page.click_continue()
    api_key = api_key_page.get_api_key()

    api_key_page.sign_out()

    return {'service_id': service_id, 'email_template_id': email_template_id, 'sms_template_id': sms_template_id, 'api_key': api_key}  # noqa
