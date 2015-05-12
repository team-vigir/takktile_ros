#!/usr/bin/env python
# This code must be run with super user privileges since it touches physical hardware
# Valuable Resources: http://sourceforge.net/p/raspberry-gpio-python/wiki/BasicUsage/
#	pi pinout diagram in takktile_ros catkin branch
import sys
import os
import rospy
import RPi.GPIO as GPIO
from takktile_ros.msg import Touch

takk_data_flag = None	# States whether data has been received yet from takktile sensors in this check cycle
switch_channel = 14 	# The pin used for toggling the takktile power circuit

def power_cycle_takk():
	global switch_channel
	off_duration = get_off_duration()
	
	# Toggle the switch pin for a duration
	rospy.logdebug("Toggling takktile sensors")
	#GPIO.output(switch_channel, GPIO.LOW)
	#rospy.sleep(off_duration)
	#GPIO.output(switch_channel, GPIO.HIGH)
	os.system("sudo ~/gpio_toggle.py --pin=" + str(switch_channel) + " --duration=" + str(off_duration.to_sec()))

# Pulls the current takktile reset duration from the parameter server
def get_off_duration():
	try:
		off_duration = rospy.get_param("/takktile_off_duration")
		return rospy.Duration(off_duration)
	except KeyError:
		rospy.logfatal("Parameter takktile_off_duration is missing from the parameter server. Cannot synchronize with takktile keepalive")
		sys.exit(1)

def init_gpio():
	global switch_channel
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(switch_channel, GPIO.OUT, initial=GPIO.HIGH)

def takktile_data_cb(msg):
	global takk_data_flag
	takk_data_flag = True

if __name__ == "__main__":
	rospy.init_node("takk_electric_reset")

	#init_gpio()
	hand = rospy.get_param("~hand_side", "left")
	takktile_topic = rospy.get_param("~takktile_reset_topic", "left_hand/tactile/calibrated")

	rospy.loginfo("Tactile reset enabled listening to " + takktile_topic + " for tactile updates on hand " + hand)

	acceptable_takk_latency = rospy.Duration(1)
	checkin_period = rospy.Duration(4)
	bringup_delay = rospy.Duration(10) #TODO: Determine an accurate bringup period on a fully loaded pi
	while not rospy.is_shutdown():
		# Subscribe and wait for a data msg
		takk_data_sub = rospy.Subscriber(takktile_topic, Touch, takktile_data_cb)
		rospy.sleep(acceptable_takk_latency)
		if takk_data_flag == False:
			# Sensors are dead
			power_cycle_takk()
			#TODO: Kill the takktile_ros node?
			rospy.logdebug("Sleeping bringup_delay seconds")
			rospy.sleep(bringup_delay)

		# Reset and wait
		if takk_data_flag is not None:
			takk_data_flag = False
		else:
			rospy.loginfo("No takktile data received")
		takk_data_sub.unregister()
		rospy.sleep(checkin_period)
		
