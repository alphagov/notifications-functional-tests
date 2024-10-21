import os
import uuid
from urllib.parse import urljoin, urlparse

from selenium.webdriver.common.by import By

from config import config, urls
from tests.pages import (
    DashboardPage,
    UnsubscribeRequestConfirmationPage,
    UnsubscribeRequestReportPage,
    UnsubscribeRequestReportsSummaryPage,
)
from tests.test_utils import create_email_template, go_to_templates_page, recordtime, send_notification_to_one_recipient


@recordtime
def test_unsubscribe_request_flow(request, driver, login_seeded_user, client_live_key):
    # Create a subscription template
    go_to_templates_page(driver)
    template_name = f"functional subscription email template {uuid.uuid4()}"
    content = "Hi ((name)), Is ((email address)) your email address? We want to send you some ((things))"
    template_id = create_email_template(driver, name=template_name, content=content, has_unsubscribe_link=True)

    dashboard_page = DashboardPage(driver)
    dashboard_page.go_to_dashboard_for_service(service_id=config["service"]["id"])

    # Send the notification via api
    send_notification_to_one_recipient(
        driver,
        template_name,
        "email",
        test=False,
        recipient_data=os.environ["FUNCTIONAL_TEST_EMAIL"],
        placeholders_number=2,
    )

    dashboard_page.click_continue()
    notification_id = dashboard_page.get_notification_id()
    one_off_email_data = client_live_key.get_notification_by_id(notification_id)
    generated_one_click_unsubscribe_url = one_off_email_data["one_click_unsubscribe_url"]
    assert one_off_email_data["template"]["id"] == template_id

    # simulate an unsubscribe request via the one click unsubscribe email header
    resp = client_live_key.post(generated_one_click_unsubscribe_url, data={})
    assert resp == {"result": "success", "message": "Unsubscribe successful"}

    # simulate an unsubscribe request via the one click unsubscribe url in the body of the email
    path = urlparse(generated_one_click_unsubscribe_url).path
    admin_url = urljoin(urls[os.environ["ENVIRONMENT"]]["admin"], path)
    driver.get(admin_url)

    unsubscribe_request_confirmation_page = UnsubscribeRequestConfirmationPage(driver)
    unsubscribe_request_confirmation_page.click_confirm()
    assert urlparse(driver.current_url).path == "/unsubscribe/confirmed"

    # Go to Email unsubscribe requests summary page
    dashboard_page.go_to_dashboard_for_service(service_id=config["service"]["id"])
    dashboard_page.click_email_unsubscribe_requests()

    # Go to email unsubscribe request report page
    unsubscribe_request_reports_summary_page = UnsubscribeRequestReportsSummaryPage(driver)
    unsubscribe_request_reports_summary_page.click_latest_unsubscribe_request_report_by_link()

    # Download email unsubscribe request report
    report_page = UnsubscribeRequestReportPage(driver)
    report_page.click_download_report_link()
    report_page.click_back_link()

    # Mark a report as completed
    unsubscribe_request_reports_summary_page.click_latest_unsubscribe_request_report_by_link()
    report_page.select_mark_as_complete_checkbox()
    report_page.click_continue()
    assert driver.find_element(By.CSS_SELECTOR, "tr td span").text == "Completed"
