"""Auto-generated step definitions for Playwright using pytest-bdd."""

import pytest
from pytest_bdd import given, when, then, parsers
from playwright.sync_api import Page, expect, sync_playwright


# ===== Fixtures =====

@pytest.fixture(scope="session")
def playwright():
    """Initialize Playwright."""
    with sync_playwright() as p:
        yield p


@pytest.fixture(scope="session")
def browser(playwright):
    """Get browser instance."""
    browser = playwright.chromium.launch(headless=True)
    yield browser
    browser.close()


@pytest.fixture
def page(browser):
    """Get Playwright page fixture."""
    page = browser.new_page()
    yield page
    page.close()


# ===== Given Steps =====

@given(parsers.re(r"""^the user is on the login page$"""))
def step_given_navigate(page):
    """Navigate to a page."""
    # Implement navigation logic
    # Example: page.goto("https://example.com/login")
    pass


# ===== When Steps =====

@when(parsers.re(r"""^the user enters their username$"""))
def step_when_enter_text(page, locator=None, value=None):
    """Enter text into a field."""
    if locator:
        # Extract locator variable
        if locator.startswith("${") and locator.endswith("}"):
            locator_var = locator[2:-1].split(".")[-1]
            # Get element from page object
            # element = getattr(page, locator_var, None)
            # if element and value:
            #     element.fill(value)
            # For now, use direct locator
            page.locator(f"#{locator_var}").fill(value or "test_value")
    pass

@when(parsers.re(r"""^the user enters their password$"""))
def step_when_enter_text(page, locator=None, value=None):
    """Enter text into a field."""
    if locator:
        # Extract locator variable
        if locator.startswith("${") and locator.endswith("}"):
            locator_var = locator[2:-1].split(".")[-1]
            # Get element from page object
            # element = getattr(page, locator_var, None)
            # if element and value:
            #     element.fill(value)
            # For now, use direct locator
            page.locator(f"#{locator_var}").fill(value or "test_value")
    pass

@when(parsers.re(r"""^the user clicks the login button$"""))
def step_when_click(page, locator=None):
    """Click on an element."""
    if locator:
        if locator.startswith("${") and locator.endswith("}"):
            locator_var = locator[2:-1].split(".")[-1]
            # Get element from page object
            # element = getattr(page, locator_var, None)
            # if element:
            #     element.click()
            # For now, use direct locator
            page.locator(f"#{locator_var}").click()
    pass

@when(parsers.re(r"""^the user enters the SQL injection string$"""))
def step_when_enter_text(page, locator=None, value=None):
    """Enter text into a field."""
    if locator:
        # Extract locator variable
        if locator.startswith("${") and locator.endswith("}"):
            locator_var = locator[2:-1].split(".")[-1]
            # Get element from page object
            # element = getattr(page, locator_var, None)
            # if element and value:
            #     element.fill(value)
            # For now, use direct locator
            page.locator(f"#{locator_var}").fill(value or "test_value")
    pass

@when(parsers.re(r"""^the user enters a password$"""))
def step_when_enter_text(page, locator=None, value=None):
    """Enter text into a field."""
    if locator:
        # Extract locator variable
        if locator.startswith("${") and locator.endswith("}"):
            locator_var = locator[2:-1].split(".")[-1]
            # Get element from page object
            # element = getattr(page, locator_var, None)
            # if element and value:
            #     element.fill(value)
            # For now, use direct locator
            page.locator(f"#{locator_var}").fill(value or "test_value")
    pass


# ===== Then Steps =====

@then(parsers.re(r"""^the user should see their name displayed on the dashboard$"""))
def step_then_verify(page, locator=None, value=None):
    """Verify an element or text is visible."""
    if locator and locator.startswith("${") and locator.endswith("}"):
        locator_var = locator[2:-1].split(".")[-1]
        # Get element from page object
        # element = getattr(page, locator_var, None)
        # if element:
        #     expect(element).to_be_visible()
        # For now, use direct locator
        expect(page.locator(f"#{locator_var}")).to_be_visible()
    elif value:
        # Check for text content
        expect(page.locator(f"text={value}")).to_be_visible()
    pass

@then(parsers.re(r"""^the user should see (?P<locator>[^\s]+) error message saying 'Invalid credentials'$"""))
def step_then_verify(page, locator=None, value=None):
    """Verify an element or text is visible."""
    if locator and locator.startswith("${") and locator.endswith("}"):
        locator_var = locator[2:-1].split(".")[-1]
        # Get element from page object
        # element = getattr(page, locator_var, None)
        # if element:
        #     expect(element).to_be_visible()
        # For now, use direct locator
        expect(page.locator(f"#{locator_var}")).to_be_visible()
    elif value:
        # Check for text content
        expect(page.locator(f"text={value}")).to_be_visible()
    pass

@then(parsers.re(r"""^the user should see (?P<locator>[^\s]+) error message$"""))
def step_then_verify(page, locator=None, value=None):
    """Verify an element or text is visible."""
    if locator and locator.startswith("${") and locator.endswith("}"):
        locator_var = locator[2:-1].split(".")[-1]
        # Get element from page object
        # element = getattr(page, locator_var, None)
        # if element:
        #     expect(element).to_be_visible()
        # For now, use direct locator
        expect(page.locator(f"#{locator_var}")).to_be_visible()
    elif value:
        # Check for text content
        expect(page.locator(f"text={value}")).to_be_visible()
    pass


# ===== And Steps =====

# Note: pytest-bdd handles "And" steps automatically by reusing
# the same step definitions. No separate handler needed.
