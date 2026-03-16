import uuid

from selenium.webdriver.common.by import By

from tests.pages import ViewEmailTemplatePage, ManageFilesForEmailTemplatePage
from tests.test_utils import (
    recordtime,
    delete_file_from_email_template_via_manage_files_page, delete_template,
    create_an_email_template_and_add_attach_a_file,
)


@recordtime
def test_attaching_files_to_emails_and_also_deleting_them_via_ui(driver, login_seeded_user, client_live_key):
    # Create an email template
    template_name = f"Functional Tests - upload/delete file to email template - {uuid.uuid4()}"
    content = "Hi ((name)), download this file:"
    file_name = "attachment.pdf"
    create_an_email_template_and_add_attach_a_file(driver, file_name, template_name, content)
    assert driver.find_element(By.CSS_SELECTOR, "h1").text.strip() == template_name
    assert driver.find_element(By.CSS_SELECTOR, "span[class='email-files-selected-counter']").text.strip() == \
           "1 file added"

    # Go to files list page
    template_page = ViewEmailTemplatePage(driver)
    template_page.click_manage_files_button()
    assert driver.find_element(By.CSS_SELECTOR, "h1").text.strip() == "Manage files"

    # Go to file management page and delete file
    manage_files_page = ManageFilesForEmailTemplatePage(driver)
    manage_files_page.click_manage_link(file_name)
    delete_file_from_email_template_via_manage_files_page(driver)
    assert driver.find_element(By.CSS_SELECTOR, "h1").text.strip() == template_name
    assert driver.find_element(By.CSS_SELECTOR, "div[class='banner-default-with-tick']").text.strip() == \
           f"‘{file_name}’ has been removed"
    assert driver.find_element(By.CSS_SELECTOR, "span[class='email-files-selected-counter']").text.strip() == \
           "No files added"

    # delete template
    delete_template(driver, template_name)
    current_templates = [x.text for x in driver.find_elements(By.CLASS_NAME, "template-list-item-label")]
    assert template_name not in current_templates
