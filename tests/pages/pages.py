import os
import shutil

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import (
    NoSuchElementException, StaleElementReferenceException, TimeoutException, WebDriverException
)

from retry import retry
from config import config

from tests.pages.element import (
    BasePageElement,
    EmailInputElement,
    FileInputElement,
    KeyNameInputElement,
    MobileInputElement,
    NameInputElement,
    PasswordInputElement,
    ServiceInputElement,
    SubjectInputElement,
    SmsInputElement,
    TemplateContentElement
)

from tests.pages.locators import (
    AddServicePageLocators,
    ApiIntegrationPageLocators,
    ApiKeysPageLocators,
    ChangeNameLocators,
    CommonPageLocators,
    EditTemplatePageLocators,
    EmailReplyToLocators,
    InviteUserPageLocators,
    LetterPreviewPageLocators,
    MainPageLocators,
    NavigationLocators,
    ServiceSettingsLocators,
    SingleRecipientLocators,
    SmsSenderLocators,
    TemplatePageLocators,
    TeamMembersPageLocators,
    UploadCsvLocators,
    VerifyPageLocators,
    ViewTemplatePageLocators
)


class RetryException(Exception):
    pass


class AntiStale:
    def __init__(self, driver, locator, webdriverwait_func):
        """
        webdriverwait_func is a function that takes in a locator and returns an element. Probably a webdriverwait.
        """
        self.driver = driver
        self.webdriverwait_func = webdriverwait_func
        self.locator = locator
        # kick it off
        self.element = self.webdriverwait_func(self.locator)

    @retry(RetryException, tries=5)
    def retry_on_stale(self, callable):
        try:
            return callable()
        except StaleElementReferenceException:
            self.reset_element()

    def reset_element(self):
        self.element = self.webdriverwait_func(self.locator)

        raise RetryException('StaleElement {}'.format(self.locator))


class AntiStaleElement(AntiStale):
    def click(self):
        def _click():
            # an element might be hidden underneath other elements (eg sticky nav items). To counter this, we can use
            # the scrollIntoView function to bring it to the top of the page
            self.driver.execute_script('arguments[0].scrollIntoViewIfNeeded()', self.element)
            try:
                self.element.click()
            except WebDriverException:
                self.driver.execute_script('arguments[0].scrollIntoView()', self.element)
                self.element.click()
        return self.retry_on_stale(_click)

    def __getattr__(self, attr):
        return self.retry_on_stale(lambda: getattr(self.element, attr))


class AntiStaleElementList(AntiStale):
    def __getitem__(self, index):
        class AntiStaleListItem:
            def click(item_self):
                return self.retry_on_stale(lambda: self.element[index].click())

            def __getattr__(item_self, attr):
                return self.retry_on_stale(lambda: getattr(self.element[index], attr))

        return AntiStaleListItem()


class BasePage(object):

    sign_out_link = NavigationLocators.SIGN_OUT_LINK

    def __init__(self, driver):
        self.base_url = config['notify_admin_url']
        self.driver = driver

    def wait_for_invisible_element(self, locator):
        return AntiStaleElement(
            self.driver,
            locator,
            lambda locator: WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(locator)
            )
        )

    def wait_for_element(self, locator, time=10):
        return AntiStaleElement(
            self.driver,
            locator,
            lambda locator: WebDriverWait(self.driver, time).until(
                EC.visibility_of_element_located(locator),
                EC.presence_of_element_located(locator)
            )
        )

    def wait_for_elements(self, locator):
        return AntiStaleElementList(
            self.driver,
            locator,
            lambda locator: WebDriverWait(self.driver, 10).until(
                EC.visibility_of_all_elements_located(locator),
                EC.presence_of_all_elements_located(locator)
            )
        )

    def sign_out(self):
        element = self.wait_for_element(BasePage.sign_out_link)
        element.click()
        self.driver.delete_all_cookies()

    def wait_until_url_is(self, url):
        return WebDriverWait(self.driver, 10).until(
            self.url_contains(url)
        )

    def url_contains(self, url):
        def check_contains_url(driver):
            return url in self.driver.current_url
        return check_contains_url

    def select_checkbox_or_radio(self, element):
        if not element.get_attribute('checked'):
            element.click()
            assert element.get_attribute('checked')

    def unselect_checkbox(self, element):
        if element.get_attribute('checked'):
            element.click()
            assert not element.get_attribute('checked')

    def click_templates(self):
        element = self.wait_for_element(NavigationLocators.TEMPLATES_LINK)
        element.click()

    def click_settings(self):
        element = self.wait_for_element(NavigationLocators.SETTINGS_LINK)
        element.click()

    def click_save(self, time=10):
        element = self.wait_for_element(CommonPageLocators.CONTINUE_BUTTON, time=time)
        element.click()

    def click_continue(self):
        element = self.wait_for_element(CommonPageLocators.CONTINUE_BUTTON)
        element.click()

    def is_page_title(self, expected_page_title):
        element = self.wait_for_element(CommonPageLocators.H1)
        return element.text == expected_page_title

    def is_text_present_on_page(self, search_text):
        return search_text in self.driver.page_source

    def get_template_id(self):
        # e.g.
        # http://localhost:6012/services/237dd966-b092-42ab-b406-0a00187d007f/templates/4808eb34-5225-492b-8af2-14b232f05b8e/edit
        # circle back and do better
        return self.driver.current_url.split('/templates/')[1].split('/')[0]


