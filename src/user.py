#########################################################################
#                                                                       #
# Name        : user.py                                                 #
#                                                                       #
# Authors     : 72904 - Luis Filipe Pookatham Ribeiro Gomes             #
#               75657 - Paulo Jorge Louseiro Gouveia                    #
#               75694 - Daniel Machado de Castro Figueira               #
#																		#
# Description : Delivery Network's User Component                       #
#                                                                       #
#########################################################################
#Libraries
import socket
import sys
import os


########################################################################
#checkReply: Check if the replies follow the protocol                  #
########################################################################
def checkReply(reply, cmd):
	
	#Error replies handler
	if reply == '':                                   print('Protocol Violation: Empty reply.')
	elif reply == 'ERR\n':                            print('Warning: ERR.')
	elif reply == 'EOF\n' and cmd == 'AWL':           print('Client <- Central Server: EOF')
	elif cmd == 'REP3':
		if not(reply.endswith('\n')):                   print('Protocol Violation: Reply doesn\'t end in \\n.')
		else: return True
	else:

		#Generic errors handler
		split = reply.split(' ',1)
		if len(split) != 2:                              print('Protocol Violation: Reply is missing arguments.')
		elif not(reply.startswith(cmd + ' ')):           print('Protocol Violation: Invalid reply.')
		elif not(reply.endswith('\n')) and cmd != 'REP': print('Protocol Violation: Reply doesn\'t end in \\n.')
		else: 

			#Specific errors handler
			if cmd == 'REP':
				args = split[1].split(' ', 2)
			else:
				args = split[1].split(' ')

			if cmd == 'AWL':

				#AWL errors handler
				if len(args) <= 3:                   print('Protocol Violation: (AWL) Invalid number of arguments.')
				elif not(args[2].isdigit()):         print('Protocol Violation: (AWL) Argument 3 should be a number.')
				elif len(args) != 3 + int(args[2]):  print('Protocol Violation: (AWL) Invalid number of files.' + str(len(args)) + ':' + args[2])
				elif int(args[2]) > 30:              print('Protocol Violation: (AWL) Too many files.')
				for i in range(1, 1 + int(args[2])):
						if len(args[2 + i]) > 20:        print('Protocol Violation: (AWL) Too long file names.')
				else:

					#AWL valid reply handler
					print('Client <- Central Server: AWL')
					return True

			elif cmd == 'AWR':

				#AWR errors handler
				if len(args) != 1:       print('Protocol Violation: (AWR) Invalid number of arguments.')
				elif args[0] == 'dup\n': print('Client <- Central Server: File already exists.')
				elif args[0] != 'new\n': print('Protocol Violation: (AWR) Invalid file status.')
				else:

					#AWR valid reply handler
					print('Client <- Central Server: AWR')
					return True
				
			elif cmd == 'AWC':

				#AWC errors handler
				if len(args) != 1:       print('Protocol Violation: (AWC) Invalid number of arguments.')
				elif args[0] == 'nok\n': print('Client <- Central Server: File not uploaded.')
				elif args[0] != 'ok\n':  print('Protocol Violation: (AWC) Invalid status.')
				else:

					#AWC valid reply handler
					print('Client <- Central Server: AWC')
					return True

			elif cmd == 'REP':

				#REP errors handler
				if args[0] == 'nok\n': 			               print('Client <- Storage Server: REP nok')
				elif len(args) != 3:                             print('Protocol Violation: (REP) Invalid number of arguments.')	
				elif args[0] != 'ok':                          print('Protocol Violation: (REP) Invalid status.')
				elif not(args[1].isdigit()) or args[1] == '0': print('Protocol Violation: (REP) Invalid file size.')
				else:

					#REP valid reply handler
					print('Client <- Storage Server: REP')
					return True
	
	return False


########################################################################
#LST: Request list of files                                            #
########################################################################
def LST():
	print('Client -> Central Server: Request list...')

	#Create UDP socket
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

	#Send list request
	s.sendto('LST\n', (cs_addr, cs_port))
	print('Client -> Central Server: LST')

	#Receive AWL reply
	reply, addr = s.recvfrom(1024)
	s.close()

	#Check AWL reply
	if not(checkReply(reply, "AWL")):
		print('Client <- Central Server: Request list... Error')
		return -1, -1

	args = reply.split(' ')
	file_list = 'SServer IP: ' + args[1] + '\nSServer Port: ' + args[2] + '\nFile List:\n'
	for i in range(1, 1 + int(args[3])): file_list = file_list + '  ' + str(i) + '. ' + args[3 + i] + '\n'
	file_list = file_list + 'Retrieve files using command "retrieve <filename>".\n'

	print(file_list + 'Client <- Central Server: Request list... Done')
	return args[1], int(args[2])

