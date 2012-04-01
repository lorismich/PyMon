import os
import string
import threading
import time
import socket

class Pymon:
	_output = ""
	_message = ""
	_verbose = False
	_remote = False
	_usersNumber = 0
	_usersNames = ""
	_processTotal = 0
	_systemUptime = ""
	_systemLoad = ""
	_systemName = ""
	_threadListen = None
	_threadRequestStop = False
	_connectionSocket = None
	_tcpHost = None
	_tcpPort = None

	def __init__(self, output = "default", verbose = False, remote = False, host = "127.0.0.1", port = 8899 ):	
		self.print_ln("Starting monitoring...")
		self._tcpHost = host
		self._tcpPort = port
		self._output = output
		self._verbose = verbose
		self._remote = remote
		self.refresh()
	
	def refresh(self):
		self.resetResult()
		self.get_user()
		self.get_total_process()
		self.get_uptime()
		self.get_hostname()
		
	def resetResult(self):
		self._usersNumber = 0
		self._usersNames = ""
		self._processTotal = 0
		self._systemUptime = ""
		self._systemLoad = ""
		self._systemName = ""
		
	def __str__(self):
		if self._output == "xml":
			return "ciao"
		else:
			# Default results style
			string = "\n\tPyMon 0.1a - Easy Linux Server Monitoring\n \
\t Author: Loris Mich <loris@lorismich.it> \n \
\t Web Site: www.lorismich.it \n"
			string += "\n\t System Load: \t%s \n\t Uptime: \t%s \n\t Hostname: \t%s \n\t Users: \t%s \n\t Process: \t%s \n\n %s" % (self._systemLoad, self._systemUptime, self._systemName, self._usersNames, self._processTotal, self._message)
			return string
	
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
			error = "Could not find users - %s" % e
			self.putMessage(error)

	def putMessage(self, message):
		self._message = message
		self.printResults()
		
	def get_total_process(self):
		try:
			self.print_ln("Getting total process...")
			# @Source example: 160
			process = os.popen("ps -A | wc -l")	
			process = process.readlines()[0].rstrip()
			self._processTotal = process
		except Exception as e:
			error = "Could not count the process - %s" % e 
			self.putMessage(error)
		
	def get_uptime(self):
		self.print_ln("Getting uptime...")
		try:
			uptime = os.popen("uptime")
			uptime = uptime.readlines()[0]
			# Remove ,
			uptime = uptime.replace(',', '')
			uptime = string.split(uptime)
			# If the uptime contains minutes and hours
			# @Source example: 04:10:11 up 1 day, 21:14,  2 users,  load average: 0.02, 0.58, 0.69
			if len(uptime) is 12:
				# Get up time
				self._systemUptime += uptime[2] + ' ' + uptime[3] + ' day and ' + uptime[4] + ' hours'
				# Get system load
				self._systemLoad += uptime[9] + ', ' + uptime[10] + ', ' + uptime[11]
			# If the uptime containd only minutes
			# @Source example: 06:00:53 up 26 min,  1 user,  load average: 0.19, 0.21, 0.27
			elif len(uptime) is 11:
			# Get up time
				self._systemUptime += uptime[2] + ' minute'
				# Get system load
				self._systemLoad += uptime[8] + ', ' + uptime[9] + ', ' + uptime[10]				
			# If the uptime containd only hours
			# @Source example: 04:10:11 up 21:14,  2 users,  load average: 0.02, 0.58, 0.69
			elif len(uptime) is 10:
			# Get up time
				self._systemUptime += uptime[2] + ' hours'
				# Get system load
				self._systemLoad += uptime[7] + ', ' + uptime[8] + ', ' + uptime[9]			
		except Exception as e:
			error = "Could not find the uptime - " + e
			self.putMessage(error)
		
	def get_hostname(self):
		try:
			self.print_ln("Getting hostname...")
			# @Source example: ubuntu-server
			hostname = os.popen("hostname")
			hostname = hostname.readlines()[0][:-1]
			self._systemName = hostname
		except Exception as e:
			error = "Could not get hostname"
			self.putMessage(error)
	
	def listen(self):
		self.putMessage("Listening on port %s ..." % self._tcpPort)
		self._threadListen = threading.Thread(target=self.listen_connection)
		self._threadListen.start()
		
	def stop(self):
		if self._remote is True:
			self.putMessage("Closing connection thread...")
			self._threadRequestStop = True
			while self._threadListen.isAlive():
				continue
			self._connectionSocket.close()
		self._message = "See you..."
		self.printResults()
			
	def listen_connection(self):
		# Start listen TCP connection
		self._connectionSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self._connectionSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self._connectionSocket.bind((self._tcpHost, self._tcpPort))
		self._connectionSocket.listen(1)
		self._connectionSocket.settimeout(10)
	
		while self._threadRequestStop is False:
			try:
				data = ""
				conn, addr = self._connectionSocket.accept()
				data = conn.recv(1024)
				self.putMessage("Connection accepted at %s on port %s" % (addr[0], addr[1]))
				# Check auth key
					# TODO
				# Send data TODO
				conn.send(self.__str__())
				conn.close()  	
			except:
				continue
				
	def printResults(self):
		# Refresh data
		self.refresh()
		# Clean the console
		os.system("clear")
		# If verbose, print results
		if self._verbose is not False: 	
			print " [*] Results: "
		print self
		
	def print_ln(self, str):
			if self._verbose is not False:
				print " [*] %s" % str
