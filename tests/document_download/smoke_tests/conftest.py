import os

import pytest

from config import get_all_unique_seeder_user_tests, setup_preview_dev_config, setup_staging_prod_config


@pytest.fixture(scope="session", autouse=True)
def staging_prod_config(request: pytest.FixtureRequest):
    """
    Setup
    """
    if os.environ.get("API_FIXTURE_APPLIED") == "true":
        setup_preview_dev_config(get_all_unique_seeder_user_tests(request))
    else:
        setup_staging_prod_config()
