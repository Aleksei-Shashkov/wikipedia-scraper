import requests # from bs4 import BeautifulSoup
root_url='https://country-leaders.onrender.com'
status_url = root_url + "/status"
countries_url =  root_url+"/countries"
cookie_url = root_url+"/cookie"
leaders_url = root_url + "/leaders"

status_response = requests.get(status_url)

web_cookies = requests.get(cookie_url).cookies
countries = requests.get(countries_url, cookies = web_cookies).json()
leaders = requests.get(leaders_url, cookies = web_cookies, params={"country":"ru"}).json()

leaders_per_country = {country: requests.get(leaders_url, cookies=web_cookies, params={'country': country}).json() for country in countries}

from bs4 import BeautifulSoup # using external library
import re

def get_first_paragraph(wikipedia_url, session):
    wikipedia_response = session.get(wikipedia_url)
    soup = BeautifulSoup(wikipedia_response.text, 'html.parser')
    first_paragraph = ''
    for paragraph in soup.find_all('p'):
        if paragraph.find('b'):
            first_paragraph = paragraph.get_text()
            break
    first_paragraph = re.sub(r' \[.*\].*?,', ',', first_paragraph)
    return first_paragraph

def get_leaders():
    cookies = requests.get(cookie_url).cookies # get the cookie
    countries = requests.get(countries_url, cookies=web_cookies).json() # get the countries

    # get the leaders
    leaders_per_country = {}
    session_render = requests.Session()
    session_wikipedia = requests.Session()
    for country in countries:
        leaders_response = requests.get(leaders_url, cookies=web_cookies, params={'country': country})
        if leaders_response.status_code == 200:
            leaders_per_country[country] = leaders_response.json()
        else:
            cookies = requests.get(cookie_url).cookies
            leaders_per_country[country] = session_render.get(leaders_url, cookies=web_cookies, params={'country': country}).json()

        for leader in leaders_per_country[country]:
            wikipedia_url = leader['wikipedia_url']
            leader['first_paragraph'] = get_first_paragraph(wikipedia_url, session_wikipedia)           

    return leaders_per_country

leaders_per_country = get_leaders()

import json
with open('leaders.json', 'w') as f:
    json.dump(leaders_per_country, f)
    leaders_per_country_copy = json.load(f)

def save(leaders_per_country):
    with open('leaders.json', 'w') as f:
        json.dump(leaders_per_country, f)

save(leaders_per_country)