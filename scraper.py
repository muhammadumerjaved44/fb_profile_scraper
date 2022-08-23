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


