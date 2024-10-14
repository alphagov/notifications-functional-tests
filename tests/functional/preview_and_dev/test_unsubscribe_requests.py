import uuid

from selenium.webdriver.common.by import By

from tests.test_utils import recordtime, go_to_templates_page, create_email_template


@recordtime
def test_unsubscribe_request_flow(driver, login_seeded_user, client_live_key):
    # Create a subscription template and assert that the template was created
    template_name = f"functional subscription email template {uuid.uuid4()}"
    go_to_templates_page(driver)

    template_id = create_email_template(driver, name=template_name, content=None, has_unsubscribe_link=True)
    go_to_templates_page(driver)
    current_templates = [x.text for x in driver.find_elements(By.CLASS_NAME, "template-list-item-label")]
    if len(current_templates) == 0:
        current_templates = [x.text for x in driver.find_elements(By.CLASS_NAME, "message-name")]
    assert template_name in current_templates

    # Retrieve template and assert that it's has_unsubscribe_link attribute is True



