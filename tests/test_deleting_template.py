from tests.pages import (
    DashboardPage,
    SendEmailTemplatePage,
    EditEmailTemplatePage
)


def test_create_edit_and_delete_email_template(driver, base_url, profile, login_user):
    test_name = 'edit/delete test'

    dashboard_page = DashboardPage(driver)
    dashboard_page.click_email_templates()

    existing_templates = [x.text for x in driver.find_elements_by_class_name('message-name')]

    all_templates_page = SendEmailTemplatePage(driver)
    all_templates_page.click_add_new_template()

    template_page = EditEmailTemplatePage(driver)
    template_page.create_template(name=test_name)

    assert test_name in [x.text for x in driver.find_elements_by_class_name('message-name')]

    all_templates_page.click_edit_template()
    template_page.click_delete()

    assert [x.text for x in driver.find_elements_by_class_name('message-name')] == existing_templates