class HomePage(BasePage):

    def accept_cookie_warning(self):
        # if the cookie warning isn't present, this does nothing
        try:
            self.wait_for_element(CommonPageLocators.ACCEPT_COOKIE_BUTTON, time=1).click()
        except (NoSuchElementException, TimeoutException):
            return


class MainPage(BasePage):

    set_up_account_button = MainPageLocators.SETUP_ACCOUNT_BUTTON

    def get(self):
        self.driver.get(self.base_url)

    def click_set_up_account(self):
        element = self.wait_for_element(MainPage.set_up_account_button)
        element.click()


class RegistrationPage(BasePage):

    name_input = NameInputElement()
    email_input = EmailInputElement()
    mobile_input = MobileInputElement()
    password_input = PasswordInputElement()
    continue_button = CommonPageLocators.CONTINUE_BUTTON

    def is_current(self):
        return self.wait_until_url_is(self.base_url + '/register')

    def register(self):
        self.name_input = config['user']['name']
        self.email_input = config['user']['email']
        self.mobile_input = config['user']['mobile']
        self.password_input = config['user']['password']
        self.click_continue_button()

    def click_continue_button(self):
        element = self.wait_for_element(RegistrationPage.continue_button)
        element.click()


class AddServicePage(BasePage):

    service_input = ServiceInputElement()
    org_type_input = AddServicePageLocators.ORG_TYPE_INPUT
    add_service_button = AddServicePageLocators.ADD_SERVICE_BUTTON

    def is_current(self):
        return self.wait_until_url_is(self.base_url + '/add-service?first=first')

    def add_service(self, name):
        self.service_input = name
        try:
            self.click_org_type_input()
        except NoSuchElementException:
            pass

        self.click_add_service_button()

    def click_add_service_button(self):
        element = self.wait_for_element(AddServicePage.add_service_button)
        element.click()

    def click_org_type_input(self):
        try:
            element = self.wait_for_invisible_element(AddServicePage.org_type_input)
            element.click()
        except TimeoutException:
            pass


class SignInPage(BasePage):

    email_input = EmailInputElement()
    password_input = PasswordInputElement()
    continue_button = CommonPageLocators.CONTINUE_BUTTON

    def get(self):
        self.driver.get(self.base_url + '/sign-in')

    def is_current(self):
        return self.wait_until_url_is(self.base_url + '/sign-in')

    def fill_login_form(self, email, password):
        self.email_input = email
        self.password_input = password

    def click_continue_button(self):
        element = self.wait_for_element(SignInPage.continue_button)
        element.click()

    def login(self, email, password):
        self.fill_login_form(email, password)
        self.click_continue_button()


class VerifyPage(BasePage):

    sms_input = SmsInputElement()
    continue_button = CommonPageLocators.CONTINUE_BUTTON

    def click_continue_button(self):
        element = self.wait_for_element(VerifyPage.continue_button)
        element.click()

    def verify(self, code):
        element = self.wait_for_element(VerifyPageLocators.SMS_INPUT)
        element.clear()
        self.sms_input = code
        self.click_continue_button()

    def has_code_error(self):
        try:
            self.driver.find_element_by_class_name('error-message')
        except NoSuchElementException:
            return False
        return True


