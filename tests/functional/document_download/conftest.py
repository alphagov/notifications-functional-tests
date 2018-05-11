import pytest

from config import setup_document_download_config


@pytest.fixture(scope="session", autouse=True)
def document_download_config():
    """
    Setup
    """
    setup_document_download_config()
