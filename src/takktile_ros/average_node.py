#!/usr/bin/env python
import roslib; roslib.load_manifest('takktile_ros')
import rospy
import sys
from takktile_ros.msg import Raw, Touch, Contact, Info
from std_msgs.msg import String

pubby = None

#Notes: The first four data points are averaged,
#	The last four are maximums
def tactile_callback(msg):
	#print "Got a message!"
	global pubby
	out_msg = Touch()
	scaler = -1.0/80
	scaled_values = []
	for pressure in msg.pressure:
		out_pressure =  (pressure * scaler)
		if out_pressure < 0:
			out_pressure = 0
		elif out_pressure > 1:
			out_pressure = 1

		#print "\tpressure: ", pressure
		scaled_values.append(out_pressure)

	#if len(scaled_values) != (4 + 15):	
	#	print "This program is detecting an improper number of sensors present. It is only built for one finger and the palm. Terminating"
	#	sys.exit(1)

	num_sensors = len(scaled_values)
	sensor_data = []
	palm_start = 0
	if num_sensors > 15:
		sensor_data.append(scaled_values[0:4])
		palm_start = 4
		if num_sensors > 19:
			sensor_data.append(scaled_values[4:8])
			palm_start = 8
			if num_sensors > 23:
				sensor_data.append(scaled_values[8:12])
				palm_start = 12
		sensor_data.append(scaled_values[palm_start:])
	elif num_sensors < 15:
		if num_sensors == 4:
			#print "Adding one sensor:",			
			sensor_data.append(scaled_values[0:4])
			#print sensor_data[0]
		if num_sensors == 8:
			sensor_data.append(scaled_values[0:4])
			sensor_data.append(scaled_values[4:8])
		if num_sensors == 12:
			sensor_data.append(scaled_values[0:4])
			sensor_data.append(scaled_values[4:8])
			sensor_data.append(scaled_values[8:12])
	else:
		sensor_data.append(scaled_values)

	for x in range(4):
		if x < len(sensor_data):
			#print "X: ", x, "  sensor_data: ", sensor_data			
			out_msg.pressure.append(average(sensor_data[x]))
		else:
			out_msg.pressure.append(0)
	
	for x in range(4):
		if x < len(sensor_data):
			out_msg.pressure.append(max(sensor_data[x]))
		else:
			out_msg.pressure.append(0)
	
	

	#out_msg.pressure.append(average(scaled_values[0:4]))
	#out_msg.pressure.append(average(scaled_values[4:]))

	#out_msg.pressure.append(max(scaled_values[0:4]))
	#out_msg.pressure.append(max(scaled_values[4:]))
	#out_msg.pressure.append(average(scaled_values[8:12]))
	#out_msg.pressure.append(average(scaled_values[12:]))

	pubby.publish(out_msg)

def average(scaled_values):
	summy = 0
	for value in scaled_values:
		summy += value

	return summy / len(scaled_values)

if __name__ == '__main__':
	rospy.init_node("takktile_average_node")
	print "Hi Sai, this node is online"

	tactile_subscriber = rospy.Subscriber("/takktile/calibrated", Touch, tactile_callback)
	pubby = rospy.Publisher("/gp_contacts", Touch, queue_size=1) 
	rospy.spin()
