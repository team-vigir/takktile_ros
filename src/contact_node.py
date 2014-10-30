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
        scaler = -1.0 / 200
        scaled_values = []
        for pressure in msg.pressure:
                out_pressure =  (pressure * scaler)
                if out_pressure < 0:
                        out_pressure = 0
                elif out_pressure > 1:
                        out_pressure = 1

                #print "\tpressure: ", pressure
                out_msg.pressure.append(out_pressure)

#        out_msg.pressure.append(average(scaled_values[0:4]))
#        out_msg.pressure.append(average(scaled_values[4:8]))
#        out_msg.pressure.append(average(scaled_values[8:12]))
#        out_msg.pressure.append(average(scaled_values[12:17]))
#        out_msg.pressure.append(average(scaled_values[17:22]))
#        out_msg.pressure.append(average(scaled_values[22:]))

        pubby.publish(out_msg)

def average(scaled_values):
        summy = 0
        for value in scaled_values:
                summy += value

        return summy / (len(scaled_values))

if __name__ == '__main__':
        rospy.init_node("takktile_converter_node")
        print "Hi Sai, this node is online"
        global pubby

        tactile_subscriber = rospy.Subscriber("/takktile/calibrated", Touch, tactile_callback)
        pubby = rospy.Publisher("/hand_contacts", Touch, queue_size=1)
        rospy.spin()
