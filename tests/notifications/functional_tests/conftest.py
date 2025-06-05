import pytest
import requests
from filelock import FileLock
from notifications_python_client.authentication import create_jwt_token

from config import config, get_all_unique_seeder_user_tests, setup_functional_tests_config


@pytest.fixture(scope="session", autouse=True)
def functional_tests_config(request: pytest.FixtureRequest):
    """
    Setup
    """
    setup_functional_tests_config(get_all_unique_seeder_user_tests(request))


def _create_seeded_users_via_notify_api(test_names):
    from tests.pages.rollups import get_email_and_password, get_mobile_number

    user_info = []
    for test_name in test_names:
        service_id = config["service"]["id"]
        organisation_id = config["service"]["organisation_id"]
        email_address, password = get_email_and_password(account_type="seeded", test_name=test_name)
        mobile_number = get_mobile_number(account_type="seeded", test_name=test_name)
        auth_type = "sms_auth"
        state = "active"
        permissions = [
            "manage_api_keys",
            "manage_settings",
            "manage_templates",
            "manage_users",
            "send_emails",
            "send_letters",
            "send_texts",
            "view_activity",
        ]

        user_info.append(
            {
                "name": f"Preview admin tests user - {test_name}",
                "service_id": service_id,
                "organisation_id": organisation_id,
                "email_address": email_address,
                "password": password,
                "mobile_number": mobile_number,
                "auth_type": auth_type,
                "state": state,
                "permissions": permissions,
            }
        )

    api_token = create_jwt_token(config["api_auth"]["secret"], config["api_auth"]["client_id"])
    headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {api_token}",
    }

    response = requests.put(config["notify_api_url"] + "/__testing/functional/users", json=user_info, headers=headers)
    assert response.status_code == 201


@pytest.fixture(scope="function")
def create_seeded_user():
    # Fixure just added to flag test as needing a seeded user created.
    # See session create_seeded_users fixture for actual creation.
    pass


@pytest.fixture(scope="session", autouse=True)
def create_seeded_users(request: pytest.FixtureRequest, functional_tests_config, tmp_path_factory, worker_id):
    """Finds all tests that use the `login_seeded_user` fixture, and (if necessary) creates seeded users
    for those tests.
    """
    # get the temp directory shared by all workers
    root_tmp_dir = tmp_path_factory.getbasetemp().parent

    unique_seeder_user_tests = get_all_unique_seeder_user_tests(request)
    if worker_id == "master":
        _create_seeded_users_via_notify_api(test_names=unique_seeder_user_tests)

    else:
        create_api_users_file = root_tmp_dir / "create-seeded-users"
        with FileLock(str(create_api_users_file) + ".lock"):
            if not create_api_users_file.is_file():
                create_api_users_file.touch()
                _create_seeded_users_via_notify_api(test_names=unique_seeder_user_tests)
