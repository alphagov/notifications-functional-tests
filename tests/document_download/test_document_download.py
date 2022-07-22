import base64

import pytest
import requests
from retry.api import retry_call

from config import config
from tests.pages import DocumentDownloadLandingPage, DocumentDownloadPage


def upload_document(service_id, file_contents):
    response = requests.post(
        f"{config['document_download']['api_host']}/services/{service_id}/documents",
        headers={
            'Authorization': f"Bearer {config['document_download']['api_key']}",
        },
        json={
            'document': base64.b64encode(file_contents).decode('ascii')
        }
    )

    json = response.json()
    assert 'error' not in json, 'Status code {}'.format(response.status_code)

    return json['document']


@pytest.mark.antivirus
def test_document_upload_and_download(driver):
    document = retry_call(
        upload_document,
        # add PDF header to trick doc download into thinking its a real pdf
        fargs=[config['service']['id'], b'%PDF-1.4 functional tests file'],
        tries=3,
        delay=10
    )

    driver.get(document['url'])

    landing_page = DocumentDownloadLandingPage(driver)
    assert 'Functional Tests' in landing_page.get_service_name()

    landing_page.go_to_download_page()

    download_page = DocumentDownloadPage(driver)
    document_url = download_page.get_download_link()

    downloaded_document = requests.get(document_url)

    assert downloaded_document.text == '%PDF-1.4 functional tests file'
