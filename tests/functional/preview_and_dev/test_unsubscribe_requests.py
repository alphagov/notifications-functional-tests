import os
import uuid

from selenium.webdriver.common.by import By

from config import config
from tests.functional.preview_and_dev.test_seeded_user import get_dashboard_stats, assert_dashboard_stats
from tests.pages import DashboardPage
from tests.test_utils import recordtime, go_to_templates_page, create_email_template, send_notification_to_one_recipient


@recordtime
def test_unsubscribe_request_flow(driver, login_seeded_user, client_live_key):
    # Create a subscription template and assert that the template was created
    go_to_templates_page(driver)
    test_name = "subscription functional test"
    template_name = f"functional subscription email template {uuid.uuid4()}"
    content = "Hi ((name)), Is ((email address)) your email address? We want to send you some ((things))"
    template_id = create_email_template(driver, name=template_name, content=content, has_unsubscribe_link=True)

    dashboard_page = DashboardPage(driver)
    dashboard_page.go_to_dashboard_for_service(service_id=config["service"]["id"])
    dashboard_stats_before = get_dashboard_stats(dashboard_page, "email", template_id)

    # Send the notification and retrieve and retrieve the generated unsubscribe link from the notification response
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
    one_off_email = client_live_key.get_notification_by_id(notification_id)
    assert one_off_email.get("created_by_name") == f"Preview admin tests user - {test_name}"

    dashboard_page.go_to_dashboard_for_service(service_id=config["service"]["id"])
    dashboard_stats_after = get_dashboard_stats(dashboard_page, "email", template_id)
    assert_dashboard_stats(dashboard_stats_before, dashboard_stats_after)

    # go_to_templates_page(driver)
    # current_templates = [x.text for x in driver.find_elements(By.CLASS_NAME, "template-list-item-label")]
    # if len(current_templates) == 0:
    #     current_templates = [x.text for x in driver.find_elements(By.CLASS_NAME, "message-name")]
    # assert template_name in current_templates


    # one_click_unsubscribe_url = data.get("one_click_unsubscribe_url")
    # assert one_click_unsubscribe_url is None
