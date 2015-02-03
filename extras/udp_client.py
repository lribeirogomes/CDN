import socket
import sys
HOST = 'localhost'
PORT = 58060
 
try :
    s = socket.socket( socket.AF_INET , socket.SOCK_DGRAM )
except socket.error, msg :
	print ( 'Error [' + str(msg[0]) + ']: ' + msg[1] )
	sys.exit()
print ( 'Socket Created' )

while ( 1 ) :
	msg = raw_input( '[' + HOST + '] <- Client : ' )
     
	try :
		s.sendto(msg, (HOST, PORT))
	except socket.error, msg :
		print ( 'Error [' + str(msg[0]) + ']: ' + msg[1] )
		sys.exit()

	reply, addr = s.recvfrom( 1024 )
	print ( '[' + HOST + '] -> Client : ' + reply.strip() )
