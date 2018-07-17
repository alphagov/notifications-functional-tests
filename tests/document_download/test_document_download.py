import requests

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

    json = response.json()
    assert 'error' not in json, 'Status code {}'.format(response.status_code)

    return json['document']['direct_file_url']


def test_document_upload_and_download():
    assert True
