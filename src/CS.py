#########################################################################
#                                                                       #
# Name        : CS.py                                                   #
#                                                                       #
# Authors     : 72904 - Luis Filipe Pookatham Ribeiro Gomes             #
#               75657 - Paulo Jorge Louseiro Gouveia                    #
#               75694 - Daniel Machado de Castro Figueira               #
#											                         	#
# Description : Delivery Network's Central Server Component             #
#                                                                       #
#########################################################################

import socket
import sys
import os


########################################################################
#checkReply: Check if the replies follow the protocol                  #
########################################################################
def checkReply(reply, cmd):
	#Error replies handler
	if reply == '':            print('Protocol Violation: Empty reply.')
	elif reply == 'ERR\n':     print('Warning: Message from client was not correctly formulated.')
	elif cmd == 'LST':
		if reply == 'LST\n':     return True
		else:                    print('Protocol Violation: Invalid reply.')
	elif cmd == 'UPC2':
		if reply.endswith('\n'): return True
		else:                    print('Protocol Violation: Reply doesn\'t end in \\n.')
	else:

		#Generic errors handler
		split = reply.split(' ',1)
		if len(split) != 2:                              print('Protocol Violation: Reply is missing arguments.')
		elif not(reply.startswith(cmd + ' ')):           print('Protocol Violation: Invalid reply.')
		elif not(reply.endswith('\n')) and cmd != 'UPC': print('Protocol Violation: Reply doesn\'t end in \\n.')
		else: 
			#Specific errors handler
			if cmd == 'UPC':
				args = split[1].split(' ', 2)
				
			else:
				args = split[1].split(' ')

			if cmd == 'AWS':
				#AWS errors handler
				if len(args) != 1:       print('Protocol Violation: (AWS) Invalid number of arguments.')
				elif (args[0] != 'ok\n' and args[0] != 'nok\n'):  print('Protocol Violation: (AWS) Invalid status.')
				else:
					#AWS valid reply handler
					return True

			if cmd == 'UPR':
				#AWS errors handler
				if len(args) != 1:       print('Protocol Violation: (UPR) Invalid number of arguments.')
				else:
					#AWS valid reply handler
					return True

			if cmd == 'UPC':
				#REP errors handler
				if len(args) != 3:                             print('Protocol Violation: (UPC) Invalid number of arguments.')	
				elif not(args[0].isdigit()) or args[0] == '0': print('Protocol Violation: (UPC) Invalid file size.')
				else: return True

	return False


########################################################################
#UDP: Central Server UDP                                               #
########################################################################
def UDP(servers):
	#Create UDP socket
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)	

	try:
		#Bind UDP socket
		s.bind((HOST, PORT))

		print('UDP Server: Ready!')
		next_server = 0

		#UDP Loop
		while True:
			#Receive command
			cmd, addr = s.recvfrom(1024)
			
			#Perform action
			if not(checkReply(cmd, 'LST')):
				s.sendto('ERR\n', addr)
				print('Central Server -> ' + addr[0] + ':' + str(addr[1]) + ': ERR')
				continue

			print('Central Server <- ' + addr[0] + ':' + str(addr[1]) + ': LST')

			if not(os.path.exists('filelist.txt')) or os.path.getsize('filelist.txt') == 0:
				s.sendto('EOF\n', addr)
				print('Central Server -> ' + addr[0] + ':' + str(addr[1]) + ': EOF')
				continue

			#Read files from file list
			file = open('filelist.txt', 'r')
			files = ''
			n = 0
			for line in file:
				n = n + 1
				files += ' ' + line.strip('\n')
			file.close()

			#Send server info and file list to client
			s.sendto('AWL ' + servers[next_server] + ' ' + str(n) + files + '\n', addr)			
			next_server = (next_server + 1) % len(servers)

			print('Central Server -> ' + addr[0] + ':' + str(addr[1]) + ': AWL')
		
	except KeyboardInterrupt:
		s.close()
		EXT('Exited with Keyboard Interruption. (UDP)')
			

########################################################################
#UPR: Receive File from Client                                         #
########################################################################
def UPR(s, conn, addr, servers, file_name):
	#Check if file list exists
	if not(os.path.exists('filelist.txt')): file = open('filelist.txt', 'w')
	else:
		#Check if the file is in the file list
		file = open('filelist.txt', 'r')
		for line in file:
			if line.strip('\n') == file_name:
				file.close()
				print('Central Server -> ' + addr[0] + ':' + str(addr[1]) + ': File already exists.')
				conn.send('AWR dup\n')
				return -1, -1

	file.close()
	conn.send('AWR new\n')

	#Receive file
	data = conn.recv(1024)
	if not(checkReply(data, 'UPC')):
		conn.send('ERR\n')
		return -1, -1
	else:
		print('Central Server -> ' + addr[0] + ':' + str(addr[1]) + ' : Upload authorized.')

	args = data.split(' ', 2)
	file_size, file_recv = int(args[1]), len(args[2])
	while file_recv < file_size + 1:
		new = conn.recv(1024)
		args[2] = args[2] + new
		file_recv = file_recv + len(new)
	print('Central Server <- ' + addr[0] + ':' + str(addr[1]) + ': File received.')
	
	if not(checkReply(args[2], 'UPC2')):
		conn.send('ERR\n')
		return -1, -1
	file_data = args[2].strip('\n')

	return file_size, file_data


