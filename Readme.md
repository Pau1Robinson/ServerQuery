# ServerQuery

Server query is a flask web the uses steam server queries, web scraping and steam api queries to get and present information on a steam server to the user.

## Requirements

- flask 
- requests
- python-valve
- bs4
- selenium
- Flask-WTF

## Webpages

### / and /index

At the /index page of the app two text boxes will appear with asking for a server ip and port.  To query a steam server the user must enter the server IP and the servers steam query port. The steam query port is different from the game port.

![img](./docs/index_help.png)

For example IP 176.57.135.17 and port 28215 will query the server Official server #1974 PvP - g-portal.us.

![query_img](./docs/query_help.png)

As server query web scrapes and makes api calls to get the player info it will dynamically serve the player info to the page.  Be aware that the steam search for the player name that server query may not be able to find that players steam info. The are multiple players with that players name or the search doesn't find that player a  message saying so will show instead.

## Api

To use the Server query api make a get request to the route /api/server_ip:server_port/. The server query api unlike the webpages will return all the server data in one go as json data. If the server has a high number of players server query make take a few minutes to return the get request.



