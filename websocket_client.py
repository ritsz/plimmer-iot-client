#! /usr/bin/env python

import websocket
import json 
import requests



local_server = 'http://127.0.0.1/'
status_file = '/mnt/sda1/plimmer_client/kennethreitz-requests-14b653a/status.txt'


def main_thread(cookies, plimmer_id, ws_url, server_post_url):
	
	cookies_dict = {cookies.name:cookies.value}
	ws = websocket.WebSocket()
	ws.connect(ws_url, cookie=cookies)
	#ws = websocket.create_connection(ws_url, cookie=cookies)
	
	
	while 1:
		try:
			command = ws.recv()
			command_dict = json.loads(command)
			page = command_dict['requested.page']
			print local_server+page
			
			
			if command_dict['request.method'] == 'GET':
				status = requests.get(local_server+page)
				fd = open(status_file, 'w')
				fd.write(status.text)
				fd.close() 
				
				
				response_data = {'plimmer_id':plimmer_id}
				response_files = {'response_file': open(status_file, 'r')}
				server_post = requests.post(server_post_url, cookies = cookies_dict, files=response_files, data=response_data)
			else:
				payload = command_dict['request.POST']
				local_post = requests.post(local_server, data=payload)
				print "Local POST done", dir(local_post), local_post.text
				fd = open(status_file, 'w')
				fd.write(str(local_post.text))
				fd.close()
				
				response_data = {'plimmer_id':plimmer_id}
				response_files = {'response_file': open(status_file, 'r')}
				server_post = requests.post(server_post_url, cookies = cookies_dict, files=response_files, data=response_data)
			
		except websocket._exceptions.WebSocketConnectionClosedException():
			print "THE ERROR IS AT WEBSOCKET"
			ws = websocket.create_connection(ws_url, cookie=cookies)
			pass
			 
			 
