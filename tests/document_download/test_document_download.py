import requests
from retry.api import retry_call

from config import config
from tests.pages import DocumentDownloadLandingPage, DocumentDownloadPage


def upload_document(service_id, file_contents):
    response = requests.post(
        "{}/services/{}/documents".format(config['document_download']['api_host'], service_id),
        headers={
            'Authorization': "Bearer {}".format(config['document_download']['api_key']),
        },
        files={
            'document': file_contents
        }
    )

    json = response.json()
    assert 'error' not in json, 'Status code {}'.format(response.status_code)

    return json['document']


def test_document_upload_and_download(driver):
    document = retry_call(
        upload_document,
        # add PDF header to trick doc download into thinking its a real pdf
        fargs=[config['service']['id'], '%PDF-1.4 functional tests file'],
        tries=3,
        delay=10
    )

    driver.get(document['url'])

    landing_page = DocumentDownloadLandingPage(driver)
    assert landing_page.get_service_name() == 'Functional Tests'

    landing_page.go_to_download_page()

    download_page = DocumentDownloadPage(driver)
    document_url = download_page.get_download_link()

    downloaded_document = requests.get(document_url)

    assert downloaded_document.text == '%PDF-1.4 functional tests file'
