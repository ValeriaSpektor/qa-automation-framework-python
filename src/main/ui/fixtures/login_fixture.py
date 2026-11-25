import pytest


@pytest.fixture
def auth_page(page):
    # Open the login page
    page.goto("https://www.saucedemo.com/")

    # Log in
    page.get_by_placeholder("Username").fill("standard_user")
    page.get_by_placeholder("Password").fill("secret_sauce")
    page.locator("#login-button").click()

    return page