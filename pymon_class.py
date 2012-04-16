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
	_kernelRelease = ""
	_kernelVersion = ""
	_diskUsage = ""
	_threadListen = None
	_threadRequestStop = False
	_connectionSocket = None
	_tcpHost = None
	_tcpPort = None
	_networkInformation = ""

	def __init__(self, output = "default", verbose = False, remote = False, host = "127.0.0.1", port = 8899 ):	
		self._tcpHost = host
		self._tcpPort = port
		self._output = output
		self._verbose = verbose
		self._remote = remote
		self.print_ln("Starting monitoring...")
	
	def refresh(self):
		self.resetResult()
		self.get_systemInfo()
		self.get_networkInfo()
		self.get_diskUsage()
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
			# Top label
			string = "\n\tPyMon 0.1a - Easy Linux Server Monitoring\n \
\t Author: Loris Mich <loris@lorismich.it> \n \
\t Web Site: www.lorismich.it \n\n"
			# Basic informations
			string += "\tGeneral Informations: \n\n\t\tSystem Load: \t%s \n\t\tUptime: \t%s \n\t\tHostname: \t%s \n\t\tKernel: \t%s \n\t\tRelease: \t%s \n\t\tUsers: \t\t%s \n\t\tProcess: \t%s" % (self._systemLoad, self._systemUptime, self._systemName, self._kernelRelease, self._kernelVersion, self._usersNames, self._processTotal)
			# Disk informations
			string += "\n\n\t Disk Informations: \n\n\t\tFile system\tDim.\tUsati\tDisp.\tUso\tMontato su\n %s" % (self._diskUsage)
			# Network Informations
			string += "\n\n\t Network Informations: \n\n\t\tInterface\tRX\t\tTX\n %s" % (self._networkInformation)
			# Footer
			string += "\n\n %s \n\n" % self._message
			string += "Press Ctrl + C to quit"
			return string
	
	def putMessage(self, message):
		self._message = message
		self.printResults()
		
	def get_diskUsage(self):
		try:
			self.print_ln("Getting disk information...")
			system = os.popen("df -H")
			system = system.readlines()
			# Remove first line
			system = system[1:]
			# Reset string
			self._diskUsage = ""
			# @Source example (one line): /dev/sda2 41G 36G 2,5G 94% /
			for line in system:
				line = line.split()
				# Check file system string lenght
				if len(line[0]) < 8:
					line[0] += '\t'
				self._diskUsage += '\t\t' + line[0] + '\t' + line[1] + '\t' + line[2] + '\t' + line[3] + '\t ' + line[4] + '\t' + line[5] + '\n'
				
		except Exception as e:
			error = "Could not get disk informations - %s" % e
			self.putMessage(error)	
	
	def convert_bytes(self, bytes):
		bytes = float(bytes)
		if bytes >= 1099511627776:
		    terabytes = bytes / 1099511627776
		    size = '%.2fTB' % terabytes
		elif bytes >= 1073741824:
		    gigabytes = bytes / 1073741824
		    size = '%.2fGB' % gigabytes
		elif bytes >= 1048576:
		    megabytes = bytes / 1048576
		    size = '%.2fMB' % megabytes
		elif bytes >= 1024:
		    kilobytes = bytes / 1024
		    size = '%.2fKB' % kilobytes
		else:
		    size = '%.2fb' % bytes
		return size
		
	def get_networkInfo(self):
		try:
			self.print_ln("Getting network information...")
			system = os.popen("netstat -i");
			self._networkInformation = ""
			system = system.readlines()
			# Remove first and second lines
			system = system[2:]
			for line in system:
				line = line.split()
				# Total data trasmit and recived
				rx = self.convert_bytes(int(line[1])*int(line[3]))
				tx = self.convert_bytes(int(line[1])*int(line[7]))
				# Check rx string lenght
				if len(rx) < 8:
					rx += '\t'
				if len(tx) < 8:
					tx += '\t'	
				self._networkInformation += '\t\t' + line[0] + '\t\t'+ rx + '\t' + tx + '\n'
		except Exception as e:
			error = "Could not network informations - %s" % e
			self.putMessage(error)	
		
	def get_systemInfo(self):
		try:
			self.print_ln("Getting system information...")
			# @Source example: Linux d4ng3r-laptop 3.0.0-16-generic #28-Ubuntu SMP Fri Jan 27 17:50:54 UTC 2012 i686 i686 i386 GNU/Linux
			system = os.popen("uname -a")
			system = system.readlines()[0]
			system = string.split(system)
			# Kernel release
			self._kernelRelease = system[2]
			# Kernel version
			self._kernelVersion = system[7] + ' ' + system[6] + ' ' + system[10]		 	
		except Exception as e:
			error = "Could not get system informations - %s" % e
			self.putMessage(error)
	
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
		time.sleep(1)
			
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
