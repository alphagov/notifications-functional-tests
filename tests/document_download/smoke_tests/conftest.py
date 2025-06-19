import os

import pytest

from config import get_all_unique_seeder_user_tests, setup_functional_tests_config, setup_smoke_tests_config


@pytest.fixture(scope="session", autouse=True)
def smoke_tests_config(request: pytest.FixtureRequest):
    """
    Setup
    """
    if os.environ.get("API_FIXTURE_APPLIED") == "true":
        setup_functional_tests_config(get_all_unique_seeder_user_tests(request))
    else:
        setup_smoke_tests_config()
