# ruff: noqa: T201
from collections import defaultdict
from dataclasses import dataclass
from enum import StrEnum
from typing import Any
from urllib.parse import urlsplit, urlunsplit

from selenium.webdriver.remote.webelement import WebElement
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
    node: str
    attempts: int = 1

    def __repr__(self):
        # remove https:// and domain as visual noise
        url = urlunsplit(urlsplit(self.current_url)._replace(scheme="", netloc=""))
        return (
            f"Event({self.event_type}, {url=}, {self.data=}"
            # only print num tries if there was more than 1
            + (f", {self.attempts=}" if self.attempts != 1 else "")
            + ")"
        )

    def __eq__(self, other):
        return (
            self.event_type == other.event_type
            and self.current_url == other.current_url
            and self.data == other.data
            and self.node == other.node
        )


class LoggingEventListener(AbstractEventListener):
    """
    Captures all `before_` selenium events and stores them in an array so that they can be printed out for debugging
    """

    _events: dict[str, list[Event]] = defaultdict(list)
    _url_history: dict[str, list[str]] = defaultdict(list)
    node: str = ""

    def set_node(self, node):
        self.node = node

    def clear_events(self):
        self._events = defaultdict(list)
        self._url_history = defaultdict(list)

    def print_events(self, node, num_to_print: int = 20):
        print(f"===== Last {num_to_print} events before test finish =====")
        for event in self._events[node][-num_to_print:]:
            print(event)
        print("")
        print(f"====== Last {num_to_print} URLs before test finish ======")
        for url in self._url_history[node][-num_to_print:]:
            print(url)
        print("===========================================" + ("=" * len(str(num_to_print))))

    def _add_event(self, event_type: EventType, current_url: str, data: Any):
        new_event = Event(node=self.node, event_type=event_type, current_url=current_url, data=data)

        events_for_current_node = self._events[self.node]
        urls_for_current_node = self._url_history[self.node]

        # if the last event was the same thing, then just record how many attempts we did
        if len(events_for_current_node) != 0 and events_for_current_node[-1] == new_event:
            events_for_current_node[-1].attempts += 1
        else:
            events_for_current_node.append(new_event)

        # if url has changed since last time, then add to the record book
        if len(urls_for_current_node) == 0 or current_url != urls_for_current_node[-1]:
            urls_for_current_node.append(current_url)

    @staticmethod
    def _format_element(element: WebElement) -> str:
        """
        elements as reported on in click/change value are a web element that will be stale by the time we print in logs

        just grab the HTML when the element's still in the DOM for printing out later.
        Truncate to 250 characters to avoid absolutely filling the logs if someone is searching for a huge element like
        the entire body or a table or something
        """
        outer_html = element.get_attribute("outerHTML")

        MAX_HTML_LEN = 250
        if len(outer_html) > MAX_HTML_LEN:
            outer_html = outer_html[:MAX_HTML_LEN] + "... <truncated>"
        return outer_html

    # --------- event hooks --------- #

    def before_navigate_to(self, url: str, driver) -> None:
        self._add_event(EventType.NAVIGATE_TO, driver.current_url, url)

    def before_find(self, by, value, driver) -> None:
        self._add_event(EventType.FIND, driver.current_url, (by, value))

    def before_click(self, element, driver) -> None:
        self._add_event(EventType.CLICK, driver.current_url, self._format_element(element))

    def before_change_value_of(self, element, driver) -> None:
        self._add_event(EventType.CHANGE_VALUE_OF, driver.current_url, self._format_element(element))

    def before_execute_script(self, script, driver) -> None:
        self._add_event(EventType.EXECUTE_SCRIPT, driver.current_url, script)