########################################################################
#UPS : Upload File to Storage Server                                   #
########################################################################
def UPS(s, conn, addr, servers, file_name, file_size, data):
	stat=0
	for i in range(0, len(servers)):
		_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			
		try:
			addr, port = servers[i].split()		
			_s.connect((addr, int(port)))

			_s.sendall('UPS ' + file_name + ' ' + str(file_size) + ' ' + data + '\n')
			print('Central Server -> ' + str(addr) + ':' + str(port) + ': File sent.')

			reply = _s.recv(1024)
			if (checkReply(reply, 'AWS') != True):
				stat=1
				print('Central Server <-  ' + addr[0] + ':' + str(addr[1]) + ' : File not uploaded.')
			else:
				print('Central Server <- ' + str(addr) + ':' + str(port) + ': File successfully uploaded.')
		
			_s.close()

		except Exception, msg:
			_s.close()
			conn.close()
			s.close()
			EXT(msg)
		except KeyboardInterrupt:
			_s.close()
			conn.close()
			s.close()
			EXT('Exited with Keyboard Interruption. (TCP)')

	print('Central Server <- ' + str(addr) + ':' + str(port) + ': ' + reply.strip('\n'))
	
	if(stat==0):
		#Add file to file list
		file = open('filelist.txt', 'a')
		file.write(file_name + '\n')
		file.close()
		conn.send('AWC ok\n')
	else:
		conn.send('AWC nok\n')
		
	
########################################################################
#TCP: Initialize TCP socket                                            #
########################################################################
def TCP(servers):
	#Create TCP socket
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	try:
		#Bind TCP socket
		s.bind((HOST, PORT))

		#Create quewe for incomming requests
		s.listen(10)
		print('TCP Server: Ready!')

		#TCP Loop
		while 1:
			#Accept new client
			conn, addr = s.accept()

			try:
				#Receive command
				cmd = conn.recv(1024)
				print('Central Server <- ' + addr[0] + ':' + str(addr[1]) + ': ' + cmd.strip('\n'))
		
				if not(checkReply(cmd, 'UPR')):
					conn.send('ERR\n')
					conn.close()
					continue
				
				#Execute command
				cmd = cmd.split(' ')
				file_name = cmd[1].strip('\n')
				file_size, file_data = UPR(s, conn, addr, servers, file_name)
				if file_size != -1:    UPS(s, conn, addr, servers, file_name, file_size, file_data)
			
			except Exception, msg:
				conn.close()
				s.close()
				EXT(msg)
			except KeyboardInterrupt:
				conn.close()
				s.close()
				EXT('Exited with Keyboard Interruption. (TCP)')

	except Exception, msg:
		s.close()
		EXT(msg)
	except KeyboardInterrupt:
		s.close()
		EXT('Exited with Keyboard Interruption. (TCP)')


########################################################################
#EXT: Print error and exit                                             #
########################################################################
def EXT(msg):
	os.system('clear')
	print(str(msg)) 
	sys.exit()


########################################################################
#Main Function                                                         #
########################################################################
try:
	#Create global variables
	HOST, PORT = '', 58060

	#Welcome Menu
	os.system('clear')
	print('+-----------------------------------+\n| Welcome to Group 60\'s RC project. |\n+-----------------------------------+\n')

	#Evaluate arguments
	argc = len(sys.argv)
	for n in range(1,argc):
		if sys.argv[n] == '-p' and n + 1 < argc: PORT = int(sys.argv[n+1])

	#Check serverfile.txt
	if not(os.path.exists('serverlist.txt')):  EXT('"serverlist.txt" doesn\'t exist.')
	if os.path.getsize('serverlist.txt') == 0: EXT('Central Server can not run without at least 1 Storage Server')

	#Choose server from server list
	servers = []
	file = open('serverlist.txt', 'r')
	for line in file: servers.append(line.strip('\n'))
	file.close()

	#Launch TCP and UDP servers
	newpid = os.fork()
	if newpid == 0: UDP(servers)
	else:           TCP(servers)

except Exception, msg:
	EXT(msg)
except KeyboardInterrupt:
	EXT('Exited with Keyboard Interruption.')
