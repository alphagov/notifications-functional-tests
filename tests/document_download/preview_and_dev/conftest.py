import pytest

from config import get_all_unique_seeder_user_tests, setup_preview_dev_config


@pytest.fixture(scope="session", autouse=True)
def preview_dev_config(request: pytest.FixtureRequest):
    """
    Setup
    """
    setup_preview_dev_config(get_all_unique_seeder_user_tests(request))
