import requests
from retry.api import retry_call

from config import Config


def upload_document(service_id, file_contents):
    response = requests.post(
        "{}/services/{}/documents".format(Config.DOCUMENT_DOWNLOAD_API_HOST, service_id),
        headers={
            'Authorization': "Bearer {}".format(Config.DOCUMENT_DOWNLOAD_API_KEY),
        },
        files={
            'document': file_contents
        }
    )

    response.raise_for_status()

    return response.json()['document']['url']


def test_document_upload_and_download():
    document_url = retry_call(
        upload_document,
        fargs=[Config.NOTIFY_RESEARCH_SERVICE_ID, 'functional tests file'],
        tries=3,
        delay=10
    )

    downloaded_document = requests.get(document_url)

    assert downloaded_document.text == 'functional tests file'
