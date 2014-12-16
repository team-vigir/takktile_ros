#!/usr/bin/env python
import roslib; roslib.load_manifest('takktile_ros')
import rospy
import sys
import random
from takktile_ros.msg import Raw, Touch, Contact, Info
from std_msgs.msg import String

current_takktile_msg = None
current_takktile_msg4 = None

def takktile_contact_callback(msg):
	global current_takktile_msg
	current_takktile_msg = msg

def takktile_contact_callback2(msg):
	global current_takktile_msg4
	current_takktile_msg4 = msg

def data_record():
	#print "Got a message!"
	global current_takktile_msg
	#temp2=[]
	#temp3=[]
	#temp4=[]	
	i=0
	test_num = 1

	grasp_data_file = open("test" + str(test_num) + "_20.txt", "w")
	grasp_data_file4 = open("test" + str(test_num) + "_4.txt", "w")
	#grasp_data_file = open("grasp_20tactile_results.csv", "w")
	grasp_data_file4.write("grasp\tmiddle finger\tleft finger\tright finger\tpalm\n")	
	while True:
		user_input = raw_input("press any key...")
		if user_input == "q" or user_input == "Q":
			break
		elif user_input == "n":
			grasp_data_file.close()
			grasp_data_file4.close()
			test_num += 1
			grasp_data_file = open("test" + str(test_num) + "_20.txt", "w")
			grasp_data_file4 = open("test" + str(test_num) + "_4.txt", "w")
			grasp_data_file4.write("grasp\tmiddle finger\tleft finger\tright finger\tpalm\n")
		else:
			temp=[] 
			temp2 = [] 
			
			# Get values     		
			for idx in range(27):
				temp.append(current_takktile_msg.pressure[idx])
			for idx in range(4):
				temp2.append(current_takktile_msg4.pressure[idx])    
			
      			print temp#1,temp2,temp3,temp4
			
			#save values
			grasp_data_file.write("grasp " + str(i%3))
			grasp_data_file4.write("grasp " + str(i%3))
			for idx in range(27):
				print temp[idx]
				grasp_data_file.write("\t" + str(temp[idx]))
			for idx in range(4):
				grasp_data_file4.write("\t" + str(temp2[idx]))

			#grasp_data_file.write(", " + str(temp2[i-1]))
			#grasp_data_file.write(", " + str(temp3[i-1]))
			#grasp_data_file.write(", " + str(temp4[i-1]) + "\n")
			grasp_data_file.write("\n")
			grasp_data_file4.write("\n")
    			i += 1


	grasp_data_file.close()
	
	return temp



if __name__ == '__main__':
	rospy.init_node("takktile_individual_node")
	print "Hi Sai, this node is online"
	global pubby

	tactile_subscriber = rospy.Subscriber("/takktile/calibrated", Touch, takktile_contact_callback)
	tactile_subscriber2 = rospy.Subscriber("/average_contacts", Touch, takktile_contact_callback2)
	data_record()




	
