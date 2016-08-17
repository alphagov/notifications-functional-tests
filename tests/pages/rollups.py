import pytest
from time import sleep

from tests.pages import (
    SignInPage,
    DashboardPage,
    SendEmailTemplatePage,
    EditEmailTemplatePage,
    SendSmsTemplatePage,
    EditSmsTemplatePage,
    ApiKeyPage
)

from tests.utils import do_verify


def sign_in(driver, test_profile):
    sign_in_page = SignInPage(driver)
    sign_in_page.get()
    assert sign_in_page.is_current()
    sign_in_page.login(test_profile)
    sleep(5)
    do_verify(driver, test_profile),


def get_service_templates_and_api_key_for_tests(driver, test_profile):

    dashboard_page = DashboardPage(driver)
    dashboard_page.click_email_templates()
    service_id = dashboard_page.get_service_id()

    email_template_page = SendEmailTemplatePage(driver)
    email_template_page.click_add_a_new_template()

    new_email_template_page = EditEmailTemplatePage(driver)
    new_email_template_page.create_template()

    email_template_page = SendEmailTemplatePage(driver)
    email_template_page.click_edit_template()

    edit_email_template_page = EditEmailTemplatePage(driver)
    email_template_id = edit_email_template_page.get_id()

    dashboard_page = DashboardPage(driver)
    dashboard_page.go_to_dashboard_for_service()
    dashboard_page.click_sms_templates()

    sms_template_page = SendSmsTemplatePage(driver)
    sms_template_page.click_add_new_template()

    new_sms_template = EditSmsTemplatePage(driver)
    new_sms_template.create_template()

    sms_template_page = SendSmsTemplatePage(driver)
    sms_template_page.click_edit_template()

    edit_sms_template = EditSmsTemplatePage(driver)
    sms_template_id = edit_sms_template.get_id()

    dashboard_page = DashboardPage(driver)
    dashboard_page.go_to_dashboard_for_service()
    dashboard_page.click_api_keys_link()

    api_key_page = ApiKeyPage(driver)
    api_key_page.click_create_key()

    api_key_page.click_key_type_radio()
    api_key_page.enter_key_name()
    api_key_page.click_continue()
    api_key = api_key_page.get_api_key()

    return {'service_id': service_id, 'email_template_id': email_template_id, 'sms_template_id': sms_template_id, 'api_key': api_key}  # noqa
