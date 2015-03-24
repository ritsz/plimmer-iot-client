#! /usr/bin/env python

import sys
sys.path.append('/mnt/sda1/libraries/requests')
sys.path.append('/mnt/sda1/libraries/websocket')
import websocket
import json 
import requests
import collector
import os.path

local_server = 'http://127.0.0.1/'
status_file = '/mnt/sda1/plimmer_client/kennethreitz-requests-14b653a/status.txt'
cookie_file = '/mnt/sda1/plimmer_client/kennethreitz-requests-14b653a/cookie.txt'

def main_thread(cookies, plimmer_id, ws_url, server_post_url):
	
	cookies_dict = {cookies.name:cookies.value}
	ws = websocket.WebSocket()
	ws.connect(ws_url, cookie=cookies)
	
	
	while 1:
		try:
			command = ws.recv()
			command_dict = json.loads(command)
			page = command_dict['requested.page']
			print command_dict
			print local_server+page
			if os.path.exists(cookie_file):
				local_cookie = json.load(open(cookie_file))
			else:
				local_cookie = {}
			
			
			if command_dict['request.method'] == 'GET':
				status = requests.get(local_server+page, cookies=local_cookie, params=command_dict['request.GET'])
				fd = open(status_file, 'w')
				fd.write(status.text)
				fd.close() 
				
				response_data = {'plimmer_id':plimmer_id}
				response_files = {'response_file': open(status_file, 'r')}
				server_post = requests.post(server_post_url, cookies=cookies_dict, files=response_files, data=response_data)
			
			
			else:	
				payload = command_dict['request.POST']
				if page == 'user/login.php':
					session = requests.session()
					res_post = session.post(local_server+page, payload)
					json.dump(requests.utils.dict_from_cookiejar(session.cookies), open(cookie_file, 'w'))
				else:
					res_post = requests.post(local_server+page, cookies=local_cookie, params=payload)
				
				fd = open(status_file, 'w')
				fd.write(str(res_post.text))
				fd.close()
				
				response_data = {'plimmer_id':plimmer_id}
				response_files = {'response_file': open(status_file, 'r')}
				server_post = requests.post(server_post_url, cookies=cookies_dict, files=response_files, data=response_data)
			
		except UnicodeEncodeError:
			print "Unicode exception"
			pass
