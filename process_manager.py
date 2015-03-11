#! /usr/bin/env python

import daemon_main
import sys


while 1:
	try:
		if len(sys.argv) >= 2:
			plimmer_id = sys.argv[1]
		else:
			print "No plimmer ID provided"
			sys.exit(-1)	
		
		print "Program manager starting for", plimmer_id
		daemon_main.daemon_main(plimmer_id)

	except:
		print "Exception caught, Restarting for ", plimmer_id
		pass
	else:
		print "Exitinf the process_manager"
		break
