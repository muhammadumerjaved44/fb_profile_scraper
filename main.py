import glob
import io
import string
from pathlib import Path

import requests
import uvicorn
from decouple import config
from fastapi import FastAPI, Response, status, HTTPException
from fastapi.openapi.utils import get_openapi

from scraper import main, load_browser, login, get_profile,desktop_image_scrapper, download_image_from_fbid



app = FastAPI()


@app.get("/scrap", tags=["demo"])
async def get_profile_images(profile_name, response: Response):
    # profile_name= 'alfred.lua'
    # facebook credentials

    email=config('FB_MAIL')
    password=config('FB_PASS')
    profile_name = profile_name
    isHeadless = False

    profile_name = profile_name.strip()

    if len(profile_name) == 0:
        raise HTTPException(status_code=404, detail="profile name can't be empty'")
    else:

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

        return {'massage': 'process done'}



def custom_openapi():

    if app.openapi_schema:

        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Point Duty - Facebook Scraper API",
        version="V-0.0.0",
        description="The Facebook Scraper Api \n FB_MAIL=mushimushi765@gmail.com, FB_PASS=Password@1",
        routes=app.routes,
    )

    openapi_schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    }

    app.openapi_schema = openapi_schema

    return app.openapi_schema


app.openapi = custom_openapi
