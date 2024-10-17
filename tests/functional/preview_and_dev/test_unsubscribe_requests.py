import os
import uuid
from urllib.parse import urlparse, urljoin

from selenium.webdriver.common.by import By

from config import config
from tests.functional.preview_and_dev.test_seeded_user import get_dashboard_stats, assert_dashboard_stats
from tests.pages import DashboardPage, ShowTemplatesPage, ViewTemplatePage, UnsubscribeRequestConfirmationPage
from tests.test_utils import recordtime, go_to_templates_page, create_email_template, send_notification_to_one_recipient


@recordtime
def test_unsubscribe_request_flow(request, driver, login_seeded_user, client_live_key):
    # Create a subscription template and assert that the template was created
    go_to_templates_page(driver)
    test_name = request.node.name
    template_name = f"functional subscription email template {uuid.uuid4()}"
    content = "Hi ((name)), Is ((email address)) your email address? We want to send you some ((things))"
    template_id = create_email_template(driver, name=template_name, content=content, has_unsubscribe_link=True)

    dashboard_page = DashboardPage(driver)
    dashboard_page.go_to_dashboard_for_service(service_id=config["service"]["id"])
    dashboard_stats_before = get_dashboard_stats(dashboard_page, "email", template_id)

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

    dashboard_page.go_to_dashboard_for_service(service_id=config["service"]["id"])
    dashboard_stats_after = get_dashboard_stats(dashboard_page, "email", template_id)
    assert_dashboard_stats(dashboard_stats_before, dashboard_stats_after)

    # simulate an unsubscribe request via the one click unsubscribe email header
    resp = client_live_key.post(generated_one_click_unsubscribe_url, data={})
    assert resp == {
        "result": "success",
        "message": "Unsubscribe successful"
    }

    # simulate an unsubscribe request via the one click unsubscribe url in the body of the email
    path = urlparse(generated_one_click_unsubscribe_url).path
    admin_url = urljoin(os.environ["FUNCTIONAL_TESTS_LOCAL_ADMIN_HOST"], path)
    driver.get(admin_url)

    unsubscribe_request_confirmation_page = UnsubscribeRequestConfirmationPage(driver)
    unsubscribe_request_confirmation_page.click_confirm()
    assert driver.find_elements(By.CSS_SELECTOR, "h1")[0].text == "We have your request to unsubscribe"

    # View and download an Unsubscribe Request Reports
    dashboard_page = DashboardPage(driver)
    dashboard_page.go_to_dashboard_for_service(config["service"]["id"])