########################################################################
#UPR: Upload file to storage server                                    #
########################################################################
def UPR(file_name):
	print('Client -> Central Server: Upload ' + file_name + '...')

	#Check if file exists
	if not(os.path.exists(file_name)):
		print('File doesn\'t exist.')
		return

	#Create TCP Socket and connect to server
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.settimeout(10000)

	s.connect((cs_addr, cs_port))

	#Send upload request
	s.sendall('UPR ' + file_name + '\n')
	print('Client -> Central Server: UPR')

	#Check AWR reply
	if not(checkReply(s.recv(1024), "AWR")):
		print('Client <- Central Server: Upload ' + file_name + '... Error')
		return

	#Upload file
	file = open(file_name, 'rb')
	file_size = os.path.getsize(file_name)
	s.sendall('UPC ' + str(file_size) + ' ' + file.read(file_size) + '\n')
	reply = s.recv(1024)
	s.close()

	#Check AWC reply
	if not(checkReply(reply, "AWC")):
		print('Client <- Central Server: Upload ' + file_name + '... Error')
		return

	print('Client <- Central Server: Upload ' + file_name + '... Done')
	return


########################################################################
#REQ: Retrieve selected file                                           #
########################################################################
def REQ(file_name):
	print('Client -> Storage Server: Retrieve ' + file_name + '...')

	#Create TCP Socket and connect to server
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.settimeout(10000)
	s.connect((ss_addr, ss_port))

	#Send request message
	s.sendall('REQ ' + file_name + '\n')
	data = s.recv(1024)

	#Check REP reply
	if not(checkReply(data, 'REP')): return

	#Retrieve file
	data = data.split(' ', 3)
	file_size, data_rcv = int(data[2]), len(data[3])
	while data_rcv < file_size + 1:
		new = s.recv(1024)
		data[3] = data[3] + new
		data_rcv = data_rcv + len(new)
	s.close()

	#Check REP's 3rd argument reply
	if not(checkReply(data[3], 'REP3')): return

	#Write data on file
	file = open(file_name, 'wb')
	file.write(data[3].strip('\n'))
	file.close()

	print('Client <- Storage Server: Retrieve ' + file_name + '... Done')
	return


########################################################################
#listCommands: print list of avaiable commands                         #
########################################################################
def listCommands():
	print('\nList of instructions  :\n  list                : Get list of available files.\n  upload <filename>   : Upload selected file.')
	if ss_addr != -1: print('  retrieve <filename> : Download selected file.')
	else:             print('  retrieve <filename> : Download selected file. (available after getting list)')
	print('  exit                : Exit program.')


########################################################################
#EXT: Print error and exit                                             #
########################################################################
def EXT(msg):
	os.system('clear')
	print(str(msg)) 
	sys.exit()
	

########################################################################
#MainFunction                                                          #
########################################################################
try:
	#Create global variables
	cs_host, cs_port, ss_addr, ss_port = 'localhost', 58060, -1, -1

	#Print welcome menu
	os.system('clear')
	print('+-----------------------------------+\n| Welcome to Group 60\'s RC project. |\n+-----------------------------------+')
	listCommands()
	print('')

	#Evaluate arguments
	argc = len(sys.argv)
	for n in range(1,argc):
		if sys.argv[n] == '-n' and n + 1 < argc: cs_host = str(sys.argv[n+1])
		if sys.argv[n] == '-p' and n + 1 < argc: cs_port = int(sys.argv[n+1])

	#Get Central Server ip address
	cs_addr = socket.gethostbyname(cs_host)

	while True:		
		#Get command
		cmd = raw_input('Command: ').split()
		
		#Execute command
		if len(cmd) > 0:
			if cmd[0] == 'list' and len(cmd) == 1:       ss_addr, ss_port = LST()
			elif cmd[0] == 'upload' and len(cmd) == 2:   UPR(cmd[1])
			elif cmd[0] == 'retrieve' and len(cmd) == 2 and ss_addr != -1: REQ(cmd[1])
			elif cmd[0] == 'exit' and len(cmd) == 1:
				os.system('clear')
				sys.exit()
			else:
				print('Invalid Command.')
				listCommands()
			print('')

except Exception, msg:
	EXT(msg)
except KeyboardInterrupt:
	EXT('Exited with Keyboard Interruption.')
