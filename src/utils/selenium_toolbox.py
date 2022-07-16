import os
import time
from asyncio.log import logger
from datetime import datetime
from enum import Enum, auto
from shutil import move
from tempfile import gettempdir

from pyvirtualdisplay.display import Display
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import Chrome, ChromeOptions, Firefox, FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from src.utils.files_management_toolbox import (append_suffix_to_filename,
                                                clear_directory,
                                                create_directory)
from src.utils.string_toolbox import convert_to_kebab_case, get_class_name


class Browser(Enum):
    CHROME = auto()
    FIREFOX = auto()


def get_webdriver(url: str, page_timeout: int = 60, browser=Browser.CHROME, headless: bool = False) -> tuple[WebDriver, Display]:
    match browser:
        case Browser.CHROME:
            return get_chrome_webdriver(url, page_timeout=page_timeout, headless=headless)
        case Browser.FIREFOX:
            return get_firefox_webdriver(url, page_timeout=page_timeout, headless=headless)
        case _:
            raise Exception(
                f'Invalid browser. Valid values are: {list(Browser)}')
    # try:
    #     from pyvirtualdisplay import Display
    #     display = Display(visible=False, size=(1080, 800))
    #     display.start()
    #     # profile = webdriver.FirefoxProfile()
    #     # profile.set_preference("http.response.timeout", 600)
    #     # driver = webdriver.Firefox(firefox_profile=profile)
    #     options = webdriver.ChromeOptions()
    #     # options = Options()
    #     # options.add_argument('--headless')
    #     # options.add_argument('--no-sandbox')
    #     # options.add_argument('--single-process')
    #     # options.add_argument('--disable-dev-shm-usage')

    #     options.add_argument('--ignore-certificate-errors')
    #     # options.add_argument("--dns-prefetch-disable")
    #     # options.add_argument("--http-response-timeout 600") !! MADE UP !!
    #     driver = webdriver.Chrome(options=options)

    #     driver.get(url)
    #
    #     return driver, display
    # except Exception as e:
    # try:
    #     if display:
    #         display.stop()
    # except:
    #     pass
    # raise Exception(f'Failed getting Selenium driver. Message: <{e}>.')


def get_chrome_webdriver(url: str, page_timeout: int = 60, headless: bool = False) -> tuple[WebDriver, Display]:
    with Display(visible=False, size=(800, 600)) as display:
        chromedriver = 'drivers/chromedriver/103'
        options = ChromeOptions()
        # options.binary_location = '/usr/bin/google-chrome'
        if headless:
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
        driver = Chrome(chromedriver, options=options)
        driver.set_page_load_timeout(page_timeout)
        driver.get(url)
        return driver, display


def get_firefox_webdriver(url: str, page_timeout: int = 60, headless: bool = False) -> tuple[WebDriver, Display]:
    with Display(visible=False, size=(800, 600)) as display:
        options = FirefoxOptions()
        # options.binary_location = '/usr/bin/firefox'
        options = FirefoxOptions()
        if headless:
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
        driver = Firefox(options=options)
        driver.set_page_load_timeout(page_timeout)
        driver.get(url)
        return driver, display


def wait_for_element(driver: WebDriver, _type: str, value, ignore_exceptions: bool = False, max_attempts: int = 3, timeout: int = 120) -> None:
    if 'class' in _type:
        element_type = By.CLASS_NAME
    elif 'text' in _type:
        element_type = By.PARTIAL_LINK_TEXT
    elif 'id' in _type:
        element_type = By.ID
    elif 'tag' in _type:
        element_type = By.TAG_NAME
    else:
        raise Exception('Invalid element_type')
    try:
        msg = 'Unknown error'
        for i in range(0, max_attempts):
            try:
                element_present = EC.presence_of_element_located(
                    (element_type, value))
                WebDriverWait(driver, timeout).until(
                    element_present)
                return
            except TimeoutException as e:
                msg = f'Timed out waiting for page to load: {e}'
            except Exception as e:
                msg = f'Error occured waiting for {value} element: {e}'
        raise Exception(
            f'Failed wating for {value} {_type} element after {max_attempts} of {timeout}s of timeout. Message: {msg}')
    except Exception as e:
        if not ignore_exceptions:
            raise e


def find_element(driver: WebDriver, by: str, value: str, max_attempts: int = 20, retry_wait_time: int = 3) -> WebElement:
    msg = 'Unknown error'
    for i in range(0, max_attempts):
        try:
            return driver.find_element(by, value)
        except Exception as e:
            msg = str(e)
            time.sleep(retry_wait_time)
    raise Exception(
        f'Could not get {value} element after {max_attempts} attempts with a {retry_wait_time}s interval. Details: <{msg}>.')


