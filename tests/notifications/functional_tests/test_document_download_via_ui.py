import uuid

from tests.pages import ViewEmailTemplatePage, ManageFilesForEmailTemplatePage, ShowTemplatesPage
from tests.test_utils import (
    recordtime,
    delete_file_from_email_template_via_manage_files_page, delete_template,
    create_an_email_template_and_add_attach_a_file,
)


@recordtime
def test_attaching_files_to_emails_and_also_deleting_them_via_ui(driver, login_seeded_user):
    # Create an email template
    template_name = f"Functional Tests - upload/delete file to email template - {uuid.uuid4()}"
    content = "Hi ((name)), download this file:"
    file_name = "attachment.pdf"
    create_an_email_template_and_add_attach_a_file(driver, file_name, template_name, content)

    # Confirm file has been attached to template on the Preview email template page
    view_email_template_page = ViewEmailTemplatePage(driver)
    assert view_email_template_page.get_h1_text() == template_name
    assert view_email_template_page.get_file_added_count_text() == "1 file added"

    # Go to files list page
    view_email_template_page.click_manage_files_button()
    manage_files_page = ManageFilesForEmailTemplatePage(driver)
    assert manage_files_page.get_h1_text() == "Manage files"

    # Go to file management page for the file attached and delete file
    manage_files_page.click_manage_link(file_name)
    delete_file_from_email_template_via_manage_files_page(driver)

    # Confirm file has been removed on Preview email template page
    assert view_email_template_page.get_page_banner_text() == f"‘{file_name}’ has been removed"
    assert view_email_template_page.get_file_added_count_text() == "No files added"

    # delete template
    assert view_email_template_page.get_h1_text() == template_name
    view_email_template_page.click_delete_template_link()
    view_email_template_page.click_template_deletion_confirmation_button()

    # confirm template has been deleted
    templates_page = ShowTemplatesPage(driver)
    assert templates_page.get_h1_text() == "Templates"
    assert template_name not in templates_page.get_all_listed_templates()
