import os
import requests
from flask import Flask
from flask import render_template, stream_with_context, request, Response
from classes import query_class
from flask import jsonify

app = Flask(__name__)

@app.route('/api/<server_ip>/', methods=["GET"])
def api(server_ip):
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

@app.route('/query/<server_ip>/')
def query(server_ip):
    def generate():
        query = query_class.SteamQuery((server_ip, 28215), 1)
        query.init_json()
        query.get_A2s()
        yield render_template('query.html', title=server_ip, query=query.json_data)
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
            player_data = query.json_data['player_info'][player]
            yield render_template('player.html', player=player, player_data=player_data)
        query.close_browser(browser)
    return Response(stream_with_context(generate()))
