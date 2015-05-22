#!/usr/bin/env python
import roslib; roslib.load_manifest('takktile_ros')
import rospy
import sys
from takktile_ros.msg import Raw, Touch, Contact, Info
from std_msgs.msg import String
import takk_lut

class TactileAggregator:
	def __init__(self, hand_name):
		# Constants
	        self.scaler = -1.0 / 50	# Value to scale the calibrated sensor data
		self.cur_indices = None
		self.lut = takk_lut.mk_lut()
	
		# ROS IO
		self.tactile_data_sub = rospy.Subscriber("takktile/calibrated", Touch, self.tactile_callback)
		self.tactile_info_sub = rospy.Subscriber("takktile/sensor_info", Info, self.info_callback)
		self.tactile_aggregate_pub = rospy.Publisher("robotiq_hands/" + hand_name[0] + "_hand/hand_contacts", Touch, queue_size=1)


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
		
		# Aggregate data
		touch_record = None
		lut_idx = takk_lut.get_idx(self.cur_indices)
		#rospy.logerr("Lut_idx: " +  str(lut_idx))
		if self.lut[lut_idx] != None:
			#rospy.logerr("Taking the LUT")
			touch_record = self.lut[lut_idx](scaled_pressures)
		else:
			#rospy.logerr("Not taking the LUT")
			touch_record = self.default_aggregator(scaled_pressures)

	        # Compose out message: Albert's code expects the following order:
		#	middle, index, pinky, palm
		# print "Palm: ", touch_record.palm, " Thumb: ", touch_record.middle, " Index: ", touch_record.index, " Pinky: ", touch_record.pinky
		out_msg = Touch()
		out_msg.pressure = [touch_record.middle, touch_record.index, touch_record.pinky, touch_record.palm]

        	self.tactile_aggregate_pub.publish(out_msg)
	

	# Iterate through available sensor data using sensor info
	#	to determine when to pull values and when to error-fill
	# The order: index, pinky, middle, palm
	def default_aggregator(self, scaled_pressures):
		touch_record = takk_lut.TactileState(takk_lut.ERR_CODE)
		sensor_start = 0
		if self.index_present():
			touch_record.index = takk_lut.aggregate(scaled_pressures[sensor_start:sensor_start + 6])
			sensor_start += 6

		if self.pinky_present():
			touch_record.pinky = takk_lut.aggregate(scaled_pressures[sensor_start:sensor_start + 6])
			sensor_start += 6

		if self.middle_present():
			touch_record.middle = takk_lut.aggregate(scaled_pressures[sensor_start:sensor_start + 6])
			sensor_start += 6

		if self.palm_present():
			touch_record.palm = takk_lut.aggregate(scaled_pressures[sensor_start:])
		
		return touch_record
	

	def index_present(self):
		return (3 in self.cur_indices)

	def pinky_present(self):
		return (8 in self.cur_indices)

	def middle_present(self):
		return (14 in self.cur_indices)

	def palm_present(self):
		return (25 in self.cur_indices)

if __name__ == '__main__':
        rospy.init_node("hand_contacts_node")
	rospy.logwarn("Assumption: the takktile sensor info data feed will omit entire pads, not single sensors inside a pad.")
	
	hand = rospy.get_param("~hand_side", "left")

	#rospy.logerr("Hand side: '" + hand + "'")

	takk_agg = TactileAggregator(hand)
	rospy.spin()
