# ServerQuery

## Outline

ServerQuery is a web application that uses a algorithmic solution to collect information about a steam game server and the players on that server using the steam framework. ServerQuery collects information using two way communication over the internet through multiple methods using flask, steam server queries, the steam api and web scraping. ServerQuery will request an IP address of a steam server from the user, gather information about the server and players, then enable the user and to query that information about from a flask api or display that information to the from a webpage served to the user from flask.

## Building steam data

ServerQuery will take input from the user in the form of post requests to a flask api or the flaskWTF forms on the web page. This input will be the IP address of the server the user wants ServerQuery to get information on.

To build information about a steam server ServerQuery will first take that IP and query the server using a python library called python-valve that uses the steam A2s server query protocol.  By querying the server, ServerQuery  will get the server name, steam game the server is running, the map the server is running, the region the server is in, the server types, the current and max player count and a list of player information.  The player information will have the names of each player.

ServerQuery then will try to gain more information about the players on that server from the steam api. To make requests to the steam api about a player the api needs the players steam id. Unfortunately the steam server query doesn't return the players steam id so to try to get the steam id ServerQuery will web scrap the steam community user search page using selenium to get the html with the search results and beautiful soup to look for matches.  After web scraping the page will look for a unique user that matches the player name and will get their profile URL. ServerQuery can then get the users steam id from querying the steam api with the users profile URL.

ServerQuery will then query the steam api using flask with the players steam id to get their avatar, visibility of their profile and their profile page. Accessing the steam api is done through flask Get requests and using a steam api key and a players steam id. ServerQuery will be structured using object oriented programing to create a class to handle the all steam query's as json object and contain methods for rate limiting and updating the data.  The server query's, web scraping and steam api query's will be methods  of the steam query class.

## Outputting Data through an api

The user will be able to get the results of the steam query's from ServerQuery either from using get requests that ServerQuery will respond to through flask to output the .json data that the steam query class will create. The user can also access the web page that will be served with flask, using flaskWTF for web forms and a html generator to server the webpage.
