#!/usr/bin/python

import time
import os
import string
from optparse import OptionParser

class Pymon:
	_output = ""
	_verbose = False
	_usersNumber = 0
	_usersNames = ""
	_processTotal = 0
	_systemUptime = ""
	_systemLoad = ""
	_systemName = ""

	def __init__(self, output = "default", verbose = False):	
		self.print_ln("Starting monitoring...")
		self._output = output
		self._verbose = verbose
		self.get_user()
		self.get_total_process()
		self.get_uptime()
		self.get_hostname()
		
	def __str__(self):
		if self._output == "xml":
			return "ciao"
		else:
			# Default results style
			return "\n\t System Load: \t%s \n\t Uptime: \t%s \n\t Hostname: \t%s \n\t Users: \t%s \n\t Process: \t%s \n" % (self._systemLoad, self._systemUptime, self._systemName, self._usersNames, self._processTotal)
	
	def get_user(self):
		try:
			self.print_ln("Getting connected users...")
			# @Source example: user1     tty6         2012-03-28 10:10 \n user2   pts/0        2012-03-28 10:10 (:0.0)
			users = os.popen("who")
			users = users.readlines()
			self._usersNumber = len(users)
			for line in users:
				self._usersNames += string.split(line)[0] + ', '
			# Remove last char
			self._usersNames = self._usersNames.rstrip()[:-1]
			# Append total users
			self._usersNames += "\t(Total: %s)" % self._usersNumber
		except Exception as e:
			raise Exception ("Could not find users")
		
	def get_total_process(self):
		try:
			self.print_ln("Getting total process...")
			# @Source example: 160
			process = os.popen("ps -A | wc -l")	
			process = process.readlines()[0].rstrip()
			self._processTotal = process
		except Exception as e:
			raise Exception ("Could not count the process")
		
	def get_uptime(self):
		self.print_ln("Getting uptime...")
		try:
			# @Source example: 04:10:11 up 1 day, 21:14,  2 users,  load average: 0.02, 0.58, 0.69
			uptime = os.popen("uptime")
			uptime = uptime.readlines()[0]
			# Remove ,
			uptime = uptime.replace(',', '')
			uptime = string.split(uptime)
			# If the system is up more than an hour
			if len(uptime) is 12:
				# Get up time
				self._systemUptime += uptime[2] + ' ' + uptime[3] + ' and ' + uptime[4] + ' hours'
				# Get system load
				self._systemLoad += uptime[9] + ', ' + uptime[10] + ', ' + uptime[11]
			# If the system is up less than an hour
			elif len(uptime) is 11:
			# Get up time
				self._systemUptime += uptime[2] + ' ' + uptime[3]
				# Get system load
				self._systemLoad += uptime[8] + ', ' + uptime[9] + ', ' + uptime[10]
		except Exception as e:
			raise Exception ("Could not find the uptime - " + e)
		
	def get_hostname(self):
		try:
			self.print_ln("Getting hostname...")
			# @Source example: ubuntu-server
			hostname = os.popen("hostname")
			hostname = hostname.readlines()[0][:-1]
			self._systemName = hostname
		except Exception as e:
			raise Exception ("Could not get hostname")
				
	def print_ln(self, str):
		if self._verbose is not False:
			print " [*] %s" % str
	
	def printResults(self):
		# If verbose, print results
		if self._verbose is not False:
			print " [*] Results: "
		print self
		
try:
	while 1:
		os.system("clear")
		print '\033[1;47m \033[1;m'
		
		print "\n\tPyMon 0.1a - Easy Linux Server Monitoring\n \
	\t Author: Loris Mich <loris@lorismich.it> \n \
	\t Web Site: www.lorismich.it \n"
	
		parser = OptionParser( usage = "usage: %prog [options]" )
		parser.add_option( "-v", "--verbose", action="store_true", default=False, dest="verbose", help="Be verbose." );
		(options, args) = parser.parse_args()

		pymon = Pymon(verbose = options.verbose)
		pymon.printResults()
		
		time.sleep(2)
except KeyboardInterrupt:
  pass
except Exception as error:
	print "[***] Error: %s" % error 

