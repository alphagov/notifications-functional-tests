import uuid
import pytest

from selenium import webdriver

from config import Config

from tests.utils import (
    generate_unique_email
)

uuid_for_test_run = str(uuid.uuid1())

functional_test_name = Config.FUNCTIONAL_TEST_NAME + uuid_for_test_run
functional_test_email = generate_unique_email(Config.FUNCTIONAL_TEST_EMAIL, uuid_for_test_run)
functional_test_service_name = Config.FUNCTIONAL_TEST_SERVICE_NAME + uuid_for_test_run
functional_test_password = Config.FUNCTIONAL_TEST_PASSWORD
functional_test_mobile = Config.TWILIO_TEST_NUMBER


@pytest.fixture(scope="session")
def test_profile():
    return {'name': functional_test_name,
            'email': functional_test_email,
            'service_name': functional_test_service_name,
            'password': functional_test_password,
            'mobile': functional_test_mobile}


@pytest.fixture(scope="module")
def driver(request):
    driver = webdriver.Firefox()

    def clear_up():
        driver.delete_all_cookies()
        driver.close()

    request.addfinalizer(clear_up)
    return driver


@pytest.fixture(scope="session")
def base_url():
    return Config.NOTIFY_ADMIN_URL
