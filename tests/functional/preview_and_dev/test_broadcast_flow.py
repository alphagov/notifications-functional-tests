import uuid

from config import config
from tests.pages import (
    BroadcastFreeformPage,
    CurrentAlertsPage,
    DashboardPage,
    NewAlertPage,
    PrepareAlertsPages,
    ShowTemplatesPage,
)
from tests.pages.rollups import sign_in_broadcast_user
from tests.test_utils import (
    create_broadcast_template,
    delete_template,
    go_to_templates_page,
    recordtime,
)


@recordtime
def test_prepare_broadcast_with_new_content(
    driver, seeded_client
):
    sign_in_broadcast_user(driver)

    dashboard_page = DashboardPage(driver)
    dashboard_page.click_current_alerts()

    current_alerts_page = CurrentAlertsPage(driver)
    current_alerts_page.is_text_present_on_page("You do not have any current alerts")
    current_alerts_page.click_new_alert()

    new_alert_page = NewAlertPage(driver)
    new_alert_page.select_write_your_own_message()
    broadcast_title = "test broadcast" + str(uuid.uuid4())
    broadcast_content = "This is a test of write your own message."
    broadcast_freeform_page = BroadcastFreeformPage(driver)
    broadcast_freeform_page.create_broadcast_content(broadcast_title, broadcast_content)
    broadcast_freeform_page.click_continue()

    prepare_alert_pages = PrepareAlertsPages(driver)
    prepare_alert_pages.click_element_by_link_text("Test areas")
    prepare_alert_pages.select_checkbox_or_radio(value="test-santa-claus-village-rovaniemi-a")
    prepare_alert_pages.select_checkbox_or_radio(value="test-santa-claus-village-rovaniemi-b")
    prepare_alert_pages.click_continue()
    prepare_alert_pages.click_continue()  # click "Preview this alert"
    # here check if selected areas displayed
    assert prepare_alert_pages.is_text_present_on_page("Santa Claus Village, Rovaniemi A")
    assert prepare_alert_pages.is_text_present_on_page("Santa Claus Village, Rovaniemi B")

    prepare_alert_pages.click_continue()  # click "Submit for approval"
    assert prepare_alert_pages.is_text_present_on_page(f"{broadcast_title} is waiting for approval")

    prepare_alert_pages.click_element_by_link_text("Discard this alert")


@recordtime
def test_prepare_broadcast_with_template(
    driver, seeded_client
):
    go_to_templates_page(driver, service='broadcast_service')
    template_name = "test broadcast" + str(uuid.uuid4())
    content = "This is a test only."
    create_broadcast_template(driver, name=template_name, content=content)

    dashboard_page = DashboardPage(driver)
    dashboard_page.go_to_dashboard_for_service(service_id=config['broadcast_service']['id'])

    dashboard_page.click_current_alerts()
    current_alerts_page = CurrentAlertsPage(driver)
    assert not current_alerts_page.is_text_present_on_page(template_name)
    current_alerts_page.click_new_alert()

    new_alert_page = NewAlertPage(driver)
    new_alert_page.select_use_a_template()

    templates_page = ShowTemplatesPage(driver)
    templates_page.click_template_by_link_text(template_name)

    templates_page.click_element_by_link_text("Get ready to send")

    prepare_alert_pages = PrepareAlertsPages(driver)
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

    delete_template(driver, template_name, service='broadcast_service')
