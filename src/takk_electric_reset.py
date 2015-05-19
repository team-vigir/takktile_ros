#!/usr/bin/env python
# This code must be run with super user privileges since it touches physical hardware
# Valuable Resources: http://sourceforge.net/p/raspberry-gpio-python/wiki/BasicUsage/
#	pi pinout diagram in takktile_ros catkin branch
import sys
import os
import socket
import subprocess
import signal
import time
import usb
import rospy
import RPi.GPIO as GPIO
import gpio_comms
import takk_comms
import rospkg
from takktile_ros.msg import Touch
from std_msgs.msg import String, Empty

operator_reset_flag = False
switch_channel = 14 	 # The pin used force toggling the takktile power circuit
atmega_reset_delay = 2.5 # The amount of time needed for the atmega to become responsive after a reset

# States whether data has been received yet from takktile sensors in this check cycle
class TakkDataStatus:
	STATUS_UNINT = 0
	STATUS_ENABLED = 1
	
	def __init__(self, takktile_topic, acceptable_latency):
		self.status = self.STATUS_UNINT
		self.takktile_topic = takktile_topic
		self.takk_launch_srv = takk_comms.init_srv()
		self.last_data_time = rospy.Time.now()
		self.acceptable_takk_latency = acceptable_latency
		self.load_takk_subscriber()

	def takk_node_init_wait(self):
		takk_comms.wait_for_msg(self.takk_launch_srv)
		rospy.loginfo("Takktile_node has registered itself as active.")
		time.sleep(1) # Let it actually begin publishing
		self.status = self.STATUS_ENABLED
	
	def load_takk_subscriber(self):
		self.takk_data_sub = rospy.Subscriber(self.takktile_topic, Touch, self.takktile_data_cb)

	def takktile_data_cb(self, msg):
		#self.status = self.STATUS_ENABLED
		self.last_data_time = rospy.Time.now()

	def set_uninit(self):
		self.status = self.STATUS_UNINT

	def takk_unresponsive(self):
		#rospy.logwarn("Status: " + str(self.status))
		if self.status == self.STATUS_ENABLED and (rospy.Time.now() - self.last_data_time) > self.acceptable_takk_latency:
			return True
		else:
			return False
			

def reset_takk(cli, takk_status):
	global atmega_reset_delay
	off_duration = get_off_duration()
	
	# Power cycle the atmega
	rospy.logdebug("Toggling takktile sensors")
	gpio_comms.send_msg(off_duration.to_sec(), cli)
	time.sleep(off_duration.to_sec())
	time.sleep(atmega_reset_delay)
	if usb.core.find(idVendor=0x59e3, idProduct=0x74C7) is None:
		rospy.logerr("Reboot required. Takktile USB interface not found.")

	# Launch a replacement takktile_node
	launch_process("rosrun takktile_ros takktile_node.py")
	takk_status.takk_node_init_wait()

def launch_process(process_cmd):
	fork_result = os.fork()
	if fork_result == -1:
		rospy.logerr("Fork unsuccessful.")
	elif fork_result == 0:
		rospy.loginfo("Starting '" + process_cmd + "'")
		try:
			os.system(process_cmd)
		except:
			print "Subprocess complete."
		finally:
			os._exit(1)
	else:	
		rospy.loginfo("Control node resumed after fork.")
		return fork_result

# Pulls the current takktile reset duration from the parameter server
def get_off_duration():
	try:
		off_duration = rospy.get_param("/takktile_off_duration")
		return rospy.Duration(off_duration)
	except KeyError:
		rospy.logfatal("Parameter takktile_off_duration is missing from the parameter server. Cannot synchronize with takktile keepalive")
		sys.exit(1)

def launch_gpio():
	rospy.loginfo("Bringing up the gpio process.")
	global switch_channel
	takktile_path	= rospkg.RosPack().get_path('takktile_ros')
	gpio_prog_path 	= takktile_path + "/src/gpio_toggle.py"

	launch_process("sudo " + gpio_prog_path + " --pin=" + str(switch_channel))
	rospy.loginfo("gpio process bringup complete.")
	
	# Let the gpio process initialize comms
	time.sleep(2.0)	
	return gpio_comms.init_cli()

def kill_gpio(cli):
	rospy.loginfo("Cleaning up the gpio_reset process.")
	gpio_comms.send_shutdown(cli)
	gpio_comms.shutdown(cli)

def pi_reboot_cb(msg):
	os.system("sudo reboot")

def operator_takk_reset_cb(msg):
	global operator_reset_flag
	operator_reset_flag = True

if __name__ == "__main__":
	rospy.init_node("takk_electric_reset")

	# Set relevant parameters
	good_latency	= rospy.Duration(1)
	checkin_period 	= rospy.Duration(3)
	hand 		= rospy.get_param("~hand_side", "left")
	takktile_topic 	= rospy.get_param("~takktile_reset_topic", "takktile/calibrated")

	takk_status = TakkDataStatus(takktile_topic, good_latency)
	rospy.loginfo("Tactile reset enabled listening to " + takktile_topic + " for tactile updates on hand " + hand)

	# Give out operator services
	op_takk_reset_sub 	= rospy.Subscriber("operator_takk_reset", Empty, operator_takk_reset_cb)
	op_pi_reboot_sub 	= rospy.Subscriber("operator_pi_reboot", Empty, pi_reboot_cb)

	cli = launch_gpio()
	
	# Initial reset on bringup
	reset_takk(cli, takk_status)
	rospy.sleep(checkin_period)

	# Perpetually check in, looking for downed sensors
	while not rospy.is_shutdown():
		if takk_status.takk_unresponsive():
			# Sensors are dead
			reset_takk(cli, takk_status)
		elif operator_reset_flag:
			# Operator thinks sensors are dead
			reset_takk(cli, takk_status)
			operator_reset_flag = False

		# Wait
		rospy.sleep(checkin_period)
	
	# Cleanup the gpio process.
	kill_gpio(cli)
