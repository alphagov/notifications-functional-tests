import uuid

from tests.pages import ViewEmailTemplatePage, ManageFilesForEmailTemplatePage, ShowTemplatesPage, \
    ChangeRentionPeriodForEmailFilePage, EmailConfirmationSettingForEmailFilePage, ChangeLinkTextForEmailFilePage, \
    ManageEmailTemplateFilePage
from tests.test_utils import (
    recordtime,
    delete_file_from_email_template_via_manage_files_page,
    create_an_email_template_and_attach_a_file,
)


@recordtime
def test_send_one_off_email_with_file_via_ui(driver, login_seeded_user):
    # Test Creating an email template and attach a file to it
    template_name = f"Functional Tests - upload/delete file to email template - {uuid.uuid4()}"
    content = "Hi ((name)), download this file:"
    file_name = "attachment.pdf"
    create_an_email_template_and_attach_a_file(driver, file_name, template_name, content)

    # Confirm file has been attached to template on the Preview email template page
    view_email_template_page = ViewEmailTemplatePage(driver)
    assert view_email_template_page.get_h1_text() == template_name
    assert view_email_template_page.get_file_added_count_text() == "1 file added"

    # Test removing the file from the template
    view_email_template_page.click_manage_files_button()
    manage_files_page = ManageFilesForEmailTemplatePage(driver)
    assert manage_files_page.get_h1_text() == "Manage files"
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


@recordtime
def test_email_template_file_management_settings(driver, login_seeded_user):
    # Test Creating an email template and attach a file to it
    template_name = f"Functional Tests - file management settings- {uuid.uuid4()}"
    content = "Hi ((name)), download this file:"
    file_name = "attachment.pdf"
    create_an_email_template_and_attach_a_file(driver, file_name, template_name, content)

    # Confirm file has been attached to template on the Preview email template page
    view_email_template_page = ViewEmailTemplatePage(driver)
    assert view_email_template_page.get_h1_text() == template_name
    assert view_email_template_page.get_file_added_count_text() == "1 file added"

    # Go to file management page
    view_email_template_page.click_manage_files_button()
    manage_files_page = ManageFilesForEmailTemplatePage(driver)
    assert manage_files_page.get_h1_text() == "Manage files"
    manage_files_page.click_manage_link(file_name)
    manage_a_file_page = ManageEmailTemplateFilePage(driver)
    assert manage_a_file_page.get_h1_text() == file_name

    # Change link text
    link_text_label = "Link text"
    original_link_text = manage_a_file_page.get_file_setting_value(link_text_label)
    assert original_link_text == "Not set"
    manage_a_file_page.click_change_file_setting(link_text_label)
    change_link_text_page = ChangeLinkTextForEmailFilePage(driver)
    assert change_link_text_page.get_h1_text() == "Add link text"
    new_link_text = "file_download_link"
    change_link_text_page.fill_in_link_text(new_link_text)
    change_link_text_page.click_continue_button()

    # confirm link text change
    assert manage_a_file_page.get_file_setting_value(link_text_label) == new_link_text

    # Change retention period
    retention_period_label = "Available for"
    original_retention_period_text = manage_a_file_page.get_file_setting_value(retention_period_label)
    assert original_retention_period_text == "78 weeks after sending"
    manage_a_file_page.click_change_file_setting(retention_period_label)
    assert change_link_text_page.get_h1_text() == "How long the file is available"
    change_retention_period = ChangeRentionPeriodForEmailFilePage(driver)
    new_retention_period = "50"
    change_retention_period.fill_in_retention_period(new_retention_period)
    change_retention_period.click_continue_button()

    # confirm retention period change
    assert manage_a_file_page.get_file_setting_value(retention_period_label) == \
           f"{new_retention_period} weeks after sending"
    assert manage_a_file_page.get_h1_text() == file_name

    # Change email confirmation
    email_confirmation_label = "Ask recipient for email address"
    confirmation_label_choice = manage_a_file_page.get_file_setting_value(email_confirmation_label)
    assert confirmation_label_choice == "Yes"
    manage_a_file_page.click_change_file_setting(email_confirmation_label)
    email_confirmation_page = EmailConfirmationSettingForEmailFilePage(driver)
    assert email_confirmation_page.get_h1_text() == "Ask recipient for their email address"
    new_confirmation_label_choice = "No"
    email_confirmation_page.select_email_confirmation_option(new_confirmation_label_choice)
    email_confirmation_page.click_continue_button()

    # confirm email confirmation option change
    assert manage_a_file_page.get_h1_text() == file_name
    assert manage_a_file_page.get_file_setting_value(email_confirmation_label) == new_confirmation_label_choice

    # delete template which would also delete file
    manage_a_file_page.click_back_link()
    manage_files_page.click_back_link()
    assert view_email_template_page.get_h1_text() == template_name
    view_email_template_page.click_delete_template_link()
    view_email_template_page.click_template_deletion_confirmation_button()

    # confirm template has been deleted
    templates_page = ShowTemplatesPage(driver)
    assert templates_page.get_h1_text() == "Templates"
    assert template_name not in templates_page.get_all_listed_templates()
