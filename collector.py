#! /usr/bin/env python

import sys
import sys
sys.path.append('/mnt/sda1/libraries/requests')
sys.path.append('/mnt/sda1/libraries/websocket')

import sqlite3 as sql
import requests
import time


sys.path.insert(0, '/usr/lib/python2.7/bridge/')                                          
from bridgeclient import BridgeClient as bridgeclient




def bridge_client():
	value = bridgeclient()
	try:
		stat1 = value.get('stato1').split('/')
		stat1[-1] = stat1[-1].replace('|', '')
		stat2 = value.get('stato2').split('/')
		stat2[-1] = stat2[-1].replace('|', '')
		stat3 = value.get('stato3').split('/')
		stat3[-1] = stat3[-1].replace('|', '')
	except:
		raise
	
	bridge_dict = dict()
	bridge_dict['status'] = stat1[9]
	bridge_dict['current_phase'] = stat1[8]
	bridge_dict['total_time_phase'] = stat2[3]
	bridge_dict['remaining_time_phase'] = stat2[4]
	if bridge_dict['current_phase'] in [22, 23, 24, 25, 26, 27]:
		bridge_dict['total_time_phase'] = bridge_dict['total_time_phase']*10
		bridge_dict['remaining_time_phase'] = bridge_dict['remaining_time_phase']*10
	bridge_dict['elapsed_time_phase'] = str(int(bridge_dict['total_time_phase']) - int(bridge_dict['remaining_time_phase']))
	bridge_dict['flusso'] = str(int(stat3[5])*256+int(stat3[4]))
	bridge_dict['pressione'] = str(int(stat3[9])*256+int(stat3[8])/100)
	
	return bridge_dict




def sql_client(database='/www/user/data.db'):
	conn = sql.connect(database)
	conn.text_factory = str
	cursor = conn.cursor()
	sql_dict = dict()
	
		
	comm = "SELECT name, value FROM 'vars' WHERE name IN ('ca_container_volume', 'ca', 'remaining_ca', 'ca_qty', 'water_hardness', 'self_maintenance_time')"
	cursor.execute(comm)
	
	for key, value in cursor.fetchall():
		sql_dict[key] = value	

	return sql_dict






def diff_dict(old_dict, new_dict):
	
	if old_dict == {}:
		return new_dict
	
	retdict = dict()
	for key in old_dict.viewkeys():
		if key == 'plimmer_id':
			retdict['plimmer_id'] = old_dict['plimmer_id']
		else:
			if old_dict[key] != new_dict[key]:
				retdict[key] = new_dict[key]		
	
	return retdict



def main_thread(cookies, plimmer_id, database, update_url):
	cookies_dict = {cookies.name:cookies.value}
	old_dict = dict()
	
	while 1:
		try:
			bridge_dict = bridge_client()
			sql_dict = sql_client(database)
			
			update_dict = dict()
			update_dict['plimmer_id'] = plimmer_id
			update_dict['phase'] = bridge_dict['current_phase']
			update_dict['flow'] = bridge_dict['flusso']
			update_dict['pressure'] = bridge_dict['pressione']
			length = len(sql_dict['self_maintenance_time'].split(','))
			update_dict['remaining'] = str(int(sql_dict['remaining_ca'])/(int(sql_dict['ca_qty'])*length))
			update_dict['tank_volume'] = str(int(sql_dict['ca_container_volume'])/1000)
			update_dict['current_time'] = time.strftime("%H:%M:%S")
			update_dict['current_date'] = time.strftime("%d/%m/%Y")
			update_dict['maintainence_schedule'] = sql_dict['self_maintenance_time']
			update_dict['water_hardness'] = sql_dict['water_hardness']
			
			post_dict = diff_dict(old_dict, update_dict)
			old_dict = update_dict
			print post_dict
			server_post = requests.post(update_url, cookies = cookies_dict, data=update_dict)
			print server_post.text
				
			time.sleep(10)
		except:
			raise

			
			
	

	
if __name__ == "__main__":
	print bridge_client()
	print sql_client()