class DashboardPage(BasePage):

    h2 = (By.CLASS_NAME, 'navigation-service-name')
    sms_templates_link = (By.LINK_TEXT, 'Text message templates')
    email_templates_link = (By.LINK_TEXT, 'Email templates')
    team_members_link = (By.LINK_TEXT, 'Team members')
    api_keys_link = (By.LINK_TEXT, 'API integration')
    total_email_div = (By.CSS_SELECTOR, '#total-email .big-number-number')
    total_sms_div = (By.CSS_SELECTOR, '#total-sms .big-number-number')
    total_letter_div = (By.CSS_SELECTOR, '#total-letters .big-number-number')
    inbox_link = (By.CSS_SELECTOR, '#total-received a')
    navigation = (By.CLASS_NAME, 'navigation')

    def _message_count_for_template_div(self, template_id):
        return (By.ID, template_id)

    def is_current(self, service_id):
        expected = '{}/services/{}/dashboard'.format(self.base_url, service_id)
        return self.driver.current_url == expected

    def h2_is_service_name(self, expected_name):
        element = self.wait_for_element(DashboardPage.h2)
        return expected_name == element.text

    def click_sms_templates(self):
        element = self.wait_for_element(DashboardPage.sms_templates_link)
        element.click()

    def click_email_templates(self):
        element = self.wait_for_element(DashboardPage.email_templates_link)
        element.click()

    def click_email_header(self):
        element = self.wait_for_element(DashboardPage.email_filter_link)
        element.click()

    def click_team_members_link(self):
        element = self.wait_for_element(DashboardPage.team_members_link)
        element.click()

    def click_user_profile_link(self, link_text):
        element = self.wait_for_element((By.LINK_TEXT, link_text))
        element.click()

    def click_api_keys_link(self):
        element = self.wait_for_element(DashboardPage.api_keys_link)
        element.click()

    def click_inbox_link(self):
        element = self.wait_for_element(DashboardPage.inbox_link)
        element.click()

    def get_service_id(self):
        return self.driver.current_url.split('/services/')[1].split('/')[0]

    def get_navigation_list(self):
        element = self.wait_for_element(DashboardPage.navigation)
        return element.text

    def get_notification_id(self):
        return self.driver.current_url.split('notification/')[1].split('?')[0]

    def go_to_dashboard_for_service(self, service_id=None):
        if not service_id:
            service_id = self.get_service_id()
        url = "{}/services/{}/dashboard".format(self.base_url, service_id)
        self.driver.get(url)

    def get_total_message_count(self, message_type):
        if message_type == 'email':
            target_div = DashboardPage.total_email_div
        elif message_type == 'letter':
            target_div = DashboardPage.total_letter_div
        else:
            target_div = DashboardPage.total_sms_div
        element = self.wait_for_element(target_div)

        return int(element.text)

    def get_template_message_count(self, template_id):
        messages_sent_count_for_template_div = self._message_count_for_template_div(template_id)
        element = self.wait_for_element(messages_sent_count_for_template_div)

        return int(element.text)


class ShowTemplatesPage(BasePage):
    add_new_template_link = (By.CSS_SELECTOR, "button[value='add-new-template']")
    add_new_folder_link = (By.CSS_SELECTOR, "button[value='add-new-folder']")
    add_to_new_folder_link = (By.CSS_SELECTOR, "button[value='move-to-new-folder']")
    move_to_existing_folder_link = (By.CSS_SELECTOR, "button[value='move-to-existing-folder']")
    email_filter_link = (By.LINK_TEXT, 'Email')

    email_radio = (By.CSS_SELECTOR, "input[type='radio'][value='email']")
    text_message_radio = (By.CSS_SELECTOR, "input[type='radio'][value='sms']")
    letter_radio = (By.CSS_SELECTOR, "input[type='radio'][value='letter']")
    continue_button = (By.CSS_SELECTOR, 'main [type=submit]')

    add_new_folder_textbox = BasePageElement(name='add_new_folder_name')
    add_to_new_folder_textbox = BasePageElement(name='move_to_new_folder_name')

    root_template_folder_radio = (By.CSS_SELECTOR, "input[type='radio'][value='__NONE__']")

    @staticmethod
    def template_link_text(link_text):
        return (
            By.XPATH,
            "//nav[contains(@id,'template-list')]//a/span[contains(normalize-space(.), '{}')]".format(link_text)
        )

    @staticmethod
    def template_checkbox(template_id):
        return (By.CSS_SELECTOR, "input[type='checkbox'][value='{}']".format(template_id))

    def click_add_new_template(self):
        element = self.wait_for_element(self.add_new_template_link)
        element.click()

    def click_add_new_folder(self, folder_name):
        element = self.wait_for_element(self.add_new_folder_link)
        element.click()

        self.add_new_folder_textbox = folder_name

        # green submit button
        element = self.wait_for_element(self.add_new_folder_link)
        element.click()

    def click_email_filter_link(self):
        element = self.wait_for_element(self.email_filter_link)
        element.click()

    def click_template_by_link_text(self, link_text):
        element = self.wait_for_element(self.template_link_text(link_text))
        element.click()

    def _select_template_type(self, type):
        # wait for continue button to be displayed - sticky nav has rendered properly
        # we've seen issues
        radio_element = self.wait_for_invisible_element(type)
        self.select_checkbox_or_radio(radio_element)

        continue_element = self.wait_for_element(self.continue_button)
        continue_element.click()

    def select_email(self):
        self._select_template_type(self.email_radio)

    def select_text_message(self):
        self._select_template_type(self.text_message_radio)

    def select_letter(self):
        self._select_template_type(self.letter_radio)

    def select_template_checkbox(self, template_id):
        element = self.wait_for_invisible_element(self.template_checkbox(template_id))
        self.select_checkbox_or_radio(element)

    def add_to_new_folder(self, folder_name):
        # grey button to go to the name input box
        element = self.wait_for_element(self.add_to_new_folder_link)
        element.click()
        self.add_to_new_folder_textbox = folder_name

        # green submit button
        element = self.wait_for_element(self.add_to_new_folder_link)
        element.click()

    def move_to_root_template_folder(self):
        move_button = self.wait_for_element(self.move_to_existing_folder_link)
        move_button.click()
        # wait for continue button to be displayed - sticky nav has rendered properly
        # we've seen issues
        continue_element = self.wait_for_element(self.continue_button)
        radio_element = self.wait_for_invisible_element(self.root_template_folder_radio)

        self.select_checkbox_or_radio(radio_element)
        continue_element.click()

    def get_folder_by_name(self, folder_name):
        try:
            return self.wait_for_invisible_element(self.template_link_text(folder_name))
        except TimeoutException:
            return None


