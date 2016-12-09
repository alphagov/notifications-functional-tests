from selenium.common.exceptions import TimeoutException, StaleElementReferenceException


def retry_on_stale_element_exception(func):
    def wrapped(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
        except StaleElementReferenceException:
            result = func(*args, **kwargs)
        return result

    return wrapped
