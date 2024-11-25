from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from tests.pages.locators import (
    AddServicePageLocators,
    CommonPageLocators,
    EditTemplatePageLocators,
    NewPasswordPageLocators,
    ServiceJoinRequestChooseServicePageLocators,
    ServiceJoinRequestJoinAskPageLocators,
    SignUpPageLocators,
    UploadCsvLocators,
    VerifyPageLocators,
)


class BasePageElement:
    def __init__(self, name=None, clear=False):
        if name:
            self.name = name
        self.clear = clear

    def __set__(self, obj, value):
        driver = obj.driver
        WebDriverWait(driver, 100).until(lambda driver: driver.find_element(By.NAME, self.name))

        element = driver.find_element(By.NAME, self.name)

        if self.clear:
            element.clear()

        element.send_keys(value)

    def __get__(self, obj, owner):
        driver = obj.driver
        WebDriverWait(driver, 100).until(lambda driver: driver.find_element(By.NAME, self.name))
        element = driver.find_element(By.NAME, self.name)
        return element.get_attribute("value")


class ServiceInputElement(BasePageElement):
    name = AddServicePageLocators.SERVICE_INPUT[1]


class ServiceOrgTypeElement(BasePageElement):
    name = AddServicePageLocators.ORG_TYPE_INPUT[1]


class EmailInputElement(BasePageElement):
    name = CommonPageLocators.EMAIL_INPUT[1]


class NewPasswordInputElement(BasePageElement):
    name = NewPasswordPageLocators.NEW_PASSWORD_INPUT[1]


class PasswordInputElement(BasePageElement):
    name = CommonPageLocators.PASSWORD_INPUT[1]


class SmsInputElement(BasePageElement):
    name = VerifyPageLocators.SMS_INPUT[1]


class NameInputElement(BasePageElement):
    name = CommonPageLocators.NAME_INPUT[1]


class MobileInputElement(BasePageElement):
    name = SignUpPageLocators.MOBILE_INPUT[1]


class TemplateContentElement(BasePageElement):
    name = EditTemplatePageLocators.TEMPLATE_CONTENT_INPUT[1]


class FileInputElement(BasePageElement):
    name = UploadCsvLocators.FILE_INPUT[1]


class SubjectInputElement(BasePageElement):
    name = EditTemplatePageLocators.TEMPLATE_SUBJECT_INPUT[1]


class ServiceJoinRequestChooseServiceInputElement(BasePageElement):
    name = ServiceJoinRequestChooseServicePageLocators.SEARCH_SERVICE_INPUT[1]


class ServiceJoinRequestJoinAskReasonTextAreaElement(BasePageElement):
    name = ServiceJoinRequestJoinAskPageLocators.REQUEST_REASON_TEXTAREA[1]