class SendSmsTemplatePage(BasePage):

    new_sms_template_link = TemplatePageLocators.ADD_NEW_TEMPLATE_LINK
    edit_sms_template_link = TemplatePageLocators.EDIT_TEMPLATE_LINK

    def click_add_new_template(self):
        element = self.wait_for_element(SendSmsTemplatePage.new_sms_template_link)
        element.click()

    def click_edit_template(self):
        element = self.wait_for_element(SendSmsTemplatePage.edit_sms_template_link)
        element.click()

    def click_upload_recipients(self):
        element = self.wait_for_element(TemplatePageLocators.UPLOAD_RECIPIENTS_LINK)
        element.click()


class EditSmsTemplatePage(BasePage):

    name_input = NameInputElement()
    template_content_input = TemplateContentElement()
    save_button = EditTemplatePageLocators.SAVE_BUTTON

    def click_save(self):
        element = self.wait_for_element(EditSmsTemplatePage.save_button)
        element.click()

    def create_template(self, name='Test sms template', content=None):
        self.name_input = name
        if content:
            self.template_content_input = content
        else:
            self.template_content_input = 'The quick brown fox jumped over the lazy dog. Jenkins job id: ((build_id))'
        self.click_save()


class SendEmailTemplatePage(BasePage):

    add_a_new_email_template_link = TemplatePageLocators.ADD_A_NEW_TEMPLATE_LINK
    add_new_email_template_link = TemplatePageLocators.ADD_NEW_TEMPLATE_LINK
    edit_email_template_link = TemplatePageLocators.EDIT_TEMPLATE_LINK

    def click_add_a_new_template(self):
        element = self.wait_for_element(SendEmailTemplatePage.add_a_new_email_template_link)
        element.click()

    def click_add_new_template(self):
        element = self.wait_for_element(SendEmailTemplatePage.add_new_email_template_link)
        element.click()

    def click_edit_template(self):
        element = self.wait_for_element(SendEmailTemplatePage.edit_email_template_link)
        element.click()

    def click_upload_recipients(self):
        element = self.wait_for_element(TemplatePageLocators.UPLOAD_RECIPIENTS_LINK)
        element.click()


class ViewTemplatePage(BasePage):
    def click_send(self):
        element = self.wait_for_element(ViewTemplatePageLocators.SEND_BUTTON)
        element.click()


class EditEmailTemplatePage(BasePage):

    name_input = NameInputElement()
    subject_input = SubjectInputElement()
    template_content_input = TemplateContentElement()
    save_button = EditTemplatePageLocators.SAVE_BUTTON
    delete_button = EditTemplatePageLocators.DELETE_BUTTON
    confirm_delete_button = EditTemplatePageLocators.CONFIRM_DELETE_BUTTON

    @staticmethod
    def folder_path_item(folder_name):
        return (
            By.XPATH,
            "//a[contains(@class,'folder-heading-folder') and contains(text(), '{}')]".format(folder_name)
        )

    def click_save(self):
        element = self.wait_for_element(EditEmailTemplatePage.save_button)
        element.click()

    def click_delete(self):
        element = self.wait_for_element(EditEmailTemplatePage.delete_button)
        element.click()
        element = self.wait_for_element(EditEmailTemplatePage.confirm_delete_button)
        element.click()

    def create_template(self, name='Test email template', content=None):
        self.name_input = name
        self.subject_input = 'Test email from functional tests'
        if content:
            self.template_content_input = content
        else:
            self.template_content_input = 'The quick brown fox jumped over the lazy dog. Jenkins job id: ((build_id))'
        self.click_save()

    def click_folder_path(self, folder_name):
        element = self.wait_for_element(self.folder_path_item(folder_name))
        element.click()


