#!/usr/bin/env python
import roslib; roslib.load_manifest('takktile_ros')
import rospy
from takktile_ros.msg import Raw, Touch, Contact, Info
from std_msgs.msg import String
import sys

#TODO: Run this aggregation node on the pi itself and prevent transmitting lots of crap data onto the system

# An easy-to-reference model of the hand's takktile arrays.
#	Meant to be filled with float data between 0 and 1
#	or an error for each finger.
class TactileState:
	def __init__(self, err_code):
		self.middle = err_code
		self.pinky = err_code
		self.index = err_code
		self.palm = err_code

class TactileAggregator:
	def __init__(self, hand_name):
		# Constants
		self.err_code = -1	# Code to send when a finger is missing. TODO: make is a rosparam
	        self.scaler = -1.0 / 50	# Value to scale the calibrated sensor data
	
		# ROS IO
		self.tactile_data_sub = rospy.Subscriber(hand_name+ "_hand/tactile_data", Touch, self.tactile_callback)
		self.tactile_info_sub = rospy.Subscriber(hand_name + "_hand/sensor_info", Info, self.info_callback)
		self.tactile_aggregate_pub = rospy.Publisher("/robotiq_hands/" + hand_name[0] + "_hand/hand_contacts", Touch, queue_size=1)
		
		self.cur_indices = None

	def info_callback(self, msg):
		self.cur_indices = msg.indexes

	def tactile_callback(self, msg):
		# Check that we can parse sensor data
		if self.cur_indices == None:
			rospy.loginfo("No sensor info data present. Publishing error code for all fingers")
			return

	        # Scale data
	        scaled_pressures = []
		for pressure in msg.pressure:
	                out_pressure =  (pressure * self.scaler)
	                if out_pressure < 0:
	                        out_pressure = 0
	                elif out_pressure > 1:
	                        out_pressure = 1
	
	                #print "\tpressure: ", pressure
	                scaled_pressures.append(out_pressure)
		
		# Iterate through available sensor data using sensor info
		#	to determine when to pull values and when to error-fill
		# The order: index, pinky, middle, palm
		touch_record = TactileState(self.err_code)
		sensor_start = 0
		if self.index_present():
			touch_record.index = self.aggregate(scaled_pressures[sensor_start:sensor_start + 6])
			sensor_start += 6

		if self.pinky_present():
			touch_record.pinky = self.aggregate(scaled_pressures[sensor_start:sensor_start + 6])
			sensor_start += 6

		if self.middle_present():
			touch_record.middle = self.aggregate(scaled_pressures[sensor_start:sensor_start + 6])
			sensor_start += 6

		if self.palm_present():
			touch_record.palm = self.aggregate(scaled_pressures[sensor_start:])
			
	
	        # Compose out message: Albert's code expects the following order:
		#	middle, pinky, index, palm
		out_msg = Touch()
		out_msg.pressure = [touch_record.middle, touch_record.pinky, touch_record.index, touch_record.palm]

        	self.tactile_aggregate_pub.publish(out_msg)
	
	def index_present(self):
		return (3 in self.cur_indices)

	def pinky_present(self):
		return (8 in self.cur_indices)

	def middle_present(self):
		return (14 in self.cur_indices)

	def palm_present(self):
		return (25 in self.cur_indices)

	# Currently just a straight average
	def aggregate(self, pad_pressure_list):
	        summy = 0
	        for value in pad_pressure_list:
	                summy += value
	
	        return summy / (len(pad_pressure_list))

if __name__ == '__main__':
        rospy.init_node("hand_contacts_node")
	rospy.logwarn("Assumption: the takktile sensor info data feed will omit entire pads, not single sensors inside a pad.")
	
	hand = rospy.get_param("~hand_side", "left")

	#rospy.logerr("Hand side: '" + hand + "'")

	takk_agg = TactileAggregator(hand)
	rospy.spin()
