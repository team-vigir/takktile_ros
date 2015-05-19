import socket
import os
import sys
import stat

sock_addr = "/tmp/takk_reset"
shutdown_val = -1.0

def init_srv():
	global sock_addr
	
	# Remove pre-existing file if exists
	try:
	    os.unlink(sock_addr)
	except OSError:
	    if os.path.exists(sock_addr):
	    	rospy.logerr("Cannot remove previous comm socket at " + common_consts.sock_addr)
	    	sys.exit(1)

	# Create the unix datagram socket
	sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
	sock.bind(sock_addr)
	os.chmod(sock_addr, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
	return sock

def init_cli():
	global sock_addr
	sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)

	return sock

def wait_for_msg(srv):
	msg, addr = srv.recvfrom(100)
	val = float(msg)
	if is_shutdown_val(val):
		return None

	return float(msg)

def send_msg(duration, cli):
	global sock_addr
	msg = str(duration)
	if len(msg) > 100:
		msg = msg[:100]
	
	try:
		cli.sendto(msg, sock_addr)
	except:
		print "Error sending client duration message."
		sys.exit(1)

def send_shutdown(cli):
	global shutdown_val
	send_msg(shutdown_val, cli)

def is_shutdown_val(msg):
	global shutdown_val
	if msg == shutdown_val:
		return True
	return False

def shutdown(comm):
	comm.shutdown()
