import uuid

from config import config
from tests.pages import (
    BasePage,
    BroadcastFreeformPage,
    DashboardPage,
    ShowTemplatesPage,
)
from tests.pages.rollups import sign_in
from tests.test_utils import (
    create_broadcast_template,
    delete_template,
    go_to_templates_page,
    recordtime,
)


@recordtime
def test_prepare_broadcast_with_new_content(
    driver
):
    sign_in(driver, account_type='broadcast_create_user')

    dashboard_page = DashboardPage(driver)
    dashboard_page.click_element_by_link_text('Current alerts')

    current_alerts_page = BasePage(driver)
    broadcast_title = "test broadcast" + str(uuid.uuid4())

    current_alerts_page.click_element_by_link_text("New alert")

    new_alert_page = BasePage(driver)
    new_alert_page.select_checkbox_or_radio(value='freeform')
    new_alert_page.click_continue()

    broadcast_freeform_page = BroadcastFreeformPage(driver)
    message_content = "This is a test of write your own message. Test ID: " + str(uuid.uuid4())
    broadcast_freeform_page.create_broadcast_content(broadcast_title, message_content)
    broadcast_freeform_page.click_continue()

    prepare_alert_pages = BasePage(driver)
    prepare_alert_pages.click_element_by_link_text("Local authorities")
    prepare_alert_pages.click_element_by_link_text("Aberdeenshire")
    prepare_alert_pages.select_checkbox_or_radio(value="wd20-S13002866")
    prepare_alert_pages.click_continue()
    prepare_alert_pages.click_continue()  # click "Preview this alert"
    # here check if selected areas displayed
    assert prepare_alert_pages.is_text_present_on_page("Mearns")

    prepare_alert_pages.click_continue()  # click "Submit for approval"
    assert prepare_alert_pages.is_text_present_on_page(f"{broadcast_title} is waiting for approval")

    prepare_alert_pages.sign_out()

    sign_in(driver, account_type='broadcast_approve_user')

    dashboard_page.click_element_by_link_text('Current alerts')
    current_alerts_page.click_element_by_link_text(broadcast_title)
    current_alerts_page.select_checkbox_or_radio(value="y")  # confirm approve alert
    current_alerts_page.click_continue()
    assert current_alerts_page.is_text_present_on_page("Live since ")

    driver.get('https://www.integration.publishing.service.gov.uk/alerts/current-alerts')
    govuk_alerts_page = BasePage(driver)
    assert govuk_alerts_page.is_text_present_on_page(message_content)

    current_alerts_page.click_element_by_link_text('Stop sending')
    current_alerts_page.click_continue()  # stop broadcasting
    assert current_alerts_page.is_text_present_on_page('Stopped by Functional Tests - Broadcast User Approve')
    current_alerts_page.click_element_by_link_text('Past alerts')
    past_alerts_page = BasePage(driver)
    assert past_alerts_page.is_text_present_on_page(broadcast_title)

    current_alerts_page.sign_out()


@recordtime
def test_prepare_broadcast_with_template(
    driver
):
    sign_in(driver, account_type='broadcast_create_user')

    go_to_templates_page(driver, service='broadcast_service')
    template_name = "test broadcast" + str(uuid.uuid4())
    content = "This is a test only."
    create_broadcast_template(driver, name=template_name, content=content)

    dashboard_page = DashboardPage(driver)
    dashboard_page.go_to_dashboard_for_service(service_id=config['broadcast_service']['id'])

    dashboard_page.click_element_by_link_text('Current alerts')

    current_alerts_page = BasePage(driver)
    current_alerts_page.click_element_by_link_text("New alert")

    new_alert_page = BasePage(driver)
    new_alert_page.select_checkbox_or_radio(value='template')
    new_alert_page.click_continue()

    templates_page = ShowTemplatesPage(driver)
    templates_page.click_template_by_link_text(template_name)

    templates_page.click_element_by_link_text("Get ready to send")

    prepare_alert_pages = BasePage(driver)
    prepare_alert_pages.click_element_by_link_text("Test areas")
    prepare_alert_pages.select_checkbox_or_radio(value="test-santa-claus-village-rovaniemi-a")
    prepare_alert_pages.select_checkbox_or_radio(value="test-santa-claus-village-rovaniemi-b")
    prepare_alert_pages.click_continue()
    prepare_alert_pages.click_continue()  # click "Preview this alert"
    # here check if selected areas displayed
    assert prepare_alert_pages.is_text_present_on_page("Santa Claus Village, Rovaniemi A")
    assert prepare_alert_pages.is_text_present_on_page("Santa Claus Village, Rovaniemi B")

    prepare_alert_pages.click_continue()  # click "Submit for approval"
    assert prepare_alert_pages.is_text_present_on_page(f"{template_name} is waiting for approval")

    prepare_alert_pages.click_element_by_link_text("Discard this alert")
    prepare_alert_pages.click_element_by_link_text('Rejected alerts')
    rejected_alerts_page = BasePage(driver)
    assert rejected_alerts_page.is_text_present_on_page(template_name)

    delete_template(driver, template_name, service='broadcast_service')
