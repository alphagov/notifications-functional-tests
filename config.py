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
    FUNCTIONAL_TEST_EMAIL_PASSWORD = os.environ[os.environ['ENVIRONMENT'] + '_FUNCTIONAL_TEST_EMAIL_PASSWORD']
    EMAIL_NOTIFICATION_LABEL = 'notify'
    REGISTRATION_EMAIL_LABEL = 'registration'
    INVITATION_EMAIL_LABEL = 'invite'
    EMAIL_TRIES = 10
    EMAIL_DELAY = 5
    FUNCTIONAL_TEST_SERVICE_NAME = os.environ['ENVIRONMENT'] + '_Functional Test Service_'


class StagingConfig(Config):
    FUNCTIONAL_TEST_SERVICE_NAME = 'Staging FunctionalTest'
    SMS_TEMPLATE_ID = os.environ.get('staging_SMS_TEMPLATE_ID')
    EMAIL_TEMPLATE_ID = os.environ.get('staging_EMAIL_TEMPLATE_ID')
    SERVICE_ID = os.environ.get('staging_SERVICE_ID')


class LiveConfig(Config):
    FUNCTIONAL_TEST_SERVICE_NAME = 'Live FunctionalTest'
    SMS_TEMPLATE_ID = os.environ.get('live_SMS_TEMPLATE_ID')
    EMAIL_TEMPLATE_ID = os.environ.get('live_EMAIL_TEMPLATE_ID')
    SERVICE_ID = os.environ.get('live_SERVICE_ID')
    API_KEY = os.environ.get('live_API_KEY')
