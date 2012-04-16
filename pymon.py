#!/usr/bin/python

import time
import os
import string
import socket
import threading
from pymon_class import *
from optparse import OptionParser

pymon = None

def shutdown():
	# Close active connection
	if pymon is not None:
		pymon.stop()
			
try:
	parser = OptionParser( usage = "usage: %prog [options]", description="PyMon 0.1a - Easy Linux Server Monitoring\nAuthor: Loris Mich <loris@lorimich.it> \n\n" )
	parser.add_option( "-c", "--continue", action="store_true", default=False, dest="continue_read", help="Continue reading." );
	parser.add_option( "-r", "--remote", action="store_true", default=False, dest="remote", help="Enable remote reading." );
	parser.add_option( "-p", "--port", action="store", default=8899, dest="tcp_port", help="TCP port for incoming connections. (Default: 8899)" );
	parser.add_option( "-v", "--verbose", action="store_true", default=False, dest="verbose", help="Be verbose." );
	(options, args) = parser.parse_args()

	pymon = Pymon(verbose = options.verbose, remote=options.remote, port = int(options.tcp_port))

	if options.remote is True:
		options.continue_read = True
		pymon.listen()

	if options.continue_read is True:
		while 1:
			pymon.printResults()
			time.sleep(2)
	else:
		pymon.printResults()
except KeyboardInterrupt:
	shutdown()
	pass
except Exception as error:
	shutdown()
	print "[***] Error: %s" % error 

