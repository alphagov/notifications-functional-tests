import pytest

from config import get_all_unique_seeder_user_tests, setup_functional_tests_config


@pytest.fixture(scope="session", autouse=True)
def functional_tests_config(request: pytest.FixtureRequest):
    """
    Setup
    """
    setup_functional_tests_config(get_all_unique_seeder_user_tests(request))
