#!/usr/bin/env python
# This code must be run with super user privileges since it touches physical hardware
# Valuable Resources: http://sourceforge.net/p/raspberry-gpio-python/wiki/BasicUsage/
#	pi pinout diagram in takktile_ros catkin branch
import sys
import os
import rospy
import RPi.GPIO as GPIO
from takktile_ros.msg import Touch
from std_srvs.srv import Empty

takk_data_flag = None	# States whether data has been received yet from takktile sensors in this check cycle
switch_channel = 14 	# The pin used for toggling the takktile power circuit

def reset_takk():
	global switch_channel
	off_duration = get_off_duration()
	atmega_reset_delay = rospy.Duration(3)
	
	rospy.logdebug("Toggling takktile sensors")
	# Power cycle the pins
	os.system("sudo ~/gpio_toggle.py --pin=" + str(switch_channel) + " --duration=" + str(off_duration.to_sec()))
	rospy.sleep(atmega_reset_delay)

	# Give the new node the goahead
	rospy.loginfo("Sending goahead signal to new takktile node")
	rospy.wait_for_service('takktile_goahead')
	takktile_goahead_srv = rospy.ServiceProxy('takktile_goahead', Empty)
	ret = takktile_goahead_srv()

# Pulls the current takktile reset duration from the parameter server
def get_off_duration():
	try:
		off_duration = rospy.get_param("/takktile_off_duration")
		return rospy.Duration(off_duration)
	except KeyError:
		rospy.logfatal("Parameter takktile_off_duration is missing from the parameter server. Cannot synchronize with takktile keepalive")
		sys.exit(1)

def takktile_data_cb(msg):
	global takk_data_flag
	takk_data_flag = True

if __name__ == "__main__":
	rospy.init_node("takk_electric_reset")

	hand = rospy.get_param("~hand_side", "left")
	takktile_topic = rospy.get_param("~takktile_reset_topic", "left_hand/tactile/calibrated")

	rospy.loginfo("Tactile reset enabled listening to " + takktile_topic + " for tactile updates on hand " + hand)

	# Initial reset on bringup
	reset_takk()

	acceptable_takk_latency = rospy.Duration(1)
	checkin_period = rospy.Duration(2)
	bringup_delay = rospy.Duration(3) #TODO: Determine an accurate bringup period on a fully loaded pi
	while not rospy.is_shutdown():
		# Subscribe and wait for a data msg
		takk_data_sub = rospy.Subscriber(takktile_topic, Touch, takktile_data_cb)
		rospy.sleep(acceptable_takk_latency)
		if takk_data_flag == False:
			# Sensors are dead
			reset_takk()
			takk_data_flag = False
			rospy.sleep(bringup_delay)

		# Reset and wait
		if takk_data_flag is not None:
			takk_data_flag = False
		else:
			rospy.loginfo("No takktile data received")
		takk_data_sub.unregister()
		rospy.sleep(checkin_period)
		
