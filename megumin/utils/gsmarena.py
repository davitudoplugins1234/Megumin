import requests
from bs4 import BeautifulSoup
import json
import random
import asyncio

proxies = [
    "http://8.219.169.172:20201",
    "http://119.13.111.169:20201",
    "http://121.37.203.216:20201",
    "http://47.254.158.115:20201",
    "http://localhost:8080",
    "http://localhost:3000",
]

def getDataFromUrl(url):
    shuffled_proxies = proxies.copy()  # Create a copy of the list
    random.shuffle(shuffled_proxies)   # Shuffle the list of proxies
    for proxy in shuffled_proxies:
        try:
            response = requests.get(url, proxies={'http': proxy})
            response.raise_for_status()  # Raise an exception for HTTP errors
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching data from {url} using proxy {proxy}: {e}")
            continue  # Try the next proxy in case of an error
        else:
            print(f"Data fetched successfully using proxy {proxy}")
            break  # Exit the loop if data is fetched successfully
    
    # If all proxies fail, return None
    return None

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
