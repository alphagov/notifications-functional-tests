# Style guide

## Granularity - or what we want to test here and what we do not want to test here

We do not want to test contents of the page except to:
- do a simple check that would prove we are on the page we expect to be for example check the page title or a heading in the page.
- check presence or status of an object before or after an action, for example:

```python
  # reject an alert
  prepare_alert_pages.click_element_by_link_text("Discard this alert")

  # check that the alert is in the rejected alerts
  prepare_alert_pages.click_element_by_link_text('Rejected alerts')
  rejected_alerts_page = BasePage(driver)
  assert rejected_alerts_page.is_text_present_on_page(template_name)
```

## Creating new classes for pages vs using BasePage

### When to use BasePage:
Use BasePage when all actions you will do on a page can be easily done using BasePage components. You can name your class instance in a way that will indicate what page the test is on, for example:

```python
prepare_alert_pages = BasePage(driver)
  prepare_alert_pages.click_element_by_link_text("Test areas")

```

### When to define a new class for a page:
Define a custom class for a page to DRY-up repetitive actions, to encapsulate complex functionality, and to give meaningful names to actions.


## Custom locators vs.
Use generic functions to click or select elements if possible, like so:

```python
current_alerts_page.click_element_by_link_text("New alert")
```

 and DRY it up into custom functions / custom locators if you need to use the same text / locator in multiple places.
