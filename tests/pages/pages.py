import os
import shutil

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from config import Config

from tests.pages.element import (
    EmailInputElement,
    PasswordInputElement,
    SmsInputElement,
    NameInputElement,
    MobileInputElement,
    ServiceInputElement,
    TemplateContentElement,
    FileInputElement,
    SubjectInputElement
)


from tests.pages.locators import (
    CommonPageLocators,
    MainPageLocators,
    AddServicePageLocators,
    DashboardPageLocators,
    NavigationLocators,
    TemplatePageLocators,
    EditTemplatePageLocators,
    UploadCsvLocators
)


class BasePage(object):

    base_url = Config.NOTIFY_ADMIN_URL
    sign_out_link = NavigationLocators.SIGN_OUT_LINK

    def __init__(self, driver):
        self.driver = driver

    def wait_for_element(self, locator):
        return WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(locator)
        )

    def sign_out(self):
        element = self.wait_for_element(BasePage.sign_out_link)
        element.click()


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
        return self.driver.current_url == self.base_url + '/register'

    def register(self, name, email, mobile_number, password):
        self.name_input = name
        self.email_input = email
        self.mobile_input = mobile_number
        self.password_input = password
        self.click_continue_button()

    def click_continue_button(self):
        element = self.wait_for_element(RegistrationPage.continue_button)
        element.click()


class AddServicePage(BasePage):

    service_input = ServiceInputElement()
    add_service_button = AddServicePageLocators.ADD_SERVICE_BUTTON

    def is_current(self):
        return self.driver.current_url == self.base_url + '/add-service?first=first'

    def add_service(self, name):
        self.service_input = name
        self.click_add_service_button()

    def click_add_service_button(self):
        element = self.wait_for_element(AddServicePage.add_service_button)
        element.click()


class TourPage(BasePage):

    def is_current(self):
        return self.driver.current_url.endswith('/tour/1')

    def get_me_out_of_here(self):
        while True:
            try:
                element = self.driver.find_element(By.LINK_TEXT, 'Next')
                element.click()
            except:
                break


class SignInPage(BasePage):

    email_input = EmailInputElement()
    password_input = PasswordInputElement()
    continue_button = CommonPageLocators.CONTINUE_BUTTON

    def get(self):
        self.driver.get(self.base_url+'/sign-in')

    def is_current(self):
        return self.driver.current_url == self.base_url+'/sign-in'

    def is_currect(self):
        return self.driver.current_url == self.base_url+'/sign-in'

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

    def is_current(self):
        return self.driver.current_url == self.base_url+'/verify'

    def click_continue_button(self):
        element = self.wait_for_element(VerifyPage.continue_button)
        element.click()

    def verify(self, code):
        self.sms_input = code
        self.click_continue_button()


class TwoFactorPage(BasePage):

    sms_input = SmsInputElement()
    continue_button = CommonPageLocators.CONTINUE_BUTTON

    def is_current(self):
        return self.driver.current_url == self.base_url+'/two-factor'

    def click_continue_button(self):
        element = self.wait_for_element(TwoFactorPage.continue_button)
        element.click()

    def verify(self, code):
        self.sms_input = code
        self.click_continue_button()


class DashboardPage(BasePage):

    h2 = DashboardPageLocators.H2
    sms_templates_link = DashboardPageLocators.SMS_TEMPLATES_LINK
    email_templates_link = DashboardPageLocators.EMAIL_TEMPLATES_LINK

    def is_current(self):
        return self.driver.current_url.endswith('/dashboard')

    def h2_is_service_name(self, expected_name):
        element = self.wait_for_element(DashboardPage.h2)
        return expected_name == element.text

    def click_sms_templates(self):
        element = self.wait_for_element(DashboardPage.sms_templates_link)
        element.click()

    def click_email_templates(self):
        element = self.wait_for_element(DashboardPage.email_templates_link)
        element.click()


class SendSmsTemplatePage(BasePage):

    new_sms_template_link = TemplatePageLocators.NEW_TEMPLATE_LINK
    send_from_csv_link = TemplatePageLocators.SEND_FROM_CSV_LINK

    def click_add_new_template(self):
        element = self.wait_for_element(SendSmsTemplatePage.new_sms_template_link)
        element.click()

    def click_send_from_csv_link(self):
        element = self.wait_for_element(SendSmsTemplatePage.send_from_csv_link)
        element.click()


class EditSmsTemplatePage(BasePage):

    name_input = NameInputElement()
    template_content_input = TemplateContentElement()
    save_button = EditTemplatePageLocators.SAVE_BUTTON

    def click_save(self):
        element = self.wait_for_element(EditSmsTemplatePage.save_button)
        element.click()

    def create_template(self):
        self.name_input = 'Test'
        self.template_content_input = 'The quick brown fox jumped over the lazy dog'
        self.click_save()


class SendEmailTemplatePage(BasePage):

    new_email_template_link = TemplatePageLocators.NEW_TEMPLATE_LINK
    send_from_csv_link = TemplatePageLocators.SEND_FROM_CSV_LINK

    def click_add_new_template(self):
        element = self.wait_for_element(SendEmailTemplatePage.new_email_template_link)
        element.click()

    def click_send_from_csv_link(self):
        element = self.wait_for_element(SendEmailTemplatePage.send_from_csv_link)
        element.click()


class EditEmailTemplatePage(BasePage):

    name_input = NameInputElement()
    subject_input = SubjectInputElement()
    template_content_input = TemplateContentElement()
    save_button = EditTemplatePageLocators.SAVE_BUTTON

    def click_save(self):
        element = self.wait_for_element(EditEmailTemplatePage.save_button)
        element.click()

    def create_template(self):
        # TODO remove the uuid mularkey once uniqueness of email subject no longer a thing
        import uuid
        self.name_input = 'Test email template'
        self.subject_input = 'Test email from functional tests ' + str(uuid.uuid1())
        self.template_content_input = 'The quick brown fox jumped over the lazy dog'
        self.click_save()


class UploadCsvPage(BasePage):

    file_input_element = FileInputElement()
    click_send_button = UploadCsvLocators.SEND_BUTTON

    def click_send(self):
        element = self.wait_for_element(UploadCsvPage.click_send_button)
        element.click()

    def upload_csv(self, directory, path):
        file_path = os.path.join(directory, 'sample.csv')
        self.file_input_element = file_path
        self.click_send()
        shutil.rmtree(directory, ignore_errors=True)
