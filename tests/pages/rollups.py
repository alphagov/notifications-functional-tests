import pdb
from urllib.parse import urlparse

from config import config
from tests.pages import SignInPage
from tests.test_utils import do_email_auth_verify, do_verify

def sign_in_webauthn(driver, account_type='broadcast_create_user'):
    _sign_in(driver, account_type)

    assert driver.current_url == config['notify_admin_url'] + '/two-factor-webauthn'
    _provide_webauthn_key(driver)


def _provide_webauthn_key(driver):

    # eg "localhost" or "www.notify.works" (no protocol, port, or specific page path)
    notify_admin_hostname = urlparse(config['notify_admin_url']).hostname

    # instruct browser to intercept all webauthn requests
    driver.execute_cdp_cmd('WebAuthn.enable', {})

    # options as defined here: https://chromedevtools.github.io/devtools-protocol/tot/WebAuthn/#type-VirtualAuthenticatorOptions
    ret = driver.execute_cdp_cmd('WebAuthn.addVirtualAuthenticator', {'options': {
        'protocol': "ctap2",
        'transport': "usb",
        'automaticPresenceSimulation': True,
        'hasResidentKey': True,
        'isUserVerified': True,
    }})

    virtual_authenticator_id = ret['authenticatorId']

    driver.execute_cdp_cmd('WebAuthn.addCredential', {
        'authenticatorId': virtual_authenticator_id,
        # this key was created by navigating to http://localhost:6012/user-profile/security-keys and clicking the register a key button
        'credential': {
            'credentialId': 'jjKPL6TusZ6VKswFdhZEa58zWiOCvyJZpC4kIcrJc7Y=',
            # this cred is not resident on the key - instead it lives on the relying party, notify admin
            # ie: notify knows what key to expect as it's already in the database
            'isResidentCredential': False,
            # rpId stands for Relying Party ID. Needs to match the file referenced in
            # notifications-admin/app/models/webauthn_credential.py
            'rpId': notify_admin_hostname,
            'privateKey': 'MIGHAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBG0wawIBAQQgsx0GO0aFcT1nIL6qZyO3pcSrfcpAoD0Kwoxn8vFR/QuhRANCAASX1/IFy8+ZdUO5gYDrCSxjGfUoR2eeXTMR5GjKnafGaCf6kPsxDy3hCuHfIc6SRTIYbXHwPik6R76L6YBRi55R',
            'signCount': 1
        }
    })

    check_security_key_button = driver.find_element_by_css_selector('button.webauthn__api-required')
    check_security_key_button.click()
    import pdb
    pdb.set_trace()
    pass


def sign_in_sms(driver, account_type='normal'):
    _sign_in(driver, account_type)
    do_verify(driver)


def sign_in_email_auth(driver):
    _sign_in(driver, 'email_auth')
    assert driver.current_url == config['notify_admin_url'] + '/two-factor-email-sent'
    do_email_auth_verify(driver)


def _sign_in(driver, account_type):
    sign_in_page = SignInPage(driver)
    sign_in_page.get()
    assert sign_in_page.is_current()
    email, password = get_email_and_password(account_type=account_type)
    sign_in_page.login(email, password)


def get_email_and_password(account_type):
    if account_type == 'normal':
        return config['user']['email'], config['user']['password']
    elif account_type == 'seeded':
        return config['service']['seeded_user']['email'], config['service']['seeded_user']['password']
    elif account_type == 'email_auth':
        # has the same password as the seeded user
        return config['service']['email_auth_account'], config['service']['seeded_user']['password']
    elif account_type == 'broadcast_create_user':
        return (
            config['broadcast_service']['broadcast_user_1']['email'],
            config['broadcast_service']['broadcast_user_1']['password']
        )
    elif account_type == 'broadcast_approve_user':
        return (
            config['broadcast_service']['broadcast_user_2']['email'],
            config['broadcast_service']['broadcast_user_2']['password']
        )
    raise Exception('unknown account_type {}'.format(account_type))
