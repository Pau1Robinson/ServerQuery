'''
Handles the flask routes and main logic for server query.
In the /index route uses flask wtf forms to allow the user to enter a server ip and port number
then redirects the user to the /query route with the ip and port the user entered.
In the /query route using the SteamQuery class generates and serves a html page with the server
info and player info of the server the user entered the info of.
'''

import os
import requests
from selenium import webdriver
from flask import Flask
from flask import render_template, flash, redirect, stream_with_context, request, Response, jsonify
from app import query_class
from app.forms import QueryForm
from config import Config

APP = Flask(__name__)
APP.config.from_object(Config)

@APP.route('/', methods=['GET', 'POST'])
@APP.route('/index', methods=['GET', 'POST'])
def index():
    '''
    Handles the route for the index page.\n
    Serves the html and handles the requests for the flask wtf forms\n
    on the index page used to input the server ip and port.
    '''
    form = QueryForm()
    if form.validate_on_submit():
        return redirect(f'/query/{form.server_ip.data}:{form.server_port.data}/')
    return render_template('form.html', form=form)

@APP.route('/api/<server_info>/', methods=["GET"])
def api(server_info):
    '''
    Handles api requests to server query.\n
    Uses the SteamQuery class to create a json object to hold api data.\n
    Then uses the methods for a2s queries, searching player names\n
    and quering the steam api to fill the json object.
    '''
    query = query_class.SteamQuery(server_info, 1)
    query.init_json()
    query.get_a2s()
    browser = init_browser()
    for player in query.json_data['player_info']:
        query.search_player_name(player, browser)
        query.get_steam_id(player)
        if query.json_data['player_info'][player]['steam_id'] != "Unable to resolve steam url into id":
            query.fill_player_steam_info(player)
    browser.quit()
    return jsonify(query.json_data)

@APP.route('/query/<server_info>/')
def server_query(server_info):
    '''
    Handles the webpage for returning a server query from the index page by using a html generator.
    '''
    def generate():
        '''
        Generates and serves the html for the query page using the SteamQuery class.\n
        Uses the query class to create a json object to store player data.\n
        Then uses the methods for a2s queries, player name search and steam api requests to fill the json object.\n
        Then serves the json to fulfil the api GET request.
        '''
        query = query_class.SteamQuery(server_info, 1)
        query.init_json()
        query.get_a2s()
        yield render_template('query.html', title=server_info, query=query.json_data)
        browser = init_browser()
        for player in query.json_data['player_info']:
            query.search_player_name(player, browser)
            query.get_steam_id(player)
            if query.json_data['player_info'][player]['steam_id'] != "Unable to resolve steam url into id":
                query.fill_player_steam_info(player)
            player_data = query.json_data['player_info'][player]
            yield render_template('player.html', player=player, player_data=player_data)
        browser.quit()
    return Response(stream_with_context(generate()))

def init_browser():
    '''
    Initialises the browser for the selenium web scraper in the search player name method.
    '''
    option = webdriver.ChromeOptions()
    option.add_argument("--incognito")
    path = r'C:/Program Files (x86)/Google/Chrome/Application/chromedriver.exe'
    browser = webdriver.Chrome(executable_path=path, chrome_options=option)
    return browser
