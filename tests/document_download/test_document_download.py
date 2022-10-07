import re
from io import BytesIO

import pytest
import requests
from notifications_python_client import prepare_upload

from config import config
from tests.pages import DocumentDownloadLandingPage, DocumentDownloadPage


@pytest.mark.antivirus
def test_document_upload_and_download(driver, seeded_client):

    # add PDF header to trick doc download into thinking its a real pdf
    file = prepare_upload(
        BytesIO(b"%PDF-1.4 functional tests file"),
        confirm_email_before_download=False,
    )
    personalisation = {"build_id": file}
    email_address = config["user"]["email"]
    template_id = config["service"]["templates"]["email"]

    resp_json = seeded_client.send_email_notification(
        email_address, template_id, personalisation
    )

    download_link = re.search(r"(https?://\S+)", resp_json["content"]["body"])

    assert download_link

    driver.get(download_link.group(0))

    landing_page = DocumentDownloadLandingPage(driver)
    assert "Functional Tests" in landing_page.get_service_name()

    landing_page.go_to_download_page()

    download_page = DocumentDownloadPage(driver)
    document_url = download_page.get_download_link()

    downloaded_document = requests.get(document_url)

    assert downloaded_document.text == "%PDF-1.4 functional tests file"
