import allure
from playwright.sync_api import Page

from src.main.ui.pages.checkout_page_one import CheckoutPageOne
from src.main.ui.pages.checkout_page_two import CheckoutPageTwo


class CheckoutSteps:
    """Steps for checkout pages."""

    def __init__(self, page: Page):
        self.page = page

        self.checkout_page_one = CheckoutPageOne(
            self.page
        )

        self.checkout_page_two = CheckoutPageTwo(
            self.page
        )

    @allure.step(
        "Fill checkout information and click Continue"
    )
    def enter_checkout(
        self,
        first_name: str,
        last_name: str,
        zip_code: str
    ):
        self.checkout_page_one.enter_checkout(
            first_name,
            last_name,
            zip_code
        )

        return self

    @allure.step("Get Item Total")
    def get_item_total_price_from_checkout(self):
        return (
            self.checkout_page_two
            .get_item_total_price_from_checkout()
        )

    @allure.step("Get Tax")
    def get_sum_tax_price_from_checkout(self):
        return (
            self.checkout_page_two
            .get_sum_tax_price_from_checkout()
        )

    @allure.step("Get Total")
    def get_sum_total_price_from_checkout(self):
        return (
            self.checkout_page_two
            .get_sum_total_price_from_checkout()
        )

    @allure.step("Click Finish")
    def click_finish_button(self):
        self.checkout_page_two.click_finish_button()
        return self

    @allure.step("Get checkout error text")
    def get_error_text(self) -> str:
        if self.checkout_page_one.error_text.is_visible():
            return (
                self.checkout_page_one
                .error_text
                .inner_text()
            )

        return ""