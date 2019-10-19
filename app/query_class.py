'''
Class for handling the Queries used by server query to build the information it returns.
'''

import time
import os
import json
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
from requests.exceptions import HTTPError

API_KEY = os.getenv("API_KEY")

class SteamQuery():
    '''
    Handles and acquires the data to be returned by Server query.
    Creates a json object to hold the data then fills it using requests
    from a2s, web scraping and the steam api.

    server_info: the ip and port of the server to be queried as a string.
    server_ip: the ip of the server to be queried as a string.
    server_port: the port of the server to be queried as a integer.
    rate: the rate limit used for api requests and web scraping as a integer.
    last_limited: the time for the last time rate_limit waited.
    json_data: the json object to store the information to be returned
    by server query as nested dictionaries.

    rate_limited: method called for rate limiting the web scraping and api calls
    init_json: method call to create the json_data object.
    get_a2s: method called to query the steam server using a2s protocol
    to get server info and a list of player names.
    fill_player_steam_info: uses the steam api and a players steam id to get the players
    avatar img and profile visibility.
    Search_player_name: uses selenium and beautiful soup to scrap the steam search page
    to get a players steam url from their name.
    get_steam_id:checks if the player has their steam id their url
    and try's to get it from the steam api if they don't.
    '''
    def __init__(self, server_info, rate):
        '''
        Initialises objects for SteamQuery class
        '''
        self.server_info = server_info
        self.server_ip = self.server_info.split(':')[0]
        self.server_port = int(self.server_info.split(':')[1])
        self.rate = rate
        self.last_limited = time.time()
        self.json_data = {}

    def rate_limit(self):
        '''
        Gets the current time checks if it has been called in self.rate seconds
        since it was last called in last_limited if not then waits the difference.
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
        Initialises the data_json object and creates the keys for the server info to be returned.
        '''
        info_list = self.server_info.split(':')
        self.server_ip = info_list[0]
        self.server_port = int(info_list[1])
        self.json_data = {
            "server_info":{
                "ip_address":self.server_ip,
                "port":self.server_port,
                "server_name":"",
                "server_game":"",
                "server_map":"",
                "player_count":"",
                "max_players":"",
                "server_type":"",
            },
            "player_info":{
            }
        }

    def get_a2s(self):
        '''
        Uses the python-valve library to query the server gets an object with server info and a list of player names
        then adds that to the key values of data_json.
        '''
        a2s_success = True
        try:
            with valve.source.a2s.ServerQuerier((self.server_ip, self.server_port)) as server:
                info = server.info()
                players = server.players()

        except valve.source.NoResponseError:
            print("Server {}:{} timed out!".format(*self.server_ip))
            a2s_success = False

        if a2s_success is True:
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

    def fill_player_steam_info(self, player):
        '''
        Uses the requests module to query the steam api using the players steam id to get the players avatar_url and profile_Visibility
        then add set that to the values of the player dictionary in json_data.
        '''
        self.rate_limit()
        player_request = 'http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key='
        steam_id = self.json_data['player_info'][player]['steam_id']
        steam_query_success = True
        try:
            request_info = requests.get(f'{player_request}{API_KEY}&steamids={steam_id}&format=json')
        except HTTPError as http_err:
            print(http_err)
            self.json_data['player_info'][player]['avatar_url'] = 'unable to query api'
            self.json_data['player_info'][player]['profile_vis'] = 'unable to query api'
            return
        except Exception as err:
            print(err)
            self.json_data['player_info'][player]['avatar_url'] = 'unable to query api'
            self.json_data['player_info'][player]['profile_vis'] = 'unable to query api'
            return

        if steam_query_success is True:
            json_data = json.loads(request_info.content)
            avatar_url = json_data['response']['players'][0]['avatar']
            if json_data['response']['players'][0]['communityvisibilitystate'] == 1:
                profile_vis = 'hidden'
            elif json_data['response']['players'][0]['communityvisibilitystate'] == 3:
                profile_vis = 'public'
            else:
                profile_vis = 'not found'
            self.json_data['player_info'][player]['avatar_url'] = avatar_url
            self.json_data['player_info'][player]['profile_vis'] = profile_vis
            return
        self.json_data['player_info'][player]['avatar_url'] = 'unable to query api'
        self.json_data['player_info'][player]['profile_vis'] = 'unable to query api'
        return

    def search_player_name(self, name, browser):
        '''
        Takes the player name and searches it in the steam search page retivies that with selenium.
        Then looks for the matching player names and urls with beautiful soup.
        if there is a single match adds the steam url to the value in the player dictionary in data_json.
        '''
        self.rate_limit()
        player = name
        player = player.replace(" ", "+")
        browser.get(f"https://steamcommunity.com/search/users/#text={name}")
        timeout = 2
        selenium_success = True
        try:
            WebDriverWait(
                browser, timeout
                ).until(
                    EC.visibility_of_element_located(
                        (
                            By.CLASS_NAME, 'searchPersonaName'
                        )
                    )
                )
        except TimeoutException:
            print("Timed out waiting for page to load")
            selenium_success = False

        if selenium_success is True:
            html = browser.page_source
            browser.get("about:blank")
            soup = BeautifulSoup(html, 'html.parser')
            results_row = soup.find_all('a', {'class': 'searchPersonaName'})
            results = []

            for result_row in results_row:
                steam_name = result_row.getText()
                steam_url = result_row.get('href')
                results.append({
                    "name": steam_name,
                    "steam_url": steam_url
                })

            num_match = 0
            for dict in results:
                if dict["name"] == name:
                    num_match += 1
                    match_url = dict["steam_url"]
            if num_match == 1:
                self.json_data['player_info'][name]['profile_url'] = match_url
                return
            if num_match == 0:
                self.json_data['player_info'][name]['profile_url'] = "No steam profile match found"
                return
            if num_match > 1:
                self.json_data['player_info'][name]['profile_url'] = "Steam name is too common"
                return
            self.json_data['player_info'][name]['profile_url'] = "Search timed out"
            return

    def get_steam_id(self, player):
        '''
        Check if the players steam id is in their steam url if not tries to retrieve it from the steam api
        then add it to the value in the player dictionary in json_data.
        '''
        self.rate_limit()
        url = self.json_data['player_info'][player]['profile_url']
        url_list = url.split('/')
        error_message = 'Unable to resolve steam url into id'
        string_request = 'http://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/?key='
        request_success = True
        if len(url_list[-1]) == 17 and url_list[-1].isdigit() is True:
            self.json_data['player_info'][player]['steam_id'] = url_list[-1]
            return
        try:
            request_id = requests.get(
                f'{string_request}{API_KEY}&vanityurl={url}&format=json')
        except HTTPError as http_err:
            print(http_err)
            self.json_data['player_info'][player]['steam_id'] = error_message
            request_success = False
        except Exception as err:
            print(err)
            self.json_data['player_info'][player]['steam_id'] = error_message
            request_success = False
        if request_success is True:
            request_data = json.loads(request_id.content)
            if request_data['response']['success'] == '1':
                self.json_data['player_info'][player]['steam_id'] = request_data['response']['steamid']
                return
            self.json_data['player_info'][player]['steam_id'] = error_message
            return
