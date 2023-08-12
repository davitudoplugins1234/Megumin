import requests
from bs4 import BeautifulSoup
import json
import uuid
import asyncio

proxies = {
    "http": "http://50.170.90.34:80",
    "http": "http://50.171.2.10:80",
    "http": "http://localhost:3800",
    "http": "http://localhost:5830",
}

def getDataFromUrl(url):
    headers={"User-Agent": f"{uuid.uuid4()}"}
    response = requests.get(url, headers=headers, proxies=proxies)
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

def get_device(device):
    html = getDataFromUrl(f'https://www.gsmarena.com/{device}.php')
    soup = BeautifulSoup(html, 'html.parser')
    display_size = soup.find('span', {'data-spec': 'displaysize-hl'}).get_text()
    display_res = soup.find('div', {'data-spec': 'displayres-hl'}).get_text()
    camera_pixels = soup.find(class_='accent-camera').get_text()
    video_pixels = soup.find('div', {'data-spec': 'videopixels-hl'}).get_text()
    ram_size = soup.find(class_='accent-expansion').get_text()
    chipset = soup.find('div', {'data-spec': 'chipset-hl'}).get_text()
    battery_size = soup.find(class_='accent-battery').get_text()
    battery_type = soup.find('div', {'data-spec': 'battype-hl'}).get_text()
    quick_spec = [
        {'name': 'Display size', 'value': display_size},
        {'name': 'Display resolution', 'value': display_res},
        {'name': 'Camera pixels', 'value': camera_pixels},
        {'name': 'Video pixels', 'value': video_pixels},
        {'name': 'RAM size', 'value': ram_size},
        {'name': 'Chipset', 'value': chipset},
        {'name': 'Battery size', 'value': battery_size},
        {'name': 'Battery type', 'value': battery_type},
    ]
    name = soup.find(class_='specs-phone-name-title').get_text()
    img = soup.find('div', class_='specs-photo-main').find('img').get('src')
    spec_nodes = soup.find_all('table')
    detail_spec = []
    for el in spec_nodes:
        spec_list = []
        category = el.find('th').get_text()
        spec_n = el.find_all('tr')
        for ele in spec_n:
            ttl = ele.find('td', class_='ttl')
            nfo = ele.find('td', class_='nfo')
            if ttl and nfo:
                spec_list.append({
                    'name': ttl.get_text(),
                    'value': nfo.get_text(),
                })
        if category:
            detail_spec.append({
                'category': category,
                'specifications': spec_list,
            })
    return {
        'name': name,
        'img': img,
        'detailSpec': detail_spec,
        'quickSpec': quick_spec,
    }
