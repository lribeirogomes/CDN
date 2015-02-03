import socket
import sys
from thread import *
HOST = ''
PORT = 59000

try:
	s = socket.socket( socket.AF_INET , socket.SOCK_STREAM )
except socket.error, msg :
	print ( 'Error [' + str( msg[ 0 ] ) + ']: ' + msg[ 1 ] )
	sys.exit()
print ( 'Socket Created' )
try :
	s.bind( ( HOST , PORT ) )
except socket.error, msg :
	print ( 'Error [' + str( msg[ 0 ] ) + ']: ' + msg[ 1 ] )
	sys.exit()
print ( 'Socket Binded' )

s.listen( 10 )
print ( 'Socket Listening' )

def client( conn , addr ):
	conn.send( 'Welcome to the server. Type something and hit enter' )
	
	while( 1 ) :
		data = conn.recv( 1024 )
		print ( '[' + addr[ 0 ] + ':' + str(addr[ 1 ]) + '] -> Server : ' + data )
		if not data: 
			break
		msg = raw_input ()
		conn.sendall( msg )
		print ( '[' + addr[ 0 ] + ':' + str(addr[ 1 ]) + '] <- Server : ' + msg )
	conn.close()

while( 1 ) :
	conn, addr = s.accept()
	print '[' + addr[ 0 ] + ':' + str(addr[ 1 ]) + '] Connected'
	start_new_thread( client , (conn,addr, ) )
