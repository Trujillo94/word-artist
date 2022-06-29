import os
import time
from datetime import datetime
from shutil import move
from tempfile import gettempdir

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from src.utils.files_management_toolbox import (append_suffix_to_filename,
                                                clear_directory,
                                                create_directory)
from src.utils.string_toolbox import convert_to_kebab_case, get_class_name


def get_selenium_browser(url, waiting_time=10):
    try:
        from pyvirtualdisplay import Display
        display = Display(visible=False, size=(1080, 800))
        display.start()
        # profile = webdriver.FirefoxProfile()
        # profile.set_preference("http.response.timeout", 600)
        # driver = webdriver.Firefox(firefox_profile=profile)
        # options = webdriver.ChromeOptions()
        options = Options()
        # options.add_argument('--headless')
        # options.add_argument('--no-sandbox')
        # options.add_argument('--single-process')
        # options.add_argument('--disable-dev-shm-usage')

        options.add_argument('--ignore-certificate-errors')
        # options.add_argument("--dns-prefetch-disable")
        # options.add_argument("--http-response-timeout 600") !! MADE UP !!
        driver = webdriver.Chrome(chrome_options=options)

        driver.get(url)
        time.sleep(waiting_time)
        return driver, display
    except Exception as e:
        try:
            if display:
                display.stop()
        except:
            pass
        raise Exception(f'Failed getting Selenium driver. Message: <{e}>.')


def wait_for_element(driver, _type, value, ignore_exceptions=False, max_attempts=3, waiting_timeout=120):
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
        for i in range(0, max_attempts):
            try:
                element_present = EC.presence_of_element_located(
                    (element_type, value))
                WebDriverWait(driver, waiting_timeout).until(element_present)
                return
            except TimeoutException as e:
                msg = f'Timed out waiting for page to load: {e}'
            except Exception as e:
                msg = f'Error occured waiting for {value} element: {e}'
        raise Exception(
            f'Failed wating for {value} {_type} element after {max_attempts} of {waiting_timeout}s of timeout. Message: {msg}')
    except Exception as e:
        if not ignore_exceptions:
            raise e


def get_element_by_id(driver, element_id, max_attempts=20, waiting_time=3):
    for i in range(0, max_attempts):
        try:
            element = driver.find_element_by_id(element_id)
            return element
        except:
            time.sleep(waiting_time)
    raise Exception(
        f'Could not get {element_id} element after {max_attempts} attempts with a {waiting_time}s interval')


def get_element_by_xpath(driver, xpath, max_attempts=20, waiting_time=3):
    for i in range(0, max_attempts):
        try:
            element = driver.find_element_by_xpath(xpath)
            return element
        except:
            time.sleep(waiting_time)
    raise Exception(
        f'Could not get {xpath} element after {max_attempts} attempts with a {waiting_time}s interval')


def get_element_by_class_name(driver, element_class, max_attempts=20, waiting_time=3):
    for i in range(0, max_attempts):
        try:
            element = driver.find_element_by_class_name(element_class)
            return element
        except:
            time.sleep(waiting_time)
    raise Exception(
        f'Could not get {element_class} element after {max_attempts} attempts with a {waiting_time}s interval')


def click_dropdown_option_by_text(dropdown_element, value, ignore_case=False):
    for option in dropdown_element.find_elements_by_tag_name('option'):
        if option.text == value or (ignore_case and option.text.lower() == value.lower()):
            option.click()  # select() in earlier versions of webdriver
            return
    print('Did NOT click any option!')


class AbstractSeleniumCrawler:

    # Public:
    def __init__(self, max_attempts=20, waiting_time=3, base_dir=None):
        self._max_attempts = max_attempts
        self._waiting_time = waiting_time
        self.url = self._url
        if base_dir is None:
            timestamp = self._get_timestamp()
            parent_dir = f'{gettempdir()}/{convert_to_kebab_case(get_class_name(self))}'
            create_directory(parent_dir)
            base_dir = f'{parent_dir}/{timestamp}'
        clear_directory(base_dir)
        self._base_dir = base_dir

    def __del__(self):
        try:
            self._display.stop()
        except Exception as e:
            raise Exception(f'Failed stopping display. Message: <{e}>.')
        try:
            self._driver.quit()
        except Exception as e:
            raise Exception(f'Failed quitting driver. Message: <{e}>.')

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, v):
        self._url = v
        self._update_browser(v)

    def get_element_by_class_name(self, element_class: str, max_attempts=None, waiting_time=None):
        if max_attempts is None:
            max_attempts = self._max_attempts
        if waiting_time is None:
            waiting_time = self._waiting_time
        return get_element_by_class_name(self._driver, element_class, max_attempts=max_attempts, waiting_time=waiting_time)

    def get_element_by_id(self, _id: str, max_attempts=None, waiting_time=None):
        if max_attempts is None:
            max_attempts = self._max_attempts
        if waiting_time is None:
            waiting_time = self._waiting_time
        return get_element_by_id(self._driver, _id, max_attempts=max_attempts, waiting_time=waiting_time)

    def get_element_by_xpath(self, xpath: str, max_attempts=None, waiting_time=None):
        if max_attempts is None:
            max_attempts = self._max_attempts
        if waiting_time is None:
            waiting_time = self._waiting_time
        return get_element_by_xpath(self._driver, xpath, max_attempts=max_attempts, waiting_time=waiting_time)

    def save_screenshot(self, filename: str = None):
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

    def move_last_downloaded_file(self, new_filepath: str = None):
        last_filepath = self.get_last_download_filepath()
        if new_filepath is None:
            new_filepath = self._get_new_filepath(last_filepath)
        move(last_filepath, new_filepath)
        return new_filepath

    # Protected:
    def _update_browser(self, url):
        self._driver, self._display = get_selenium_browser(url)

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
