import os
import random
import uuid

import pytest


def generate_unique_email(email, uuid):
    parts = email.split("@")
    return f"{parts[0]}+{uuid}@{parts[1]}"


def get_ofcom_test_number():
    return f"07700{random.randrange(900002, 900899, 1)}"


def get_seeded_users_number_range():
    return range(7700900900, 7700901000, 1)


def get_all_unique_seeder_user_tests(request: pytest.FixtureRequest):
    return sorted(
        [
            node.name
            for node in request.session.items
            if any(
                fixture_name == "login_seeded_user" or fixture_name == "create_seeded_user"
                for fixture_name in node.fixturenames
            )
        ]
    )


# global variable
config = {
    # static
    "notification_retry_times": 15,
    "notification_retry_interval": 5,
    "pdf_generation_retry_times": 40,
    "pdf_generation_retry_interval": 2,
    "verify_callback_retry_times": 40,
    "verify_callback_retry_interval": 1,
    "letter_retry_times": 108,
    "provider_retry_times": 12,
    "provider_retry_interval": 22,
    "verify_code_retry_times": 8,
    "verify_code_retry_interval": 9,
    "functional_test_service_name": "Functional Test Service_",
    "letter_contact_data": {
        "address_line_1": "test",
        "address_line_2": "London",
        "postcode": "N1 7RA",
    },
    # notify templates
    "notify_templates": {
        "email_auth_template_id": "299726d2-dba6-42b8-8209-30e1d66ea164",
        "invitation_template_id": "4f46df42-f795-4cc4-83bb-65ca312f49cc",
        "org_invitation_template_id": "203566f0-d835-47c5-aa06-932439c86573",
        "password_reset_template_id": "474e9242-823b-4f99-813d-ed392e7f1201",
        "registration_template_id": "ece42649-22a8-4d06-b87f-d52d5d3f0a27",
        "verify_code_template_id": "36fb0730-6259-4da1-8a80-c8de22ad4246",
        "request_invite_to_service_template_id": "77677459-f862-44ee-96d9-b8cb2323d407",
    },
}


def setup_shared_config():
    """
    Used by all tests
    """
    config.update(
        {
            "env": os.environ["ENVIRONMENT"].lower(),
            "notify_api_url": os.environ.get("FUNCTIONAL_TESTS_API_HOST", "http://localhost:6011"),
            "notify_admin_url": os.environ.get("FUNCTIONAL_TESTS_ADMIN_HOST", "http://localhost:6012"),
            "name": "{} Functional Tests".format(os.environ["ENVIRONMENT"].lower()),
            "notify_service_api_key": os.environ["NOTIFY_SERVICE_API_KEY"],
            # the smoke tests send a CSV which might get stuck behind other jobs we allow
            # these notifications to take longer (8m rather than the normal wait of 1m15s)
            "smoke_test_csv_notification_retry_time": 96,
        }
    )


def setup_functional_tests_config(unique_seeder_user_tests=None):
    uuid_for_test_run = str(uuid.uuid4())

    config.update(
        {
            "service_name": f"Functional Test_{uuid_for_test_run}",
            "enable_edit_reply_to": os.environ.get("FUNCTIONAL_TESTS_ENABLE_EDIT_REPLY_TO", "0"),
            "user": {
                "name": "{}_Functional Test_{}".format(config["env"], uuid_for_test_run),
                "email": generate_unique_email(os.environ["FUNCTIONAL_TEST_EMAIL"], uuid_for_test_run),
                "password": os.environ["FUNCTIONAL_TEST_PASSWORD"],
                "mobile": get_ofcom_test_number(),
            },
            "api_auth": {
                "client_id": "notify-functional-tests",
                "secret": os.environ["FUNCTIONAL_TESTS_API_AUTH_SECRET"],
            },
            "service": {
                "id": os.environ["FUNCTIONAL_TESTS_SERVICE_ID"],
                "name": os.environ["FUNCTIONAL_TESTS_SERVICE_NAME"],
                "seeded_user": {
                    "email": os.environ["FUNCTIONAL_TESTS_SERVICE_EMAIL"],
                    "password": os.environ["FUNCTIONAL_TESTS_SERVICE_EMAIL_PASSWORD"],
                    "mobile": os.environ["FUNCTIONAL_TESTS_SERVICE_NUMBER"],
                },
                "api_live_key": os.environ["FUNCTIONAL_TESTS_SERVICE_API_KEY"],
                "api_test_key": os.environ["FUNCTIONAL_TESTS_SERVICE_API_TEST_KEY"],
                # email address of seeded email auth user
                "email_auth_account": os.environ["FUNCTIONAL_TESTS_SERVICE_EMAIL_AUTH_ACCOUNT"],
                "organisation_id": os.environ["FUNCTIONAL_TESTS_ORGANISATION_ID"],
                "email_reply_to": os.environ["FUNCTIONAL_TESTS_SERVICE_EMAIL_REPLY_TO"],
                "email_reply_to_2": os.environ.get("FUNCTIONAL_TESTS_SERVICE_EMAIL_REPLY_TO_2"),
                "email_reply_to_3": os.environ.get("FUNCTIONAL_TESTS_SERVICE_EMAIL_REPLY_TO_3"),
                "sms_sender_text": "func tests",
                "templates": {
                    "email": os.environ["FUNCTIONAL_TEST_EMAIL_TEMPLATE_ID"],
                    "sms": os.environ["FUNCTIONAL_TEST_SMS_TEMPLATE_ID"],
                    "letter": os.environ["FUNCTIONAL_TEST_LETTER_TEMPLATE_ID"],
                },
                "inbound_number": os.environ["FUNCTIONAL_TESTS_SERVICE_INBOUND_NUMBER"],
            },
            "mmg_inbound_sms": {
                "username": os.environ["MMG_INBOUND_SMS_USERNAME"],
                "password": os.environ["MMG_INBOUND_SMS_AUTH"],
            },
            "pipedream": {
                "api_token": os.environ["REQUEST_BIN_API_TOKEN"],
                "source_id": "dc_bPuNxED",
            },
            "unique_seeder_user_tests": unique_seeder_user_tests or [],
        }
    )


def setup_smoke_tests_config():
    config.update(
        {
            "user": {
                "email": os.environ["FUNCTIONAL_TEST_EMAIL"],
                "password": os.environ["FUNCTIONAL_TEST_PASSWORD"],
                "mobile": os.environ["TEST_NUMBER"],
            },
            "service": {
                "id": os.environ["FUNCTIONAL_TESTS_SERVICE_ID"],
                "api_live_key": os.environ["FUNCTIONAL_TESTS_SERVICE_API_KEY"],
                "api_test_key": os.environ["FUNCTIONAL_TESTS_SERVICE_API_TEST_KEY"],
                "email_auth_account": os.environ["FUNCTIONAL_TESTS_SERVICE_EMAIL_AUTH_ACCOUNT"],
                "seeded_user": {"password": os.environ["FUNCTIONAL_TEST_PASSWORD"]},
                "templates": {
                    "email": os.environ["FUNCTIONAL_TEST_EMAIL_TEMPLATE_ID"],
                    "sms": os.environ["FUNCTIONAL_TEST_SMS_TEMPLATE_ID"],
                    # letter template not set up for smoke tests
                },
                "inbound_number": os.environ["PROVIDER_TEST_INBOUND_NUMBER"],
            },
        }
    )