class UploadCsvPage(BasePage):

    file_input_element = FileInputElement()
    send_button = UploadCsvLocators.SEND_BUTTON
    first_notification = UploadCsvLocators.FIRST_NOTIFICATION_AFTER_UPLOAD

    def click_send(self):
        element = self.wait_for_element(UploadCsvPage.send_button)
        element.click()

    def upload_csv(self, directory, path):
        file_path = os.path.join(directory, path)
        self.file_input_element = file_path
        self.click_send()
        shutil.rmtree(directory, ignore_errors=True)

    # we've been having issues with celery short polling causing notifications to take a long time.
    @retry(RetryException, tries=10, delay=10)
    def get_notification_id_after_upload(self):
        try:
            element = self.wait_for_element(UploadCsvPage.first_notification)
            notification_id = element.get_attribute('id')
            if not notification_id:
                raise RetryException('No notification id yet {}'.format(notification_id))
            else:
                return notification_id
        except StaleElementReferenceException:
            raise RetryException('Could not find element...')

    def go_to_upload_csv_for_service_and_template(self, service_id, template_id):
        url = "{}/services/{}/send/{}/csv".format(self.base_url, service_id, template_id)
        self.driver.get(url)


class TeamMembersPage(BasePage):

    h1 = TeamMembersPageLocators.H1
    invite_team_member_button = TeamMembersPageLocators.INVITE_TEAM_MEMBER_BUTTON
    edit_team_member_link = TeamMembersPageLocators.EDIT_TEAM_MEMBER_LINK

    def get_edit_link_for_member_name(self, email):
        return self.wait_for_element((By.XPATH, "//h3[@title='{}']/..//a".format(email)))

    def h1_is_team_members(self):
        element = self.wait_for_element(TeamMembersPage.h1)
        return element.text == 'Team members'

    def click_invite_user(self):
        element = self.wait_for_element(TeamMembersPage.invite_team_member_button)
        element.click()

    def click_edit_team_member(self, email):
        element = self.get_edit_link_for_member_name(email)
        element.click()


class InviteUserPage(BasePage):

    email_input = EmailInputElement()
    see_dashboard_check_box = InviteUserPageLocators.SEE_DASHBOARD_CHECKBOX
    choose_folders_button = InviteUserPageLocators.CHOOSE_FOLDERS_BUTTON
    send_messages_checkbox = InviteUserPageLocators.SEND_MESSAGES_CHECKBOX
    manage_services_checkbox = InviteUserPageLocators.MANAGE_SERVICES_CHECKBOX
    manage_templates_checkbox = InviteUserPageLocators.MANAGE_TEMPLATES_CHECKBOX
    manage_api_keys_checkbox = InviteUserPageLocators.MANAGE_API_KEYS_CHECKBOX
    choose_folders_button = InviteUserPageLocators.CHOOSE_FOLDERS_BUTTON
    send_invitation_button = InviteUserPageLocators.SEND_INVITATION_BUTTON

    def get_folder_checkbox(self, folder_name):
        label = self.driver.find_elements_by_xpath("//label[contains(text(), '{}')]".format(folder_name))
        return (By.ID, label[0].get_attribute("for"))

    def fill_invitation_form(self, email, send_messages_only):
        self.email_input = email
        if send_messages_only:
            element = self.wait_for_invisible_element(InviteUserPage.send_messages_checkbox)
            self.select_checkbox_or_radio(element)
        else:
            element = self.wait_for_invisible_element(InviteUserPage.see_dashboard_check_box)
            self.select_checkbox_or_radio(element)
            element = self.wait_for_invisible_element(InviteUserPage.send_messages_checkbox)
            self.select_checkbox_or_radio(element)
            element = self.wait_for_invisible_element(InviteUserPage.manage_templates_checkbox)
            self.select_checkbox_or_radio(element)
            element = self.wait_for_invisible_element(InviteUserPage.manage_services_checkbox)
            self.select_checkbox_or_radio(element)
            element = self.wait_for_invisible_element(InviteUserPage.manage_api_keys_checkbox)
            self.select_checkbox_or_radio(element)

    def send_invitation(self):
        element = self.wait_for_element(InviteUserPage.send_invitation_button)
        element.click()

    # support variants of this page with a 'Save' button instead of 'Send invitation' (both use the same locator)
    def click_save(self):
        self.send_invitation()

    def uncheck_folder_permission_checkbox(self, folder_name):
        try:
            choose_folders_button = self.wait_for_invisible_element(InviteUserPage.choose_folders_button)
            choose_folders_button.click()
        except (NoSuchElementException, TimeoutException):
            pass

        checkbox = self.wait_for_invisible_element(self.get_folder_checkbox(folder_name))
        self.unselect_checkbox(checkbox)

    def is_checkbox_checked(self, folder_name):
        try:
            choose_folders_button = self.wait_for_invisible_element(InviteUserPage.choose_folders_button)
            choose_folders_button.click()
        except (NoSuchElementException, TimeoutException):
            pass

        checkbox = self.wait_for_invisible_element(self.get_folder_checkbox(folder_name))
        return checkbox.get_attribute('checked')


