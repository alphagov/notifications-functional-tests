import requests
from retry.api import retry_call

from config import config


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

    response.raise_for_status()

    return response.json()['document']['url']


def test_document_upload_and_download():
    document_url = retry_call(
        upload_document,
        fargs=[config['service']['id'], 'functional tests file'],
        tries=3,
        delay=10
    )

    downloaded_document = requests.get(document_url)

    assert downloaded_document.text == 'functional tests file'
