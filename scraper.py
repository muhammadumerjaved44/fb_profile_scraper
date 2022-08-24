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






def login(email: str , password:str, browser:object):

    """This function creat the login session in the facebook

    Args:
        email (str): require facebook email to be login
        password (str): require password of the facebook profile
        browser (object): require browser instance
    """

    browser.get('https://www.facebook.com/')
    time.sleep(5)

    WebDriverWait(browser, 2500).until(EC.presence_of_element_located((By.TAG_NAME, "input")))
    browser.find_element_by_name("email").send_keys(email)
    browser.find_element_by_name("pass").send_keys(password)
    browser.find_element_by_name("login").click()

    time.sleep(5)







def find_album_url(browser:object) -> set:

    """This will find on the album urls form the browser page

    Args:
        browser (object): require browser instance

    Returns:
        set: return the album_links
    """

    soup = BeautifulSoup(browser.page_source, 'lxml')
    album_links = set(post.get('href') for post in soup.find_all('a', href=re.compile('media/set')))

    return album_links






#working code
def find_photos_urls(browser:object) -> set:

    """this will find the all photos links thats contain the fbid paremeter

    Args:
        browser (object): require browser instance


    Returns:
        set: returns the images_links
    """

    images_links = set()
    soup = BeautifulSoup(browser.page_source, 'lxml')
    images_links = set(post.get('href').split('?')[1].split('&')[0] for post in soup.find_all('a',href=re.compile("fbid")))
    print('this amount of image collected', len(images_links))

    print('returing the images sets of len',len(images_links))

    return images_links






def download_image_from_fbid(all_images_collection: set, browser:object):

    """this funciton start downloading the images when you pass the set of images with fbids

    Args:
        all_images_collection (set): takes set of images
        fbids e.g: {'fbid=10100230247154651','fbid=10100277884733561'}
        browser (object): require browser instance
    """

    os.makedirs(os.path.dirname('download_images/all_images/'), exist_ok=True)

    for i, image in enumerate(sorted(all_images_collection)):

        print(i, image)
        file_name = image
        browser.get(f'https://m.facebook.com/photo/view_full_size/?{image}&ref_component=mbasic_photo_permalink&ref_page=%2Fwap%2Fphoto.php&refid=13&__tn__=%2Cg')
        # time.sleep(1)
        save_as_path = os.path.realpath(f'./download_images/all_images/image_{file_name}.jpg')

        try:
            wget.download(browser.current_url, save_as_path)
            print(f"\n{i}/{len(all_images_collection)}")
        except:
            print('error on image downloading')






@timeit
def long_scroll(browser:object):

    """This funciton dose the scroll on any facebook page

    Args:
        browser (object): require browser instance
    """

    scroll_from = 0
    scroll_limit = 300

    while scroll_from != scroll_limit:

        browser.execute_script("window.scrollTo(%d, %d);" % (scroll_from, scroll_limit))
        time.sleep(10)
        scroll_from = scroll_limit

        scroll_limit = browser.execute_script("return document.body.scrollHeight")
        print(scroll_from, scroll_limit)

    print("\nmaximum scroll done")





@timeit
def get_profile(profile_name:str, browser:object):

    """This funciton load the profile of any person and put 10 sec delay

    Args:
        profile_name (str, optional): Pass the profile in the string.
        browser (object): require browser instance
    """
    # browser.quit()
    # raise HTTPException(status_code=404, detail="this profile is not available'")
    browser.get(f'https://m.facebook.com/{profile_name}/photos')
    time.sleep(10)
    isPageNotAvailable = False

    try:

        soup = BeautifulSoup(browser.page_source, 'lxml')
        matched_text = "The link you followed may be broken, or the page may have been removed."
        isPageNotAvailable = [True for text in soup.find_all(text=re.compile(matched_text)) if text.startswith('The link you followed')][0]

    except:
        print('no error found on the page')

    if isPageNotAvailable:

            print('the profile not found')
            browser.quit()
            print('browser is closing now')

            raise HTTPException(status_code=404, detail="this profile is not available'")

    else:
        print('profile found testing done fine')






@timeit
def desktop_image_scrapper(profile_name:str, browser:object) -> set:

    """This funciton scrape all the information from these
    urls["photos_all", "photos_of", "photos_by", "photos_albums"]

    Args:
        profile_name (str): pass the profile name as argument
        browser (object): require browser instance

    Returns:
        set: returns the set of images collectd form the profile photos, albums and others images
    """

    all_images_collection = set()

    for i in ["photos_all", "photos_of", "photos_by", "photos_albums"]:
        print('scrapper working on this page = ', i)
        # i = 'photos_of'

        if i == 'photos_albums':

            print('run album script')
            browser.get(f"https://www.facebook.com/{profile_name}/{i}/")
            time.sleep(5)
            album_links = find_album_url(browser)

            for link in album_links:

                browser.get(link)
                time.sleep(5)
                long_scroll(browser)
                time.sleep(2)
                some_images = find_photos_urls(browser)
                all_images_collection.update(some_images)

        else:

            browser.get(f"https://www.facebook.com/{profile_name}/{i}/")
            time.sleep(5)
            long_scroll(browser)
            time.sleep(2)
            some_images = find_photos_urls(browser)
            all_images_collection.update(some_images)

    return all_images_collection



#https://medium.com/analytics-vidhya/the-art-of-not-getting-blocked-how-i-used-selenium-python-to-scrape-facebook-and-tiktok-fd6b31dbe85f

def main(email:str,
         password:str,
         headless:bool,
         profile_name:str):

    """This is the main function. code starts form here

    Args:
        email (str): required the email of facebook account
        password (str): required the password of facebook account
        headless (bool): required the headless flag e.g headless=True
        profile_name (str): required the profile that need to be scraped
    """

    try:

        email = email
        password = password
        profile_name = profile_name
        isHeadless = headless
        driver = load_browser(isHeadless)

        #facebook login
        login(email, password, driver)

        get_profile(profile_name, driver)

        all_images_collection = desktop_image_scrapper(profile_name, driver)

        driver.quit()

        driver = load_browser(isHeadless)

        #facebook login
        login(email, password, driver)

        download_image_from_fbid(all_images_collection, driver)
        print('closing browser')
        driver.quit()

    except Exception as e:
        print('error or try catch', e)






if __name__ == "__main__":

    """Run this code like $ python scrape.py.
    Note: For demo run from this file only.
    """
    # facebook credentials
    FB_MAIL=config('FB_MAIL')
    FB_PASS=config('FB_PASS')
    # e.g 'alfred.lua'
    main(email=FB_MAIL,password=FB_PASS, headless=False, profile_name='alfred.lua')