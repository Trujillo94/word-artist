from asyncio.log import logger

import pytest
from genericpath import exists
from pyvirtualdisplay.display import Display
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from src.utils.selenium_toolbox import (BaseSeleniumCrawler, Browser,
                                        get_webdriver)

TEST_URL = 'https://books.toscrape.com/'
PAGE_TIMEOUT = 60
RETRY_WAIT_TIME = 0


def test_chrome_get_driver() -> None:
    assert_webdriver(get_webdriver(TEST_URL, browser=Browser.CHROME,
                     page_timeout=PAGE_TIMEOUT, headless=False))


def test_headless_chrome_get_driver() -> None:
    assert_webdriver(get_webdriver(
        TEST_URL, browser=Browser.CHROME, page_timeout=PAGE_TIMEOUT, headless=True))


def test_firefox_get_driver() -> None:
    assert_webdriver(get_webdriver(TEST_URL, browser=Browser.FIREFOX,
                     page_timeout=PAGE_TIMEOUT, headless=False))


def test_headless_firefox_get_driver() -> None:
    assert_webdriver(get_webdriver(
        TEST_URL, browser=Browser.FIREFOX, page_timeout=PAGE_TIMEOUT, headless=True))


@pytest.mark.skip(reason='Work in progress')
def test_chrome_get_element_by_class() -> None:
    crawler = BaseSeleniumCrawler(
        TEST_URL, browser_type=Browser.CHROME, page_timeout=PAGE_TIMEOUT, retry_wait_time=RETRY_WAIT_TIME, headless=False)
    element = crawler.find_element(By.CLASS_NAME,
                                   'image_container', max_attempts=1)
    assert type(element) is WebElement


@pytest.mark.skip(reason='Work in progress')
def assert_webdriver(driver_tuple: tuple) -> None:
    driver, display = driver_tuple
    assert isinstance(driver, WebDriver)
    assert isinstance(display, Display)
    try:
        display.stop()
    except Exception as e:
        logger.warning(f'Exception while stopping display: {e}')
    try:
        driver.quit()
    except Exception as e:
        logger.warning(f'Exception while quitting driver: {e}')


if __name__ == "__main__":
    # test_chrome_get_driver()
    # test_headless_chrome_get_driver()
    # test_firefox_get_driver()
    # test_headless_firefox_get_driver()
    test_chrome_get_element_by_class()
