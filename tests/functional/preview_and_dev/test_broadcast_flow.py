import uuid

from config import config
from tests.pages import (
    BasePage,
    BroadcastFreeformPage,
    DashboardPage,
    GovUkAlertsPage,
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

    # prepare alert
    current_alerts_page = BasePage(driver)
    test_uuid = str(uuid.uuid4())
    broadcast_title = "test broadcast" + test_uuid

    current_alerts_page.click_element_by_link_text("New alert")

    new_alert_page = BasePage(driver)
    new_alert_page.select_checkbox_or_radio(value='freeform')
    new_alert_page.click_continue()

    broadcast_freeform_page = BroadcastFreeformPage(driver)
    broadcast_content = "This is a test broadcast " + test_uuid
    broadcast_freeform_page.create_broadcast_content(broadcast_title, broadcast_content)
    broadcast_freeform_page.click_continue()

    prepare_alert_pages = BasePage(driver)
    prepare_alert_pages.click_element_by_link_text("Local authorities")
    prepare_alert_pages.click_element_by_link_text("Adur")
    prepare_alert_pages.select_checkbox_or_radio(value="wd20-E05007564")
    prepare_alert_pages.select_checkbox_or_radio(value="wd20-E05007565")
    prepare_alert_pages.click_continue()
    prepare_alert_pages.click_element_by_link_text("Preview this alert")
    # here check if selected areas displayed
    assert prepare_alert_pages.is_text_present_on_page("Cokeham")
    assert prepare_alert_pages.is_text_present_on_page("Eastbrook")

    prepare_alert_pages.click_continue()  # click "Submit for approval"
    assert prepare_alert_pages.is_text_present_on_page(f"{broadcast_title} is waiting for approval")

    prepare_alert_pages.sign_out()

    # approve the alert
    sign_in(driver, account_type='broadcast_approve_user')

    dashboard_page.click_element_by_link_text('Current alerts')
    current_alerts_page.click_element_by_link_text(broadcast_title)
    current_alerts_page.select_checkbox_or_radio(value="y")  # confirm approve alert
    current_alerts_page.click_continue()
    assert current_alerts_page.is_text_present_on_page("Live since ")
    alert_page_url = current_alerts_page.current_url

    # check if alert is published on gov.uk/alerts
    gov_uk_alerts_page = GovUkAlertsPage(driver)
    gov_uk_alerts_page.get()
    page_title = 'Current alerts'
    gov_uk_alerts_page.click_element_by_link_text(page_title)
    gov_uk_alerts_page.check_alert_is_published(page_title=page_title, broadcast_content=broadcast_content)

    # get back to the alert page
    current_alerts_page.get(alert_page_url)

    # stop sending the alert
    current_alerts_page.click_element_by_link_text('Stop sending')
    current_alerts_page.click_continue()  # stop broadcasting
    assert current_alerts_page.is_text_present_on_page('Stopped by Functional Tests - Broadcast User Approve')
    current_alerts_page.click_element_by_link_text('Past alerts')
    past_alerts_page = BasePage(driver)
    assert past_alerts_page.is_text_present_on_page(broadcast_title)

    # check if alert on gov.uk/alerts is moved to past alerts
    gov_uk_alerts_page = GovUkAlertsPage(driver)
    gov_uk_alerts_page.get()
    page_title = 'Past alerts'
    gov_uk_alerts_page.click_element_by_link_text(page_title)
    gov_uk_alerts_page.check_alert_is_published(page_title=page_title, broadcast_content=broadcast_content)

    # sign out
    current_alerts_page.get()
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
    prepare_alert_pages.click_element_by_link_text("Local authorities")
    prepare_alert_pages.click_element_by_link_text("Adur")
    prepare_alert_pages.select_checkbox_or_radio(value="wd20-E05007564")
    prepare_alert_pages.select_checkbox_or_radio(value="wd20-E05007565")
    prepare_alert_pages.click_continue()
    prepare_alert_pages.click_element_by_link_text("Preview this alert")
    # here check if selected areas displayed
    assert prepare_alert_pages.is_text_present_on_page("Cokeham")
    assert prepare_alert_pages.is_text_present_on_page("Eastbrook")

    prepare_alert_pages.click_continue()  # click "Submit for approval"
    assert prepare_alert_pages.is_text_present_on_page(f"{template_name} is waiting for approval")

    prepare_alert_pages.click_element_by_link_text("Discard this alert")
    prepare_alert_pages.click_element_by_link_text('Rejected alerts')
    rejected_alerts_page = BasePage(driver)
    assert rejected_alerts_page.is_text_present_on_page(template_name)

    delete_template(driver, template_name, service='broadcast_service')