class RegisterFromInvite(BasePage):

    name_input = NameInputElement()
    mobile_input = MobileInputElement()
    password_input = PasswordInputElement()
    continue_button = CommonPageLocators.CONTINUE_BUTTON

    def fill_registration_form(self, name):
        self.name_input = name
        self.mobile_input = config['user']['mobile']
        self.password_input = config['user']['password']

    def click_continue(self):
        element = self.wait_for_element(RegisterFromInvite.continue_button)
        element.click()


class ProfilePage(BasePage):

    h1 = CommonPageLocators.H1

    def h1_is_correct(self):
        element = self.wait_for_element(ProfilePage.h1)
        return element.text == 'Your profile'


class ApiIntegrationPage(BasePage):
    message_log = ApiIntegrationPageLocators.MESSAGE_LOG
    client_reference = ApiIntegrationPageLocators.CLIENT_REFERENCE
    message_list = ApiIntegrationPageLocators.MESSAGE_LIST
    view_letter_link = ApiIntegrationPageLocators.VIEW_LETTER_LINK

    def get_notification_id(self):
        element = self.wait_for_elements(ApiIntegrationPage.message_list)[0]
        return element.text

    def click_message_log(self):
        element = self.wait_for_element(ApiIntegrationPage.message_log)
        element.click()

    def get_client_reference(self):
        element = self.wait_for_elements(ApiIntegrationPage.client_reference)[1]
        return element.text

    def go_to_api_integration_for_service(self, service_id):
        url = "{}/services/{}/api".format(self.base_url, service_id)
        self.driver.get(url)

    def get_status_from_message(self):
        element = self.wait_for_elements(ApiIntegrationPage.message_list)[5]
        return element.text

    def get_view_letter_link(self):
        link = self.wait_for_elements(ApiIntegrationPage.view_letter_link)[0]
        return link.get_attribute("href")

    def go_to_preview_letter(self):
        link = self.wait_for_elements(ApiIntegrationPage.view_letter_link)[0]
        self.driver.get(link.get_attribute("href"))


class PreviewLetterPage(BasePage):
    download_pdf_link = LetterPreviewPageLocators.DOWNLOAD_PDF_LINK
    pdf_image = LetterPreviewPageLocators.PDF_IMAGE

    def get_download_pdf_link(self):
        link = self.wait_for_element(PreviewLetterPage.download_pdf_link)
        return link.get_attribute("href")

    def get_image_src(self):
        link = self.wait_for_element(PreviewLetterPage.pdf_image)
        return link.get_attribute("src")


class ApiKeyPage(BasePage):

    key_name_input = KeyNameInputElement()
    keys_link = ApiKeysPageLocators.KEYS_PAGE_LINK
    create_key_link = ApiKeysPageLocators.CREATE_KEY_LINK
    continue_button = CommonPageLocators.CONTINUE_BUTTON
    api_key_element = ApiKeysPageLocators.API_KEY_ELEMENT
    key_types = {
        'normal': ApiKeysPageLocators.NORMAL_KEY_RADIO,
        'test': ApiKeysPageLocators.TEST_KEY_RADIO,
        'team': ApiKeysPageLocators.TEAM_KEY_RADIO,
    }

    def enter_key_name(self, key_type='normal'):
        self.key_name_input = 'Test ' + key_type

    def click_keys_link(self):
        element = self.wait_for_element(ApiKeyPage.keys_link)
        element.click()

    def click_create_key(self):
        element = self.wait_for_element(ApiKeyPage.create_key_link)
        element.click()

    def click_continue(self):
        element = self.wait_for_element(ApiKeyPage.continue_button)
        element.click()

    def get_api_key(self):
        element = self.wait_for_element(ApiKeyPage.api_key_element)
        return element.text

    def click_key_type_radio(self, key_type='normal'):
        element = self.wait_for_invisible_element(ApiKeyPage.key_types[key_type])
        self.select_checkbox_or_radio(element)


