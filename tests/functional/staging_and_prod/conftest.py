import pytest

from config import setup_staging_live_config


@pytest.fixture(scope="session", autouse=True)
def staging_live_config():
    """
    Setup
    """
    setup_staging_live_config()
