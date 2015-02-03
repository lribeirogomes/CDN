import socket
import sys
HOST = 'localhost'
PORT = 58060

try:
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket.error, msg :
	print ( 'Error [' + str(msg[0]) + ']: ' + msg[1] )
	sys.exit()
print ( 'Socket Created' )
 
try:
	addr = socket.gethostbyname( HOST )
except socket.gaierror, msg :
	print ( 'Error [' + str(msg[0]) + ']: ' + msg[1] )
	sys.exit()
print ( 'Server IP Identified' )
 
s.connect((addr , PORT))
reply = s.recv(4096)
print ( '[' +  HOST + '] Connected : ' + reply )
 
while ( 1 ) :
	msg = raw_input ( '[' + HOST + '] <- Client : ' )

	try :
		s.sendall(msg)
	except socket.error, msg :
		print ( 'Error [' + str(msg[0]) + ']: ' + msg[1] )
		sys.exit()
 
	reply = s.recv(4096)
	print ( '[' + HOST + '] -> Client : ' + reply )
