import socket
import sys
HOST = ''
PORT = 58000

try :
	s = socket.socket( socket.AF_INET , socket.SOCK_DGRAM )	
except socket.error, msg :
	print ( 'Error [' + str(msg[0]) + ']: ' + msg[1] )
	sys.exit()
print ( 'Socket Created' )
try :
	s.bind( ( HOST , PORT ) )
except socket.error, msg :
	print ( 'Error [' + str(msg[0]) + ']: ' + msg[1] )
	sys.exit()
print ( 'Socket Binded' )

while ( 1 ) :
	data, addr = s.recvfrom( 1024 )
	if not data:
		break
	print ( '[' + addr[ 0 ] + ':' + str( addr[ 1 ] ) + '] -> Server : ' + data.strip() )
	msg = raw_input( '[' + addr[ 0 ] + ':' + str( addr[ 1 ] ) + '] <- Server : ' )
	s.sendto( msg , addr )
s.close
