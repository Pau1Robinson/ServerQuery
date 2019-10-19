import time
import os
import requests
import json
import valve.source
import valve.source.a2s
import valve.source.master_server
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
# from dotenv import load_dotenv
from requests.exceptions import HTTPError

# load_dotenv()
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
        A2s_success = True
        try:
            with valve.source.a2s.ServerQuerier(self.server_ip) as server:
                info = server.info()
                players = server.players()

        except valve.source.NoResponseError:
            print("Server {}:{} timed out!".format(*self.server_ip))
            A2s_success = False

        if A2s_success is True:
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
        else:
            print('A2s query failed')

    def fill_player_url():
        for dict in self.json_data["player_info"]:
            pass

    def init_browser(self):
        option = webdriver.ChromeOptions()
        option.add_argument("--incognito")
        browser = webdriver.Chrome(executable_path=r'C:/Program Files (x86)/Google/Chrome/Application/chromedriver.exe', chrome_options=option)
        return browser

    def close_browser(self, browser):
        browser.quit()

    def search_player_name(self, name, browser):
        '''
        fix me
        '''
        name = name.replace(" ", "+")
        browser.get(f"https://steamcommunity.com/search/users/#text={name}")
        timeout = 2
        selenium_success = True
        try:
            WebDriverWait(browser, timeout).until(EC.visibility_of_element_located((By.CLASS_NAME, 'searchPersonaName')))
        except TimeoutException:
            print("Timed out waiting for page to load")
            selenium_success = False

        if selenium_success is True:
            html = browser.page_source
            browser.get("about:blank")
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
        return "Timed out waiting for page to load"

    def get_steam_id(self, url):
        '''
        fix me
        '''
        url_list = url.split('/')
        if len(url_list[-1]) == 17 and url_list[-1].isdigit() is True:
            return url_list[-1]
        try:
            request_id = requests.get(f'http://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/?key={API_KEY}&vanityurl={url}&format=json')
        except HTTPError as http_err:
            return(f'Unable to resolve steam url into id')
        except Exception as err:
            return('Unable to resolve steam url into id')
        json_data = json.loads(request_id.content)
        if json_data['response']['success'] == '1':
            steam_id = json_data['response']['steamid']
        else:
            return('Unable to resolve steam url into id')
        return steam_id

    def fill_player_steam_info(self, steam_id):
        '''
        fix me
        '''
        steam_query_success = True
        try:
            steam_id = requests.get(f'http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={API_KEY}&steamids={steam_id}&format=json')
        except HTTPError as http_err:
            return(f'Unable to resolve steam url into id http error:{http_err}')
            steam_query_success = False
        except Exception as err:
            return('Unable to resolve steam url into id')
            steam_query_success = False
        if steam_query_success is True:
            json_data = json.loads(steam_id.content)
            avatar_url = json_data['response']['players'][0]['avatar']
            if json_data['response']['players'][0]['communityvisibilitystate'] == 1:
                profile_vis = 'hidden'
            elif json_data['response']['players'][0]['communityvisibilitystate'] == 3:
                profile_vis = 'public'
            else:
                profile_vis = 'not found'
            return (avatar_url, profile_vis)
        return ("unable to query Api", "unable to query Api")

    def print_json(self):
        '''
        fix me
        '''
        print(self.json_data)

# query = SteamQuery(('45.121.209.68', 26015), 1)
# browser = query.init_browser()
# print(query.search_player_name("(DoW)+WilboWD40", browser))
# query.rate_limit()
# print(query.search_player_name("About_30_ninjas", browser))
# query.close_browser(browser)
# print(query.get_steam_id("DarkyBenny"))
# print(query.fill_player_steam_info("76561198151637619"))
# query.init_json()
# query.get_A2s()
# query.print_json()
