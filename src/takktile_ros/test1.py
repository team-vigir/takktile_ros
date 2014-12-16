#!/usr/bin/env python
import roslib; roslib.load_manifest('takktile_ros')
import rospy
import sys
import random
from takktile_ros.msg import Raw, Touch, Contact, Info
from std_msgs.msg import String

pubby = None
current_takktile_msg = None

def takktile_contact_callback(msg):
	global current_takktile_msg
	#print "test1's global msg updated"
	current_takktile_msg = msg

def data_record():
	#print "Got a message!"
	global pubby
	global current_takktile_msg
	temp1=[]
	temp2=[]
	temp3=[]
	temp4=[]	
	i=0

	test_num = 9	
	grasp_data_file = open("grasp_tactile_results.csv", "w")
	grasp_data_file.write("grasp, middle finger, left finger, right finger, palm \n")	
	while True:
		user_input = raw_input("press any key...")
		if user_input == "q" or user_input == "Q":
			break
		elif user_input == "n":
			grasp_data_file.close()
			test_num += 1
		else:
			grasp_data_file = open(
        		temp1.append(current_takktile_msg.pressure[0])
        		temp2.append(current_takktile_msg.pressure[1])
        		temp3.append(current_takktile_msg.pressure[2])
			temp4.append(current_takktile_msg.pressure[3])
	
      
      			print temp1,temp2,temp3,temp4
			grasp_data_file.write("grasp " + str(i%3))
			grasp_data_file.write(", " + str(temp1[i-1]))
			grasp_data_file.write(", " + str(temp2[i-1]))
			grasp_data_file.write(", " + str(temp3[i-1]))
			grasp_data_file.write(", " + str(temp4[i-1]) + "\n")
    			i += 1
		else:
			break

	grasp_data_file.close()
	
	return temp1, temp2, temp3, temp4



if __name__ == '__main__':
	rospy.init_node("takktile_test_node")
	print "Hi Sai, this node is online"
	global pubby

	tactile_subscriber = rospy.Subscriber("/average_contacts", Touch, takktile_contact_callback)
	pubby = rospy.Publisher("/test_contacts", Touch, queue_size=1)
	data_record()




	