class SendOneRecipient(BasePage):

    def go_to_send_one_recipient(self, service_id, template_id):
        url = "{}/services/{}/send/{}/set-sender".format(self.base_url, service_id, template_id)
        self.driver.get(url)

    def is_placeholder_a_recipient_field(self, message_type):
        element = self.wait_for_element(SingleRecipientLocators.PLACEHOLDER_NAME)
        if message_type == "email":
            return element.text.strip() == 'email address'
        else:
            return element.text.strip() == 'phone number'

    def get_placeholder_name(self):
        element = self.wait_for_element(SingleRecipientLocators.PLACEHOLDER_NAME)
        return element.text.strip()

    def enter_placeholder_value(self, placeholder_value):
        element = self.wait_for_element(SingleRecipientLocators.PLACEHOLDER_VALUE_INPUT)
        element.send_keys(placeholder_value)

    def get_preview_contents(self):
        table = self.wait_for_element(SingleRecipientLocators.PREVIEW_TABLE)
        rows = table.find_elements(By.TAG_NAME, "tr")  # get all of the rows in the table
        return rows

    def choose_alternative_sender(self):
        radio = self.wait_for_invisible_element(SingleRecipientLocators.ALTERNATIVE_SENDER_RADIO)
        radio.click()

    def send_to_myself(self, message_type):
        if message_type == "email":
            element = self.wait_for_element(SingleRecipientLocators.USE_MY_EMAIL)
        else:
            element = self.wait_for_element(SingleRecipientLocators.USE_MY_NUMBER)
        element.click()


class ServiceSettingsPage(BasePage):
    def check_service_name(self, expected_name):
        name = self.wait_for_element(ServiceSettingsLocators.SERVICE_NAME)
        if name.element.text == expected_name:
            return True
        else:
            raise ValueError("Service name not changed succesfully")


class ChangeName(BasePage):
    def go_to_change_service_name(self, service_id):
        url = "{}/services/{}/service-settings/name".format(self.base_url, service_id)
        self.driver.get(url)

    def enter_new_name(self, new_name):
        element = self.wait_for_element(ChangeNameLocators.CHANGE_NAME_FIELD)
        element.clear()
        element.send_keys(new_name)

    def enter_password(self, password):
        element = self.wait_for_element(ChangeNameLocators.PASSWORD_FIELD)
        element.send_keys(password)


class EmailReplyTo(BasePage):

    def go_to_add_email_reply_to_address(self, service_id):
        url = "{}/services/{}/service-settings/email-reply-to/add".format(self.base_url, service_id)
        self.driver.get(url)

    def click_add_email_reply_to(self):
        element = self.wait_for_element(EmailReplyToLocators.ADD_EMAIL_REPLY_TO_BUTTON)
        element.click()

    def click_continue_button(self, time=120):
        element = self.wait_for_element(EmailReplyToLocators.CONTINUE_BUTTON, time=time)
        element.click()

    def insert_email_reply_to_address(self, email_address):
        element = self.wait_for_element(EmailReplyToLocators.EMAIL_ADDRESS_FIELD)
        element.send_keys(email_address)

    def get_reply_to_email_addresses(self):
        elements = self.wait_for_element(EmailReplyToLocators.REPLY_TO_ADDRESSES)
        return elements

    def go_to_edit_email_reply_to_address(self, service_id, email_reply_to_id):
        url = "{}/services/{}/service-settings/email-reply-to/{}/edit".format(
            self.base_url,
            service_id,
            email_reply_to_id
        )
        self.driver.get(url)

    def check_is_default_check_box(self):
        radio = self.wait_for_invisible_element(EmailReplyToLocators.IS_DEFAULT_CHECKBOX)
        radio.click()

    def clear_email_reply_to(self):
        element = self.wait_for_element(EmailReplyToLocators.EMAIL_ADDRESS_FIELD)
        element.clear()


