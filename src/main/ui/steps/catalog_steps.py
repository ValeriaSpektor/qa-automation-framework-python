import allure

from playwright.sync_api import Page, expect

from src.main.ui.pages.login_page import LoginPage
from src.main.ui.pages.catalog_page import CatalogPage


class CatalogSteps:

    def __init__(self, page: Page):
        self.page = page
        self.catalog_page = CatalogPage(page)

    @allure.step("Open catalog page")
    def open_catalog_page(self):
        self.catalog_page.open()
        return self

    @allure.step("Logout from catalog")
    def logout(self):
        self.catalog_page.logout()

        expect(self.page).to_have_url(
            LoginPage.URL
        )

        expect(
            self.page.locator("#login-button")
        ).to_be_visible()

        return self

    @allure.step("Sort catalog by {option}")
    def sort_items(self, option: str):
        self.catalog_page.sort_catalog_items(option)
        return self

    @allure.step("Open cart")
    def open_cart(self):
        self.catalog_page.open_cart()
        return self

    @allure.step("Add product {product_name} to cart")
    def add_to_cart(self, product_name: str):
        return self.catalog_page.add_to_cart(
            product_name
        )

    @allure.step("Remove product {product_name} from cart")
    def remove_from_cart(self, product_name: str):
        return self.catalog_page.remove_from_cart(
            product_name
        )

    @allure.step("Get cart products count")
    def get_cart_count(self) -> int:
        return self.catalog_page.get_cart_count()

    @allure.step("Get cart badge")
    def cart_badge(self):
        return self.catalog_page.cart_badge

    @allure.step("Get products count")
    def get_products_count(self) -> int:
        return self.catalog_page.get_products_count()

    @allure.step("Get product names")
    def get_product_names(self) -> list[str]:
        return self.catalog_page.get_product_names()

    @allure.step("Get product prices")
    def get_product_prices(self) -> list[float]:
        return self.catalog_page.get_product_prices()

    @allure.step("Open product details: {product_name}")
    def open_product_details(self, product_name: str):
        return self.catalog_page.open_product_details(
            product_name
        )