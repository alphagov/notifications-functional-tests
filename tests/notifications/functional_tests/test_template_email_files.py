import uuid

from selenium.webdriver.common.by import By

from config import config
from tests.pages import ShowTemplatesPage, EditEmailTemplatePage, ViewEmailTemplatePage, AddFileToEmailTemplatePage, \
    DashboardPage
from tests.test_utils import (
    create_email_template,
    go_to_templates_page,
    recordtime, add_file_to_an_email_template,
)

@recordtime
def test_attaching_files_to_emails_and_also_deleting_them_via_ui(driver, login_seeded_user, client_live_key):
    # Create an email template
    template_name = f"upload/delete file to email template {uuid.uuid4()}"
    content = "Hi ((name)), download these files:"
    go_to_templates_page(driver)
    create_email_template(driver, name=template_name, content=content, has_unsubscribe_link=True)
    go_to_templates_page(driver)
    dashboard_page = DashboardPage(driver)
    service_id = config["service"]["id"]
    dashboard_page.go_to_dashboard_for_service(service_id=service_id)

    # Attach a file to the template
    dashboard_page = DashboardPage(driver)
    dashboard_page.go_to_dashboard_for_service(service_id=service_id)
    file_name = "tests/test_files/attachment.pdf"
    add_file_to_an_email_template(driver, template_name, file_name, service_id)
    assert driver.find_element(By.CLASS_NAME, "edit-template-link-attachment").text == "Manage attachment"


