#########################################################################
#                                                                       #
# Name        : SS.py                                                   #
#                                                                       #
# Authors     : 72904 - Luis Filipe Pookatham Ribeiro Gomes             #
#               75657 - Paulo Jorge Louseiro Gouveia                    #
#               75694 - Daniel Machado de Castro Figueira               #
#									               		                #
# Description : Delivery Network's Storage Server Component             #
#                                                                       #
#########################################################################
#Libraries
import socket
import sys
import os


########################################################################
#UPS: Receive file from Central Server                                 #
########################################################################
def UPS(conn, addr, args):
	print('Storage Server <- Central Server: UPS')
	
	#Check if reply follows protocol
	args = args.split(' ', 2)
	if not(len(args) == 3 and args[1].isdigit() == True and args[1] != '0'):
		print('Storage Server -> Central Server: ERR')
		conn.sendall('ERR\n')
		return
	
	#Receive file
	file_name = args[0]
	file_size, file_recv = int(args[1]), len(args[2])
	while file_recv < file_size + 1:
		new = conn.recv(1024)
		args[2] = args[2] + new
		file_recv = file_recv + len(new)
		
	#Check if reply follows protocol
	if not(args[2].endswith('\n')):
		print('Storage Server -> Central Server: ERR')
		conn.sendall('ERR\n')
		return
	file_data = args[2].strip('\n')

	#Write data on file
	try:
		file = open(file_name, 'wb')
		file.write(file_data)
		file.close()
	except IOError, msg:
		print('Storage Server -> Central Server: AWS nok')
		conn.sendall('AWS nok\n')
		return

	print('Storage Server -> Central Server: AWS ok')
	conn.sendall('AWS ok\n')


########################################################################
#REQ: Send requested file to Client                                    #
########################################################################
def REQ(conn, addr, args):
	print('Storage Server <- ' + addr[0] + ':' + str(addr[1]) + ': REQ ' + args.strip('\n'))	
	
	#Check if reply follows protocol
	args = args.split(' ')		
	if len(args) == 1 and args[0].endswith('\n') == True:
		file_name = args[0].strip()
		
		#Check if file exists
		if os.path.exists(file_name):
			file_size = os.path.getsize(file_name)
			
			#Send file
			file = open(file_name, 'rb')
			conn.sendall('REP ok ' + str(file_size) + ' ' + file.read(file_size) + '\n')
			print('Storage Server -> ' + addr[0] + ':' + str(addr[1]) + ': File sent.')
			file.close()
		
		else:
			print('Storage Server -> ' + addr[0] + ':' + str(addr[1]) + ': ' + file_name + ' doesn\'t exist!')
			conn.send('REP nok\n')
					
	else:
		print('Protocol Violation!')
		conn.send('ERR\n')
	
	return


########################################################################
#TCP: Initialize TCP socket                                           #
########################################################################
def TCP():
	try:
		#Create TCP Socket and connect
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	except Exception, msg:
		EXT(msg)
	
	try:
		#Bind socket
		s.bind((HOST, PORT))
		s.listen(10)
		print('Storage Server: Ready!')
		
		while True:
			#Accept new client
			conn, addr = s.accept()

			#Receive command
			cmd = conn.recv(1024)
			cmd = cmd.split(' ', 1)

			#Check if reply follows protocol
			if cmd[0] != 'REQ' and cmd[0] != 'UPS':
				print('Storage Server: Protocol Violation!')
				continue

			#Perform action
			newpid = os.fork()
			if newpid == 0:
				#Identify client
				if cmd[0] == 'REQ' and len(cmd) == 2:   REQ(conn, addr, cmd[1])
				elif cmd[0] == 'UPS' and len(cmd) == 2: UPS(conn, addr, cmd[1])
				sys.exit()

			else:
				continue
	
	except Exception, msg:
		s.close()
		EXT(msg)
		
	except KeyboardInterrupt:
		s.close()
		EXT('Exited with Keyboard Interruption.')


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

#Create global variables
HOST, PORT = '', 59000

#Evaluate arguments
argc = len(sys.argv)
for n in range(1,argc):
	if sys.argv[n] == '-p' and n + 1 < argc:
		PORT = int(sys.argv[n+1])

#Welcome Menu
os.system('clear')
print('+-----------------------------------+\n| Welcome to Group 60\'s RC project. |\n+-----------------------------------+\n')

TCP()
