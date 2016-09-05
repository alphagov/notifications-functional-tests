import os
import uuid
import pytest

from selenium import webdriver

from tests.utils import (
    generate_unique_email
)

from tests.pages.rollups import sign_in

from config import Config


class Profile(object):

    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            setattr(self, key, val)

    def __repr__(self):
        return '{} - {}'.format(self.env, self.email)


@pytest.fixture(scope="session")
def profile():
    env = os.environ['ENVIRONMENT'].lower()
    if env == 'staging':
        from config import StagingConfig
        return Profile(**{'env': StagingConfig.ENVIRONMENT,
                          'name': StagingConfig.FUNCTIONAL_TEST_NAME,
                          'email': StagingConfig.FUNCTIONAL_TEST_EMAIL,
                          'service_name': StagingConfig.FUNCTIONAL_TEST_SERVICE_NAME,
                          'password': StagingConfig.FUNCTIONAL_TEST_PASSWORD,
                          'email_password': StagingConfig.FUNCTIONAL_TEST_EMAIL_PASSWORD,
                          'mobile': StagingConfig.TEST_NUMBER,
                          'service_id': StagingConfig.SERVICE_ID,
                          'email_template_id': StagingConfig.EMAIL_TEMPLATE_ID,
                          'sms_template_id': StagingConfig.SMS_TEMPLATE_ID,
                          'email_notification_label': StagingConfig.EMAIL_NOTIFICATION_LABEL,
                          'registration_email_label': StagingConfig.REGISTRATION_EMAIL_LABEL,
                          'invitation_email_label': StagingConfig.INVITATION_EMAIL_LABEL,
                          'api_key': StagingConfig.SERVICE_API_KEY,
                          'notify_api_url': StagingConfig.NOTIFY_API_URL,
                          'registration_template_id': StagingConfig.REGISTRATION_TEMPLATE_ID,
                          'invitation_template_id': StagingConfig.INVITATION_TEMPLATE_ID})
    elif env == 'live':
        from config import LiveConfig
        return Profile(**{'env': LiveConfig.ENVIRONMENT,
                          'name': LiveConfig.FUNCTIONAL_TEST_NAME,
                          'email': LiveConfig.FUNCTIONAL_TEST_EMAIL,
                          'service_name': LiveConfig.FUNCTIONAL_TEST_SERVICE_NAME,
                          'password': LiveConfig.FUNCTIONAL_TEST_PASSWORD,
                          'email_password': LiveConfig.FUNCTIONAL_TEST_EMAIL_PASSWORD,
                          'mobile': LiveConfig.TEST_NUMBER,
                          'service_id': LiveConfig.SERVICE_ID,
                          'email_template_id': LiveConfig.EMAIL_TEMPLATE_ID,
                          'sms_template_id': LiveConfig.SMS_TEMPLATE_ID,
                          'email_notification_label': LiveConfig.EMAIL_NOTIFICATION_LABEL,
                          'registration_email_label': LiveConfig.REGISTRATION_EMAIL_LABEL,
                          'invitation_email_label': LiveConfig.INVITATION_EMAIL_LABEL,
                          'api_key': LiveConfig.SERVICE_API_KEY,
                          'notify_api_url': LiveConfig.NOTIFY_API_URL,
                          'registration_template_id': StagingConfig.REGISTRATION_TEMPLATE_ID,
                          'invitation_template_id': StagingConfig.INVITATION_TEMPLATE_ID})
    else:
        from config import Config
        uuid_for_test_run = str(uuid.uuid1())
        functional_test_name = Config.FUNCTIONAL_TEST_NAME + uuid_for_test_run
        functional_test_email = generate_unique_email(Config.FUNCTIONAL_TEST_EMAIL, uuid_for_test_run)
        functional_test_service_name = Config.FUNCTIONAL_TEST_SERVICE_NAME + uuid_for_test_run
        functional_test_password = Config.FUNCTIONAL_TEST_PASSWORD
        functional_test_email_password = Config.FUNCTIONAL_TEST_EMAIL_PASSWORD
        functional_test_mobile = Config.TEST_NUMBER
        return Profile(**{'env': Config.ENVIRONMENT,
                          'name': functional_test_name,
                          'email': functional_test_email,
                          'service_name': functional_test_service_name,
                          'password': functional_test_password,
                          'email_password': functional_test_email_password,
                          'mobile': functional_test_mobile,
                          'email_notification_label': Config.EMAIL_NOTIFICATION_LABEL,
                          'registration_email_label': Config.REGISTRATION_EMAIL_LABEL,
                          'invitation_email_label': Config.INVITATION_EMAIL_LABEL,
                          'notify_service_id': Config.NOTIFY_SERVICE_ID,
                          'notify_service_api_key': Config.NOTIFY_SERVICE_API_KEY,
                          'registration_template_id': Config.REGISTRATION_TEMPLATE_ID,
                          'invitation_template_id': Config.INVITATION_TEMPLATE_ID})


@pytest.fixture(scope="module")
def driver(request):
    driver_name = os.getenv('SELENIUM_DRIVER', 'chrome').lower()
    if os.environ.get('TRAVIS'):
        driver_name = 'firefox'

    if driver_name == 'firefox':
        driver = webdriver.Firefox()
    elif driver_name == 'chrome':
        driver = webdriver.Chrome()
    else:
        raise ValueError('Invalid Selenium driver', driver_name)

    driver.delete_all_cookies()

    def clear_up():
        driver.delete_all_cookies()
        driver.close()

    request.addfinalizer(clear_up)
    return driver


@pytest.fixture(scope="session")
def base_url():
    return Config.NOTIFY_ADMIN_URL


@pytest.fixture(scope="module")
def login_user(driver, profile):
    sign_in(driver, profile)
