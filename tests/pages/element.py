from selenium.webdriver.support.ui import WebDriverWait

from tests.pages.locators import (
    CommonPageLocators,
    VerifyPageLocators,
    SignUpPageLocators,
    AddServicePageLocators,
    EditTemplatePageLocators,
    UploadCsvLocators,
    ApiKeysPageLocators
)


class BasePageElement(object):

    def __set__(self, obj, value):
        driver = obj.driver
        WebDriverWait(driver, 100).until(
            lambda driver: driver.find_element_by_name(self.locator))
        driver.find_element_by_name(self.locator).send_keys(value)

    def __get__(self, obj, owner):
        driver = obj.driver
        WebDriverWait(driver, 100).until(
            lambda driver: driver.find_element_by_name(self.locator))
        element = driver.find_element_by_name(self.locator)
        return element.get_attribute("value")


class ServiceInputElement(BasePageElement):
    locator = AddServicePageLocators.SERVICE_INPUT[1]


class EmailInputElement(BasePageElement):
    locator = CommonPageLocators.EMAIL_INPUT[1]


class PasswordInputElement(BasePageElement):
    locator = CommonPageLocators.PASSWORD_INPUT[1]


class SmsInputElement(BasePageElement):
    locator = VerifyPageLocators.SMS_INPUT[1]


class NameInputElement(BasePageElement):
    locator = CommonPageLocators.NAME_INPUT[1]


class MobileInputElement(BasePageElement):
    locator = SignUpPageLocators.MOBILE_INPUT[1]


class TemplateContentElement(BasePageElement):
    locator = EditTemplatePageLocators.TEMPLATE_CONTENT_INPUT[1]


class FileInputElement(BasePageElement):
    locator = UploadCsvLocators.FILE_INPUT[1]


class SubjectInputElement(BasePageElement):
    locator = EditTemplatePageLocators.TEMPLATE_SUBJECT_INPUT[1]


class KeyNameInputElement(BasePageElement):
    locator = ApiKeysPageLocators.KEY_NAME_INPUT[1]
