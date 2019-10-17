import time
import os
import requests
import valve.source
import valve.source.a2s
import valve.source.master_server
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from dotenv import load_dotenv
from requests.exceptions import HTTPError

load_dotenv()
API_KEY = os.getenv("API_KEY")

class SteamQuery():
    '''
    fix me
    '''
    def __init__(self, server_ip, rate):
        '''
        fix me
        '''
        self.server_ip = server_ip
        self.rate = rate
        self.last_limited = time.time()
        self.json_data = {}

    def rate_limit(self):
        '''
        fix me
        '''
        current_time = time.time()
        if current_time - self.last_limited < self.rate:
            print(f"sleeping for {1.0 - (current_time - self.last_limited)}")
            time.sleep(1.0 - (current_time - self.last_limited))
            print('finished')
        else:
            print(f"don't wait last sleep was {self.last_limited}")
        self.last_limited = time.time()

    def init_json(self):
        '''
        fix me
        '''
        self.json_data = {
        "server_info":{
            "ip_address":self.server_ip[0],
            "server_name":"",
            "server_game":"",
            "server_map":"",
            "region":"",
            "player_count":"",
            "max_players":"",
            "server_type":"",
            },
        "player_info":{
            }
        }

    def get_A2s(self):
        '''
        fix me
        '''
        self.rate_limit()
        try:
            with valve.source.a2s.ServerQuerier(self.server_ip) as server:
                info = server.info()
                players = server.players()

        except valve.source.NoResponseError:
            print("Server {}:{} timed out!".format(*self.server_ip))

        self.json_data["server_info"]["server_name"] = ("{server_name}".format(**info))
        self.json_data["server_info"]["player_count"] = ("{player_count}".format(**info))
        self.json_data["server_info"]["max_players"] = ("{max_players}".format(**info))
        self.json_data["server_info"]["server_map"] = ("{map}".format(**info))
        self.json_data["server_info"]["server_game"] = ("{game}".format(**info))
        self.json_data["server_info"]["server_type"] = ("{server_type}".format(**info))
        for player in sorted(players["players"], key=lambda p: p["score"], reverse=True):
            if "{name}".format(**player) != '':
                self.json_data["player_info"]["{name}".format(**player)] = {
                    "steam_id":"",
                    "profile_url":"",
                    "avatar_url":"",
                    "profile_vis":""
                }

    def fill_player_url():
        for dict in self.json_data["player_info"]:
            pass

    def search_player_name(self, name):
        '''
        fix me
        '''
        name = name.replace(" ", "+")
        option = webdriver.ChromeOptions()
        option.add_argument("--incognito")
        browser = webdriver.Chrome(executable_path=r'C:/Program Files (x86)/Google/Chrome/Application/chromedriver.exe', chrome_options=option)
        browser.get(f"https://steamcommunity.com/search/users/#text={name}")
        timeout = 20
        try:
            WebDriverWait(browser, timeout).until(EC.visibility_of_element_located((By.CLASS_NAME, 'searchPersonaName')))
        except TimeoutException:
            print("Timed out waiting for page to load")
            browser.quit()

        html = browser.page_source
        soup = BeautifulSoup(html, 'html.parser')
        resultsRow = soup.find_all('a', {'class': 'searchPersonaName'})
        results = []

        for resultRow in resultsRow:
            steam_name = resultRow.getText()
            steam_URL = resultRow.get('href')
            results.append({
            "name": steam_name,
            "steam_url": steam_URL
            })

        num_match = 0
        name = name.replace("+", " ")
        for dict in results:
            if dict["name"] == name:
                num_match += 1
                match_url = dict["steam_url"]
        if num_match == 1:
            return match_url
        elif num_match == 0:
            return "No steam profile match found"
        elif num_match > 1:
            return "Steam name was too common"

    def get_steam_id(self, url):
        '''
        fix me
        '''
        self.rate_limit()
        try:
            steam_id = requests.get(f'http://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/?key={API_KEY}&vanityurl={url}')
        except HTTPError as http_err:
            return(f'Unable to resolve steam url into id http error:{http_err}')
        except Exception as err:
            return('Unable to resolve steam url into id')
        return steam_id.content

    def fill_player_steam_info(self, steam_id):
        '''
        fix me
        '''
        self.rate_limit()
        try:
            steam_id = requests.get(f'http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={API_KEY}&steamids={steam_id}&format=json')
        except HTTPError as http_err:
            return(f'Unable to resolve steam url into id http error:{http_err}')
        except Exception as err:
            return('Unable to resolve steam url into id')
        return steam_id.content

    def print_json(self):
        '''
        fix me
        '''
        print(self.json_data)

query = SteamQuery(('45.121.209.68', 26015), 1)
# print(query.search_player_name("Who's+Bishop"))
# print(query.get_steam_id("DarkyBenny"))
print(query.fill_player_steam_info("76561198151637619"))
# query.init_json()
# query.get_A2s()
# query.print_json()
