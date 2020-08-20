import requests
import sys
import re
import json
from bs4 import BeautifulSoup as zbs


def getData(username):
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)',
    }

    s = requests.Session()
    s.headers.update(headers)

    basePage = s.get("https://www.instagram.com/{}/".format(username))
    basePageSoup = zbs(basePage.text)
    basePageSources = basePageSoup.findAll('script',{"src":True})

    for i in basePageSources:
        if "ProfilePageContainer" in i['src']:
            ProfilePageScript = s.get(i['src']).text



