import pytest

from config import setup_staging_prod_config


@pytest.fixture(scope="session", autouse=True)
def staging_prod_config():
    """
    Setup
    """
    setup_staging_prod_config()
