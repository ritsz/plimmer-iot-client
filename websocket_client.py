#! /usr/bin/env python

import sys
sys.path.append('/mnt/sda1/libraries/requests')
sys.path.append('/mnt/sda1/libraries/websocket')
import websocket
import json 
import requests
import os.path

local_server = 'http://127.0.0.1/'
status_file = '/mnt/sda1/libraries/status.txt'
html_file  = '/mnt/sda1/libraries/html_parsed.txt'
cookie_file = '/mnt/sda1/libraries/cookie.txt'


def parse_response_file(local_file_obj, response_file_obj, r_plimmer_id):
	content_found = False
	for line in response_file_obj.__iter__():
		if not content_found:
			linkhref = line.find('href=')
			if linkhref!=-1:
				src_beg = line[linkhref:].find('"') + 1 + linkhref
				new_line = line[0:linkhref] + 'href="/tunnel/%s/' %(r_plimmer_id) + line[src_beg:].strip('/')
				local_file_obj.write(new_line)
			elif line.find('<div class="header">')!=-1 or line.find('<div class="content">')!=-1:
				content_found = True
				local_file_obj.write(line)
			else:
				pass
			continue
		if line.find('</body>')!=-1:
			break
		new_line = line
		imgsrc = line.find('src=')
		if imgsrc!=-1:
			src_beg = new_line[imgsrc:].find('"') + 1 + imgsrc
			new_line = new_line[0:imgsrc] + 'src="http://aquasphere.s3.amazonaws.com/admin/' + new_line[src_beg:].strip('/')
		linkhref = new_line.find('href=')
		if linkhref!=-1:
			src_beg = new_line[linkhref:].find('"') + 1 + linkhref
			new_line = new_line[0:linkhref] + 'href="/tunnel/%s/user/' %(r_plimmer_id) + new_line[src_beg:].strip('/')
		action = new_line.find('action=')
		if action!=-1:
			src_beg = new_line[action:].find('"') + 1 + action
			new_line = new_line[0:action] + 'action="/tunnel/%s/user/' %(r_plimmer_id) + new_line[src_beg:].strip('/')
		local_file_obj.write(new_line)
	return local_file_obj






def main_thread(cookies, plimmer_id, ws_url, server_post_url):
	
	cookies_dict = {cookies.name:cookies.value}
	ws = websocket.create_connection(ws_url, cookie=cookies)
	if ws.connected:
		print "WE ARE CONNECTED TO THE WEBSOCKET for", plimmer_id
	else:
		print "NOT CONNECTED TO WEBSOCKET"
	
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
				print status.text
				fd = open(status_file, 'w')
				fd.write(status.text)
				fd.close()
				#Adding the html parsing code here
				fd = open(status_file, 'r')				
				send_fd = open(html_file, 'w')
				parse_response_file(send_fd, fd, plimmer_id)
				send_fd.close()
				fd.close() 
				
				response_data = {'plimmer_id':plimmer_id}
				response_files = {'response_file': open(html_file, 'r')}
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
				print res_post.text
				fd.write(str(res_post.text))
				fd.close()
				#Adding the html parsing code here
				fd = open(status_file, 'r')
				send_fd = open(html_file, 'w')
				parse_response_file(send_fd, fd, plimmer_id)
				send_fd.close()
				fd.close()
				
				response_data = {'plimmer_id':plimmer_id}
				response_files = {'response_file': open(html_file, 'r')}
				server_post = requests.post(server_post_url, cookies=cookies_dict, files=response_files, data=response_data)
			
		except UnicodeEncodeError:
			print "Unicode exception"
			pass