def click_dropdown_option_by_text(dropdown_element, value, ignore_case: bool = False) -> None:
    for option in dropdown_element.find_elements_by_tag_name('option'):
        if option.text == value or (ignore_case and option.text.lower() == value.lower()):
            option.click()  # select() in earlier versions of webdriver
            return
    print('Did NOT click any option!')


class BaseSeleniumCrawler:

    # Public:
    def __init__(self, url, browser_type=Browser.CHROME, max_attempts: int = 20, retry_wait_time: int = 0, page_timeout: int = 60, headless: bool = False, base_dir: str | None = None):
        self._url = url
        self._browser_type = browser_type
        self._max_attempts = max_attempts
        self._retry_wait_time = retry_wait_time
        self._page_timeout = page_timeout
        self._headless = headless
        self.url = self._url
        if base_dir is None:
            timestamp = self._get_timestamp()
            parent_dir = f'{gettempdir()}/{convert_to_kebab_case(get_class_name(self))}'
            create_directory(parent_dir)
            base_dir = f'{parent_dir}/{timestamp}'
        clear_directory(base_dir)
        self._base_dir = base_dir

    def __del__(self):
        self.quit_webdriver()

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, v):
        self._url = v
        self._update_browser(v)

    def quit_webdriver(self):
        print('Quitting webdriver')
        try:
            self._display.stop()
        except Exception as e:
            raise Exception(f'Failed stopping display. Message: <{e}>.')
        try:
            self._driver.quit()
        except Exception as e:
            raise Exception(f'Failed quitting driver. Message: <{e}>.')

    def find_element(self, by: str, value: str,  max_attempts=None, retry_wait_time=None) -> WebElement:
        if max_attempts is None:
            max_attempts = self._max_attempts
        if retry_wait_time is None:
            retry_wait_time = self._retry_wait_time
        return find_element(self._driver, by, value, max_attempts=max_attempts, retry_wait_time=retry_wait_time)

    def save_screenshot(self, filename: str | None = None):
        if filename is None:
            timestamp = datetime.now().timestamp()
            filename = f'{self._url.split("/")[0]}_{timestamp}.png'
        self._driver.save_screenshot(filename)

    def get_last_download_filepath(self):
        driver = self._driver
        driver.get("chrome://downloads/")
        time.sleep(3)

        show_in_folder = driver.execute_script(
            'return document.querySelector("body > downloads-manager").shadowRoot.querySelector("#frb0").shadowRoot.querySelector("#show")')
        filepath = show_in_folder.get_attribute("title")
        return filepath

    def get_last_download_url(self):
        driver = self._driver
        driver.get("chrome://downloads/")
        time.sleep(3)

        download_link = driver.execute_script(
            'return document.querySelector("body > downloads-manager").shadowRoot.querySelector("#frb0").shadowRoot.querySelector("#url")')

        cancel_button = driver.execute_script(
            'return document.querySelector("body > downloads-manager").shadowRoot.querySelector("#frb0").shadowRoot.querySelector("#safe > div:nth-child(6) > cr-button")')
        if cancel_button is not None:
            cancel_button.click()
        url = download_link.get_attribute('href')
        return url

    def move_last_downloaded_file(self, new_filepath: str | None = None):
        last_filepath = self.get_last_download_filepath()
        if new_filepath is None:
            new_filepath = self._get_new_filepath(last_filepath)
        move(last_filepath, new_filepath)
        return new_filepath

    # Protected:
    def _update_browser(self, url):
        browser = self._browser_type
        self._driver, self._display = get_webdriver(
            url, browser=browser, page_timeout=self._page_timeout, headless=self._headless)

    def _get_new_filepath(self, old_filepath):
        base_dir = self._base_dir
        old_filename = os.path.basename(old_filepath)
        new_filename = self._get_new_filename(old_filename)
        new_filepath = f'{base_dir}/{new_filename}'
        return new_filepath

    def _get_new_filename(self, old_filepath):
        old_filename = os.path.basename(old_filepath)
        timestamp = self._get_timestamp()
        new_filename = append_suffix_to_filename(
            convert_to_kebab_case(old_filename), f'_{timestamp}')
        return new_filename

    def _get_timestamp(self):
        return round(datetime.now().timestamp())
