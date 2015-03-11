#! /usr/bin/env python

import daemon_main



while 1:
	try:
		daemon_main.daemon_main()
	except:
		print "Exception caught, Restarting"
		pass
	else:
		print "Exitinf the process_manager"
		break
