from playwright.sync_api import expect

from src.main.ui.pages.catalog_page import CatalogPage
from src.main.ui.steps.catalog_steps import CatalogSteps
from src.main.ui.steps.basket_steps import BasketSteps


BACKPACK = "Sauce Labs Backpack"
JACKET = "Sauce Labs Fleece Jacket"
SHIRT = "Sauce Labs Bolt T-Shirt"
RED_SHIRT = "Test.allTheThings() T-Shirt (Red)"


def test_add_item_and_check_in_cart(auth_page):
    catalog_steps = CatalogSteps(auth_page)
    basket_steps = BasketSteps(auth_page)

    expect(auth_page).to_have_url(
        CatalogPage.URL
    )

    catalog_steps.add_to_cart(BACKPACK)
    catalog_steps.open_cart()

    item_name = basket_steps.get_item_name(
        BACKPACK
    )

    assert item_name.inner_text() == BACKPACK


def test_add_jacket_and_shirt_and_check_in_cart(
    auth_page
):
    catalog_steps = CatalogSteps(auth_page)
    basket_steps = BasketSteps(auth_page)

    expect(auth_page).to_have_url(
        CatalogPage.URL
    )

    catalog_steps.add_to_cart(JACKET)
    catalog_steps.add_to_cart(SHIRT)

    catalog_steps.open_cart()

    item_names = (
        basket_steps.get_all_cart_items()
    )

    assert JACKET in item_names
    assert SHIRT in item_names


def test_remove_item_from_cart(auth_page):
    catalog_steps = CatalogSteps(auth_page)
    basket_steps = BasketSteps(auth_page)

    expect(auth_page).to_have_url(
        CatalogPage.URL
    )

    catalog_steps.add_to_cart(JACKET)
    catalog_steps.open_cart()

    item_name = basket_steps.get_item_name(
        JACKET
    )

    expect(item_name).to_be_visible()

    basket_steps.remove_item_from_cart(
        JACKET
    )

    expect(item_name).not_to_be_visible()


def test_remove_backpack_and_shirt_from_cart(
    auth_page
):
    catalog_steps = CatalogSteps(auth_page)
    basket_steps = BasketSteps(auth_page)

    expect(auth_page).to_have_url(
        CatalogPage.URL
    )

    catalog_steps.add_to_cart(BACKPACK)
    catalog_steps.add_to_cart(RED_SHIRT)

    catalog_steps.open_cart()

    backpack = basket_steps.get_item_name(
        BACKPACK
    )

    shirt = basket_steps.get_item_name(
        RED_SHIRT
    )

    expect(backpack).to_be_visible()
    expect(shirt).to_be_visible()

    basket_steps.remove_item_from_cart(
        BACKPACK
    )

    basket_steps.remove_item_from_cart(
        RED_SHIRT
    )

    expect(backpack).not_to_be_visible()
    expect(shirt).not_to_be_visible()