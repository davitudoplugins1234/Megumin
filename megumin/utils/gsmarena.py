import requests
from bs4 import BeautifulSoup
import json
import uuid
import asyncio

def getDataFromUrl(url):
    response = requests.get(url)
    return response.text

def search_device(searchValue):
    url = f"https://gsmarena.com/results.php3?sQuickSearch=yes&sName={searchValue}"
    html = getDataFromUrl(url)

    soup = BeautifulSoup(html, 'html.parser')

    json = []

    devices = soup.select('.makers li')

    for i, el in enumerate(devices):
        imgBlock = el.find('img')

        json.append({
            'id': el.find('a')['href'].replace('.php', ''),
            'name': el.find('span').text.replace('\n', '').replace('\r', '').replace('\t', ''),
            'img': imgBlock['src'],
            'description': imgBlock['title'],
        })

    return json
