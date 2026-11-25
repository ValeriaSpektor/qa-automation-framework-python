from playwright.sync_api import expect

from src.main.ui.pages.catalog_page import CatalogPage
from src.main.ui.pages.checkout_page_one import CheckoutPageOne
from src.main.ui.pages.checkout_page_two import CheckoutPageTwo

from src.main.ui.steps.catalog_steps import CatalogSteps
from src.main.ui.steps.basket_steps import BasketSteps
from src.main.ui.steps.checkout_steps import CheckoutSteps


BACKPACK = "Sauce Labs Backpack"
SHIRT = "Sauce Labs Bolt T-Shirt"

CHECKOUT_COMPLETE_URL = (
    "https://www.saucedemo.com/"
    "checkout-complete.html"
)


def test_checkout_cart(auth_page):
    catalog_steps = CatalogSteps(auth_page)
    basket_steps = BasketSteps(auth_page)
    checkout_steps = CheckoutSteps(auth_page)

    expect(auth_page).to_have_url(
        CatalogPage.URL
    )

    # Add products
    catalog_steps.add_to_cart(BACKPACK)
    catalog_steps.add_to_cart(SHIRT)

    # Open cart
    catalog_steps.open_cart()

    # Verify cart items
    item_names = (
        basket_steps.get_all_cart_items()
    )

    assert BACKPACK in item_names
    assert SHIRT in item_names

    # Calculate cart total
    prices_sum_from_cart = (
        basket_steps
        .get_sum_all_price_item_from_cart()
    )

    # Open checkout
    basket_steps.open_checkout()

    expect(auth_page).to_have_url(
        CheckoutPageOne.URL
    )

    # Fill checkout information
    checkout_steps.enter_checkout(
        "Ivan",
        "Petrov",
        "123"
    )

    expect(auth_page).to_have_url(
        CheckoutPageTwo.URL
    )

    # Verify Item Total
    item_total = (
        checkout_steps
        .get_item_total_price_from_checkout()
    )

    assert item_total == prices_sum_from_cart

    # Verify Total
    tax = (
        checkout_steps
        .get_sum_tax_price_from_checkout()
    )

    total = (
        checkout_steps
        .get_sum_total_price_from_checkout()
    )

    assert total == item_total + tax

    # Finish purchase
    checkout_steps.click_finish_button()

    expect(auth_page).to_have_url(
        CHECKOUT_COMPLETE_URL
    )

    thank_text = auth_page.locator(
        ".complete-header",
        has_text="Thank you for your order!"
    )

    expect(thank_text).to_be_visible()


def test_checkout_invalid_last_name(
    auth_page
):
    catalog_steps = CatalogSteps(auth_page)
    basket_steps = BasketSteps(auth_page)
    checkout_steps = CheckoutSteps(auth_page)

    expect(auth_page).to_have_url(
        CatalogPage.URL
    )

    catalog_steps.add_to_cart(BACKPACK)

    catalog_steps.open_cart()

    item_names = (
        basket_steps.get_all_cart_items()
    )

    assert BACKPACK in item_names

    basket_steps.open_checkout()

    expect(auth_page).to_have_url(
        CheckoutPageOne.URL
    )

    # Leave Last Name empty
    checkout_steps.enter_checkout(
        "Test",
        "",
        "123"
    )

    assert (
        "Error: Last Name is required"
        in checkout_steps.get_error_text()
    )