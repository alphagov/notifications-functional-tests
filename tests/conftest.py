import os
from datetime import datetime
from pathlib import Path

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from seleniumwire import webdriver as selenium_wire_webdriver

from broadcast_client.broadcast_client import BroadcastClient
from config import config, setup_shared_config
from tests.client import FunctionalTestsAPIClient
from tests.pages.pages import HomePage
from tests.pages.rollups import sign_in, sign_in_email_auth


def pytest_addoption(parser):
    parser.addoption("--no-headless", action="store_true", default=False)


@pytest.fixture(scope="session", autouse=True)
def shared_config():
    """
    Setup shared config variables (eg env and urls)
    """
    setup_shared_config()


@pytest.fixture(scope="session")
def download_directory(tmp_path_factory):
    return tmp_path_factory.mktemp("downloads")


@pytest.fixture(scope="module")
def _driver(request, download_directory):
    options = webdriver.chrome.options.Options()
    options.add_argument("--no-sandbox")
    options.add_argument("user-agent=Selenium")
    options.add_experimental_option(
        "prefs",
        {
            "download.default_directory": str(download_directory),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": False,
        },
    )

    if not request.config.getoption("--no-headless"):
        options.add_argument("--headless")

    service = ChromeService(log_path="./logs/chrome_browser.log", service_args=["--verbose"])

    driver = selenium_wire_webdriver.Chrome(service=service, options=options)
    driver.set_window_size(1280, 720)

    def interceptor(request):
        request.headers["x-notify-ecs-origin"] = "true"

    if os.getenv("NOTIFY_ECS_ORIGIN"):
        driver.request_interceptor = interceptor

    driver.delete_all_cookies()

    # go to root page and accept analytics cookies to hide banner in all pages
    driver.get(config["notify_admin_url"])
    HomePage(driver).accept_cookie_warning()
    yield driver
    driver.delete_all_cookies()
    driver.close()


@pytest.fixture(scope="function")
def driver(_driver, request):
    prev_failed_tests = request.session.testsfailed
    yield _driver
    if prev_failed_tests != request.session.testsfailed:
        print("URL at time of failure:", _driver.current_url)
        filename_datetime = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        filename = str(Path.cwd() / "screenshots" / "{}_{}.png".format(filename_datetime, request.function.__name__))
        _driver.save_screenshot(str(filename))
        print("Error screenshot saved to " + filename)


@pytest.fixture(scope="module")
def login_user(_driver):
    sign_in_email_auth(_driver)


@pytest.fixture(scope="module")
def login_seeded_user(_driver):
    sign_in(_driver, account_type="seeded")


@pytest.fixture(scope="module")
def client_live_key():
    client = FunctionalTestsAPIClient(base_url=config["notify_api_url"], api_key=config["service"]["api_live_key"])
    return client


@pytest.fixture(scope="module")
def client_test_key():
    client = FunctionalTestsAPIClient(base_url=config["notify_api_url"], api_key=config["service"]["api_test_key"])
    return client


@pytest.fixture(scope="module")
def broadcast_client():
    client = BroadcastClient(
        api_key=config["broadcast_service"]["api_key_live"],
        base_url=config["notify_api_url"],
    )
    return client
