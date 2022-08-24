import os
import re
import time

import wget
from bs4 import BeautifulSoup
from decouple import config
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ActionChains, DesiredCapabilities
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from fastapi import HTTPException

try:
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
except:
    pass

IS_DRIVER_DOCKER_ON = config('DRIVER_DOCKER')
SE_EVENT_BUS_HOST = config('SE_EVENT_BUS_HOST')
SE_EVENT_BUS_PORT = config('SE_EVENT_BUS_PORT')


def timeit(f):

    """timeit is the python decorator function to calulate the execution time of the funcitons

    Args:
        f (funtion): it requires funciton as input
    """

    def timed(*args, **kw):

        ts = time.time()
        result = f(*args, **kw)
        te = time.time()

        print('func:%r args:[%r, %r] took: %2.4f sec' % \
          (f.__name__, args, kw, te-ts))

        return result

    return timed

@timeit
def load_browser(isHeadless: bool) -> object:

    """This fucntion load the chrome browser

    Args:
        isHeadless (bool): if Ture headless is applied otherwise not

    Returns:
        object: returns the browser object
    """

    caps = DesiredCapabilities.CHROME
    caps['goog:loggingPrefs'] = {'performance': 'ALL'}
    option = Options()
    option.add_argument("--disable-infobars")
    option.add_argument("start-maximized")
    if isHeadless: option.add_argument('--headless')
    option.add_argument('--no-sandbox')
    option.add_argument("--disable-extensions")
    option.add_argument("--disable-popup-blocking")
    option.add_argument('--disable-dev-shm-usage')
    option.add_experimental_option("prefs", {
        "profile.default_content_setting_values.notifications": 1
    })

    if not IS_DRIVER_DOCKER_ON:

        print('loading local chrome driver...', os.path.realpath('chromedriver/chromedriver'))
        driver = webdriver.Chrome(executable_path=os.path.realpath('chromedriver/chromedriver'), options=option, desired_capabilities=caps)
        print('local driver is running')

    else:

        print('loading remote chrome driver...')
        remote_url_chrome = f'http://{SE_EVENT_BUS_HOST}:{SE_EVENT_BUS_PORT}/wd/hub'
        driver = webdriver.Remote(remote_url_chrome, options=option, desired_capabilities=caps)
        print('driver is running')

    return driver



