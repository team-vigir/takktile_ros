#!/usr/bin/env python
# This code must be run with super user privileges since it touches physical hardware
# Valuable Resources: http://sourceforge.net/p/raspberry-gpio-python/wiki/BasicUsage/
#	pi pinout diagram in takktile_ros catkin branch
# TODO: Make this the keep-alive checker as well if possible
import sys
import rospy
import RPi.GPIO as GPIO
from takktile_ros.msg import Raw

takk_data_flag = None	# States whether data has been received yet from takktile sensors in this check cycle
switch_channel = 14 	# The pin used for toggling the takktile power circuit

def power_cycle_takk():
	global switch_channel
	off_duration = get_off_duration()
	
	# Toggle the switch pin for a duration
	GPIO.output(switch_channel, GPIO.LOW)
	rospy.sleep(off_duration)
	GPIO.output(switch_channel, GPIO.HIGH)

# Pulls the current takktile reset duration from the parameter server
def get_off_duration():
	try:
		off_duration = rospy.get_param("takktile_off_duration")
		return rospy.Duration(off_duration)
	except KeyError:
		rospy.logfatal("Parameter takktile_off_duration is missing from the parameter server. Cannot synchronize with takktile keepalive")
		sys.exit(1)

def init_gpio():
	global switch_channel
	GPIO.setmode(GPIO.BOARD)
	GPIO.setup(switch_channel, GPIO.OUT, initial=GPIO.HIGH)

def takktile_data_cb(msg):
	global takk_data_flag
	takk_data_flag = True

if __name__ == "__main__":
	global takk_data_flag
	rospy.init_node("takk_electric_reset")

	init_gpio()
	
	rospy.logerror("takktile reset node developed for left hand only. Set parameter server appropriately.")
	hand= "left"
	takktile_topic = "takktile/raw"

	acceptable_takk_latency = rospy.Duration(1)
	checkin_period = rospy.Duration(5)
	bringup_delay = rospy.Duration(10) #TODO: Determine an accurate bringup period on a fully loaded pi
	while not rospy.is_shutdown():
		# Subscribe and wait for a data msg
		takk_data_sub = rospy.Subscribe(takktile_topic, Raw, takktile_data_cb)
		rospy.sleep(acceptable_takk_latency)
		if takk_data_flag == False:
			# Sensors are dead
			power_cycle_takk()
			#TODO: Kill the takktile_ros node?
			rospy.sleep(bringup_delay)

		# Reset and wait
		if takk_data_flag is not None:
			takk_data_flag = False
		takk_data_sub.unsubscribe()
		rospy.sleep(checkin_period)
		