class SmsSenderPage(BasePage):
    def go_to_text_message_senders(self, service_id):
        url = "{}/services/{}/service-settings/sms-sender".format(self.base_url, service_id)
        self.driver.get(url)

    def go_to_add_text_message_sender(self, service_id):
        url = "{}/services/{}/service-settings/sms-sender/add".format(self.base_url, service_id)
        self.driver.get(url)

    def insert_sms_sender(self, sender):
        element = self.wait_for_element(SmsSenderLocators.SMS_SENDER_FIELD)
        element.clear()
        element.send_keys(sender)

    def click_save_sms_sender(self):
        element = self.wait_for_element(SmsSenderLocators.SAVE_SMS_SENDER_BUTTON)
        element.click()

    def get_sms_senders(self):
        elements = self.wait_for_element(SmsSenderLocators.ALL_SMS_SENDERS)
        return elements

    def click_change_link_for_first_sms_sender(self):
        change_link = self.wait_for_element(SmsSenderLocators.FIRST_CHANGE_LINK)
        change_link.click()

    def get_sms_sender(self):
        return self.wait_for_element(SmsSenderLocators.SMS_SENDER)

    def get_sms_recipient(self):
        return self.wait_for_element(SmsSenderLocators.SMS_RECIPIENT)

    def get_sms_content(self):
        return self.wait_for_element(SmsSenderLocators.SMS_CONTENT)


class OrganisationDashboardPage(BasePage):

    h1 = (By.CSS_SELECTOR, 'h1')
    team_members_link = (By.LINK_TEXT, 'Team members')
    service_list = (By.CSS_SELECTOR, 'main .browse-list-item')

    def is_current(self, org_id):
        expected = "{}/organisations/{}".format(self.base_url, org_id)
        return self.driver.current_url == expected

    def click_team_members_link(self):
        element = self.wait_for_element(DashboardPage.team_members_link)
        element.click()

    def go_to_dashboard_for_org(self, org_id):
        url = "{}/organisations/{}".format(self.base_url, org_id)
        self.driver.get(url)


class InviteUserToOrgPage(BasePage):
    email_input = EmailInputElement()
    send_invitation_button = InviteUserPageLocators.SEND_INVITATION_BUTTON

    def fill_invitation_form(self, email):
        self.email_input = email

    def send_invitation(self):
        element = self.wait_for_element(self.send_invitation_button)
        element.click()


class InboxPage(BasePage):

    def is_current(self, service_id):
        expected = "{}/services/{}/inbox".format(self.base_url, service_id)
        return self.driver.current_url == expected

    def go_to_conversation(self, user_number):
        # link looks like "07123 456789". because i don't know if user_number starts with +44, just get the last 10
        # digits. (so this'll look for partial link text of "123 456789")
        formatted_phone_number = '{} {}'.format(user_number[-10:-6], user_number[-6:])
        element = self.wait_for_element((By.PARTIAL_LINK_TEXT, formatted_phone_number))
        element.click()


class ConversationPage(BasePage):
    sms_message = (By.CSS_SELECTOR, '.sms-message-wrapper')

    def get_message(self, content):
        elements = self.wait_for_elements(self.sms_message)
        return next((el for el in elements if content in el.text), None)


class DocumentDownloadLandingPage(BasePage):
    continue_button = (By.CSS_SELECTOR, 'a.govuk-button')

    def get_service_name(self):
        element = self.wait_for_element((By.CSS_SELECTOR, 'main p:first-of-type'))

        return element.text.partition(' sent you ')[0]

    def go_to_download_page(self):
        button = self.wait_for_element(self.continue_button)

        button.click()


class DocumentDownloadPage(BasePage):
    download_link = (By.LINK_TEXT, "Download this file to your device")

    def get_download_link(self):
        link = self.wait_for_element(self.download_link)

        return link.element.get_attribute('href')


class ViewFolderPage(ShowTemplatesPage):
    manage_link = (By.LINK_TEXT, 'Manage')
    template_path_and_name = (By.TAG_NAME, 'h1')

    def click_manage_folder(self):
        link = self.wait_for_element(self.manage_link)
        link.click()

    def assert_name_equals(self, expected_name):
        h1 = self.wait_for_element(self.template_path_and_name)
        assert expected_name in h1.text


class ManageFolderPage(BasePage):
    delete_link = (By.LINK_TEXT, 'Delete this folder')
    name_input = NameInputElement()
    delete_button = (By.NAME, 'delete')
    save_button = (By.CSS_SELECTOR, 'main [type=submit]')
    error_message = (By.CSS_SELECTOR, '.banner-dangerous')

    def set_name(self, new_name):
        self.name_input = new_name
        button = self.wait_for_element(self.save_button)
        button.click()

    def delete_folder(self):
        link = self.wait_for_element(self.delete_link)
        link.click()

    def confirm_delete_folder(self):
        link = self.wait_for_element(self.delete_button)
        link.click()

    def get_errors(self):
        errors = self.wait_for_element(self.error_message)
        return errors.text.strip()
