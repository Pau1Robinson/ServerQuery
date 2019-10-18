import os
import requests
from flask import Flask
from classes import query_class
from flask import jsonify

app = Flask(__name__)

@app.route('/api/<server_ip>/', methods=["GET"])
def index(server_ip):
    query = query_class.SteamQuery((server_ip, 28215), 1)
    query.init_json()
    query.get_A2s()
    browser = query.init_browser()
    for player in query.json_data['player_info']:
        query.rate_limit()
        player_url = query.search_player_name(player, browser)
        query.rate_limit()
        player_steam_id = query.get_steam_id(player_url)
        query.json_data['player_info'][player]['steam_id'] = player_steam_id
        query.json_data['player_info'][player]['profile_url'] = player_url
        if player_steam_id != "Unable to resolve steam url into id":
            steam_query_data = query.fill_player_steam_info(player_steam_id)
            query.json_data['player_info'][player]['avatar_url'] = steam_query_data[0]
            query.json_data['player_info'][player]['profile_vis'] = steam_query_data[1]
    query.close_browser(browser)
    return jsonify(query.json_data)
