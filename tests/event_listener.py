# ruff: noqa: T201
from dataclasses import dataclass
from enum import StrEnum
from typing import Any
from urllib.parse import urlsplit, urlunsplit

from selenium.webdriver.support.events import AbstractEventListener


class EventType(StrEnum):
    NAVIGATE_TO = "NAVIGATE_TO"
    FIND = "FIND"
    CLICK = "CLICK"
    CHANGE_VALUE_OF = "CHANGE_VALUE_OF"
    EXECUTE_SCRIPT = "EXECUTE_SCRIPT"


@dataclass
class Event:
    event_type: EventType
    current_url: str
    data: Any

    def __repr__(self):
        # remove https:// and domain as visual noise
        url = urlunsplit(urlsplit(self.current_url)._replace(scheme="", netloc=""))
        return f"Event({self.event_type}, {url=}, {self.data=})"


class LoggingEventListener(AbstractEventListener):
    """
    Captures all `before_` selenium events and stores them in an array so that they can be printed out for debugging
    """

    _events: list[Event] = []
    _url_history = []

    def clear_events(self):
        self._events = []
        self._url_history = []

    def print_events(self, num_to_print: int = 20):
        print(f"===== Last {num_to_print} events before test finish =====")
        for event in self._events[-num_to_print:]:
            print(event)
        print("")
        print(f"====== Last {num_to_print} URLs before test finish ======")
        for url in self._url_history[-num_to_print:]:
            print(url)
        print("===========================================" + ("=" * len(str(num_to_print))))

    def _add_event(self, event_type: EventType, current_url: str, data: Any):
        self._events.append(Event(event_type=event_type, current_url=current_url, data=data))

        # if url has changed since last time, then add to the record book
        if len(self._url_history) == 0 or current_url != self._url_history[-1]:
            self._url_history.append(current_url)

    # --------- event hooks --------- #

    def before_navigate_to(self, url: str, driver) -> None:
        self._add_event(EventType.NAVIGATE_TO, driver.current_url, url)

    def before_find(self, by, value, driver) -> None:
        self._add_event(EventType.FIND, driver.current_url, (by, value))

    def before_click(self, element, driver) -> None:
        self._add_event(EventType.CLICK, driver.current_url, element)

    def before_change_value_of(self, element, driver) -> None:
        self._add_event(EventType.CHANGE_VALUE_OF, driver.current_url, element)

    def before_execute_script(self, script, driver) -> None:
        self._add_event(EventType.EXECUTE_SCRIPT, driver.current_url, script)
