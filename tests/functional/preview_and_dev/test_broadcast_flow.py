import uuid
from datetime import datetime, timedelta

from config import config
from tests.functional.preview_and_dev.sample_cap_xml import (
    ALERT_XML,
    CANCEL_XML,
)
from tests.pages import (
    BasePage,
    BroadcastFreeformPage,
    DashboardPage,
    ShowTemplatesPage,
)
from tests.pages.rollups import sign_in
from tests.test_utils import (
    check_alert_is_published_on_govuk_alerts,
    convert_naive_utc_datetime_to_cap_standard_string,
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

    check_alert_is_published_on_govuk_alerts(driver, 'Current alerts', broadcast_content)

    # get back to the alert page
    current_alerts_page.get(alert_page_url)

    # stop sending the alert
    current_alerts_page.click_element_by_link_text('Stop sending')
    current_alerts_page.click_continue()  # stop broadcasting
    assert current_alerts_page.is_text_present_on_page('Stopped by Functional Tests - Broadcast User Approve')
    current_alerts_page.click_element_by_link_text('Past alerts')
    past_alerts_page = BasePage(driver)
    assert past_alerts_page.is_text_present_on_page(broadcast_title)

    check_alert_is_published_on_govuk_alerts(driver, 'Past alerts', broadcast_content)

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

    prepare_alert_pages.sign_out()


@recordtime
def test_create_and_then_reject_broadcast_using_the_api(driver, broadcast_client):
    sent_time = convert_naive_utc_datetime_to_cap_standard_string(datetime.utcnow() - timedelta(hours=1))
    cancel_time = convert_naive_utc_datetime_to_cap_standard_string(datetime.utcnow())
    expires_time = convert_naive_utc_datetime_to_cap_standard_string(datetime.utcnow() + timedelta(hours=1))
    identifier = uuid.uuid4()
    event = f'test broadcast {identifier}'

    new_alert_xml = ALERT_XML.format(identifier=identifier, alert_sent=sent_time, event=event)
    broadcast_client.post_broadcast_data(new_alert_xml)

    sign_in(driver, account_type='broadcast_approve_user')
    page = BasePage(driver)
    page.click_element_by_link_text('Current alerts')
    page.click_element_by_link_text(event)

    assert page.is_text_present_on_page(f'An API call wants to broadcast {event}')

    reject_broadcast_xml = CANCEL_XML.format(
        identifier=identifier,
        alert_sent=sent_time,
        cancel_sent=cancel_time,
        event=event,
        expires=expires_time,
    )
    broadcast_client.post_broadcast_data(reject_broadcast_xml)

    page.click_element_by_link_text('Rejected alerts')
    assert page.is_text_present_on_page(event)

    page.sign_out()


@recordtime
def test_cancel_live_broadcast_using_the_api(driver, broadcast_client):
    sent_time = convert_naive_utc_datetime_to_cap_standard_string(datetime.utcnow() - timedelta(hours=1))
    cancel_time = convert_naive_utc_datetime_to_cap_standard_string(datetime.utcnow())
    expires_time = convert_naive_utc_datetime_to_cap_standard_string(datetime.utcnow() + timedelta(hours=1))
    identifier = uuid.uuid4()
    event = f'test broadcast {identifier}'

    new_alert_xml = ALERT_XML.format(identifier=identifier, alert_sent=sent_time, event=event)
    broadcast_client.post_broadcast_data(new_alert_xml)

    sign_in(driver, account_type='broadcast_approve_user')

    page = BasePage(driver)
    page.click_element_by_link_text('Current alerts')
    page.click_element_by_link_text(event)
    page.select_checkbox_or_radio(value="y")  # confirm approve alert
    page.click_continue()
    assert page.is_text_present_on_page("Live since ")
    alert_page_url = page.current_url

    check_alert_is_published_on_govuk_alerts(
        driver,
        page_title='Current alerts',
        broadcast_content='A severe flood warning has been issued',
    )

    cancel_broadcast_xml = CANCEL_XML.format(
        identifier=identifier,
        alert_sent=sent_time,
        cancel_sent=cancel_time,
        event=event,
        expires=expires_time,
    )
    broadcast_client.post_broadcast_data(cancel_broadcast_xml)

    # go back to the page for the current alert
    page.get(alert_page_url)

    # assert that it's now cancelled
    assert page.is_text_present_on_page('Stopped by an API call')
    page.click_element_by_link_text('Past alerts')
    assert page.is_text_present_on_page(event)

    check_alert_is_published_on_govuk_alerts(
        driver,
        page_title='Past alerts',
        broadcast_content='A severe flood warning has been issued',
    )

    page.get()
    page.sign_out()
