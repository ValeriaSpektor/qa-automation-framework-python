import pytest
from pathlib import Path
from playwright.sync_api import sync_playwright, Page


@pytest.fixture(scope="session")
def playwright_instance():
    with sync_playwright() as playwright:
        yield playwright


@pytest.fixture(scope="session")
def browser(playwright_instance):
    browser = playwright_instance.chromium.launch(
        headless=False,
        slow_mo=500
    )

    yield browser

    browser.close()


@pytest.fixture(scope="function")
def page(browser, request) -> Page:
    context = browser.new_context()

    traces_dir = Path("traces")
    traces_dir.mkdir(exist_ok=True)

    context.tracing.start(
        screenshots=True,
        snapshots=True,
        sources=True
    )

    page = context.new_page()

    try:
        yield page
    finally:
        context.tracing.stop(
            path=str(traces_dir / f"{request.node.name}.zip")
        )

        context.close()