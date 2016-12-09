from selenium.common.exceptions import StaleElementReferenceException


def retry_on_stale_element_exception(func):
    def wrapped(*args, **kwargs):
        retry = 5
        while retry:
            try:
                result = func(*args, **kwargs)
            except StaleElementReferenceException as e:
                if retry:
                    retry -= 1
                    continue
                raise e
            return result

    return wrapped
