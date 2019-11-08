import os
import pytest
from datetime import datetime
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary

from notifications_python_client import NotificationsAPIClient

from tests.pages.rollups import sign_in
from config import config, setup_shared_config


@pytest.fixture(scope="session", autouse=True)
def shared_config():
    """
    Setup shared config variables (eg env and urls)
    """
    setup_shared_config()


@pytest.fixture(scope="module")
def _driver():
    driver_name = (os.getenv('SELENIUM_DRIVER') or 'chrome').lower()
    if os.environ.get('TRAVIS'):
        driver_name = 'firefox'

    http_proxy = os.getenv('HTTP_PROXY')

    if driver_name == 'firefox':
        profile = webdriver.FirefoxProfile()
        profile.set_preference("general.useragent.override", "Selenium")

        if http_proxy is not None and http_proxy != "":
            http_proxy_url = http_proxy.split(':')[0] + ':' + http_proxy.split(':')[1]
            http_proxy_port = int(http_proxy.split(':')[2])
            profile.set_preference("network.proxy.type", 5)
            profile.set_preference("network.proxy.http", http_proxy_url)
            profile.set_preference("network.proxy.http_port", http_proxy_port)
            profile.set_preference("network.proxy.https", http_proxy_url)
            profile.set_preference("network.proxy.https_port", http_proxy_port)
            profile.set_preference("network.proxy.ssl", http_proxy_url)
            profile.set_preference("network.proxy.ssl_port", http_proxy_port)
            profile.update_preferences()

        binary = FirefoxBinary(log_file=open("./logs/browser.log", "wb"))
        driver = webdriver.Firefox(profile, firefox_binary=binary)
        driver.set_window_position(0, 0)
        driver.set_window_size(1280, 720)

    elif driver_name == 'chrome':
        options = webdriver.chrome.options.Options()
        service_args = ['--verbose']
        options.add_argument("--no-sandbox")
        options.add_argument("--headless")
        options.add_argument("user-agent=Selenium")

        if http_proxy is not None and http_proxy != "":
            options.add_argument('--proxy-server={}'.format(http_proxy))

        driver = webdriver.Chrome(service_log_path='./logs/chrome_browser.log',
                                  service_args=service_args,
                                  options=options)
        driver.set_window_size(1280, 720)

    elif driver_name == 'phantomjs':

        service_args = None

        if http_proxy is not None and http_proxy != "":
            service_args = [
                '--proxy={}'.format(http_proxy)
            ]

        driver = webdriver.PhantomJS(service_args=service_args,
                                     service_log_path='./logs/phantomjs.log')
        driver.maximize_window()

    else:
        raise ValueError('Invalid Selenium driver', driver_name)

    driver.delete_all_cookies()
    yield driver
    driver.delete_all_cookies()
    driver.close()


@pytest.fixture(scope='function')
def driver(_driver, request):
    prev_failed_tests = request.session.testsfailed
    yield _driver
    if prev_failed_tests != request.session.testsfailed:
        print('URL at time of failure:', _driver.current_url)
        filename = str(Path.cwd() / 'screenshots' / '{}_{}.png'.format(datetime.utcnow(), request.function.__name__))
        _driver.save_screenshot(str(filename))
        print('Error screenshot saved to ' + filename)


@pytest.fixture(scope="module")
def login_user(_driver):
    sign_in(_driver)


@pytest.fixture(scope="module")
def login_seeded_user(_driver):
    sign_in(_driver, True)


@pytest.fixture(scope="module")
def client():
    client = NotificationsAPIClient(
        base_url=config['notify_api_url'],
        api_key=config['service']['api_key']
    )
    return client


@pytest.fixture(scope="module")
def seeded_client():
    client = NotificationsAPIClient(
        base_url=config['notify_api_url'],
        api_key=config['service']['api_live_key']
    )
    return client


@pytest.fixture(scope="module")
def seeded_client_using_test_key():
    client = NotificationsAPIClient(
        base_url=config['notify_api_url'],
        api_key=config['service']['api_test_key']
    )
    return client
