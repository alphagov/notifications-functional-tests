import os

import pytest

from config import setup_preview_dev_config, setup_staging_prod_config


@pytest.fixture(scope="session", autouse=True)
def staging_prod_config():
    """
    Setup
    """
    if os.environ.get("API_FIXTURE_APPLIED") == "true":
        setup_preview_dev_config()
    else:
        setup_staging_prod_config()
