import pytest

from config import setup_preview_dev_config


@pytest.fixture(scope="session", autouse=True)
def preview_dev_config():
    """
    Setup
    """
    setup_preview_dev_config()
