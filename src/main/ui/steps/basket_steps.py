import allure
from playwright.sync_api import Page

from src.main.ui.pages.basket_page import BasketPage


class BasketSteps:
    """Steps for working with the cart page."""

    def __init__(self, page: Page):
        self.page = page
        self.basket_page = BasketPage(self.page)

    @allure.step("Open basket page")
    def open_basket_page(self):
        self.basket_page.open()
        return self

    @allure.step("Get product {product_name} from basket")
    def get_item_name(self, product_name: str):
        return self.basket_page.get_item_name(
            product_name
        )

    @allure.step("Get all cart items")
    def get_all_cart_items(self):
        return self.basket_page.get_all_cart_items()

    @allure.step("Remove product {product_name} from basket")
    def remove_item_from_cart(self, product_name: str):
        return self.basket_page.remove_item_from_cart(
            product_name
        )

    @allure.step("Calculate total price of basket items")
    def get_sum_all_price_item_from_cart(self):
        return (
            self.basket_page
            .get_sum_all_price_item_from_cart()
        )

    @allure.step("Open checkout")
    def open_checkout(self):
        self.basket_page.open_checkout()
        return self