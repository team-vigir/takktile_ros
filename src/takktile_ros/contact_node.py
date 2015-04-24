#!/usr/bin/env python
import roslib; roslib.load_manifest('takktile_ros')
import rospy
from takktile_ros.msg import Raw, Touch, Contact, Info
from std_msgs.msg import String

pubby = None

def tactile_callback(msg):
        #print "Got a message!"
        global pubby
        out_msg = Touch()
        scaler = -1.0 / 50
        scaled_pressures = []

	#Hack, chop and slice!~!!!!!!!!!!!
	msg.pressure = list(msg.pressure[0:6]) + [0,0,0,0,0,0] + list(msg.pressure[7:])


	for pressure in msg.pressure:
                out_pressure =  (pressure * scaler)
                if out_pressure < 0:
                        out_pressure = 0
                elif out_pressure > 1:
                        out_pressure = 1

                #print "\tpressure: ", pressure
                scaled_pressures.append(out_pressure)
	
	out_msg.pressure.append(average(scaled_pressures[13:19]))
	out_msg.pressure.append(average(scaled_pressures[7:13]))
	out_msg.pressure.append(average(scaled_pressures[0:6]))
	out_msg.pressure.append(average(scaled_pressures[20:]))

        pubby.publish(out_msg)

def average(scaled_values):
        summy = 0
        for value in scaled_values:
                summy += value

        return summy / (len(scaled_values))

if __name__ == '__main__':
        rospy.init_node("takktile_converter_node")
        global pubby

	hand = "left" #TODO: Make this a private parameter
        tactile_subscriber = rospy.Subscriber("/" + hand + "_hand/tactile_data", Touch, tactile_callback)
        pubby = rospy.Publisher("/robotiq_hands/" + hand[0] + "_hand/hand_contacts", Touch, queue_size=1)
        rospy.spin()
