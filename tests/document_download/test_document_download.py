import re
from io import BytesIO

import pytest
import requests
from notifications_python_client import prepare_upload
from selenium.webdriver.common.by import By

from config import config
from tests.pages import (
    DocumentDownloadConfirmEmailPage,
    DocumentDownloadLandingPage,
    DocumentDownloadPage,
)


def _get_test_doc_dl_url(seeded_client, prepare_upload_kwargs):
    file = prepare_upload(
        BytesIO("foo-bar-baz".encode("utf-8")), **prepare_upload_kwargs
    )
    personalisation = {"build_id": file}
    email_address = config["service"]["seeded_user"]["email"]
    template_id = config["service"]["templates"]["email"]

    resp_json = seeded_client.send_email_notification(
        email_address, template_id, personalisation
    )

    download_link = re.search(r"(https?://\S+)", resp_json["content"]["body"])

    assert download_link

    return download_link.group(0)


@pytest.mark.antivirus
def test_document_upload_and_download(driver, seeded_client):
    download_link = _get_test_doc_dl_url(
        seeded_client,
        {"confirm_email_before_download": False},
    )

    driver.get(download_link)

    landing_page = DocumentDownloadLandingPage(driver)
    assert "Functional Tests" in landing_page.get_service_name()

    landing_page.go_to_download_page()

    download_page = DocumentDownloadPage(driver)
    document_url = download_page.get_download_link()

    downloaded_document = requests.get(document_url)

    assert downloaded_document.text == "foo-bar-baz"


def test_document_download_with_email_confirmation(driver, seeded_client):
    download_link = _get_test_doc_dl_url(
        seeded_client,
        {"confirm_email_before_download": True},
    )

    driver.get(download_link)
    landing_page = DocumentDownloadLandingPage(driver)
    assert "Functional Tests" in landing_page.get_service_name()

    landing_page.go_to_download_page()

    email_confirm_page = DocumentDownloadConfirmEmailPage(driver)
    email_confirm_page.input_email_address(config["service"]["seeded_user"]["email"])
    email_confirm_page.click_continue()

    download_page = DocumentDownloadPage(driver)
    download_page.click_download_link()

    body = driver.find_element(By.TAG_NAME, "body")
    assert body.text == "foo-bar-baz"
