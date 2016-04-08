import os


class Config(object):
    ENVIRONMENT = os.environ['ENVIRONMENT']
    NOTIFY_ADMIN_URL = os.environ[os.environ['ENVIRONMENT'] + '_NOTIFY_ADMIN_URL']
    NOTIFY_API_URL = os.environ[os.environ['ENVIRONMENT'] + '_NOTIFY_API_URL']
    TWILIO_TEST_NUMBER = os.environ[os.environ['ENVIRONMENT'] + '_TWILIO_TEST_NUMBER']
    TWILIO_ACCOUNT_SID = os.environ[os.environ['ENVIRONMENT'] + '_TWILIO_ACCOUNT_SID']
    TWILIO_AUTH_TOKEN = os.environ[os.environ['ENVIRONMENT'] + '_TWILIO_AUTH_TOKEN']
    FUNCTIONAL_TEST_NAME = os.environ['ENVIRONMENT'] + '_Functional Test_'
    FUNCTIONAL_TEST_EMAIL = os.environ[os.environ['ENVIRONMENT']+'_FUNCTIONAL_TEST_EMAIL']
    FUNCTIONAL_TEST_PASSWORD = os.environ[os.environ['ENVIRONMENT'] + '_FUNCTIONAL_TEST_PASSWORD']
    FUNCTIONAL_EMAIL_TEMPLATE_ID = os.environ[os.environ['ENVIRONMENT'] + '_EMAIL_TEMPLATE_ID']
    FUNCTIONAL_SMS_TEMPLATE_ID = os.environ[os.environ['ENVIRONMENT'] + '_SMS_TEMPLATE_ID']
    FUNCTIONAL_SERVICE_ID = os.environ[os.environ['ENVIRONMENT'] + '_SERVICE_ID']
    FUNCTIONAL_API_KEY = os.environ[os.environ['ENVIRONMENT'] + '_API_KEY']
    EMAIL_NOTIFICATION_LABEL = 'notify'
    REGISTRATION_EMAIL_LABEL = 'registration'
    EMAIL_TRIES = 10
    EMAIL_DELAY = 5
    FUNCTIONAL_TEST_SERVICE_NAME = os.environ['ENVIRONMENT'] + '_Functional Test Service_'
