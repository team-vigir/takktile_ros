#!/usr/bin/env python

#'''
#Gaussian Process Regression.
#Testing using takktile data for DRC,
#Sai Krishna
#'''

import rospy
import roslib; roslib.load_manifest('takktile_ros')
from takktile_ros.msg import Touch
import rospkg

recent_takktile_data = None
rospack = rospkg.RosPack()
takktile_base_path = rospack.get_path('takktile_ros')

def tactile_callback(msg):
    global recent_takktile_data
    #print "Takktile data: ", msg.pressure
    recent_takktile_data = msg.pressure

#-------function to import data--------------------------
import pyGPs
import numpy as np
def import_gp_data(filename):
    csv_file = open(filename, "r")
    lines = csv_file.readlines()

    grasp_data = []
    for line in lines[1:]:
        float_row = []
        row = line.split("\t")
        row[-1] = row[-1][:-1]
        cnt = min(len(row), 9)
        for element in row[1:cnt]:
            float_row.append(float(element))
        grasp_data.append(float_row)

    out_data = np.array(grasp_data)
    csv_file.close()
    return out_data
#--------------------END------------------------------------------------        
#demoData = np.load('regression_data.npz')
#user_file_name = raw_input("Please input the grasp data file name: ")
#-------------------------WHICH OBJECT DATA TO CHOOSE-------------------

def run_gp(obj):
    #obj = raw_input('enter name of the object: ')
    training_data_path = takktile_base_path + "/src/takktile_ros/training_data/"
    if obj == 'cylinder':
        user_file_name = training_data_path + 'data_cylinder.txt'
        x = import_gp_data(user_file_name) # training data
        user_file_name = training_data_path + 'results.txt'
        y = import_gp_data(user_file_name) # results data
        user_file_name = training_data_path + 'test_cylinder.txt'
        z = import_gp_data(user_file_name) # test data
    elif obj == 'debris1':
        user_file_name = 'data_debris1.txt'
        x = import_gp_data(user_file_name) # training data
        user_file_name = 'results.txt'
        y = import_gp_data(user_file_name) # results data
        user_file_name = 'test_debris1.txt'
        z = import_gp_data(user_file_name) # test data
    elif obj == 'debris2':
        user_file_name = 'data_debris2.txt'
        x = import_gp_data(user_file_name) # training data
        user_file_name = 'results.txt'
        y = import_gp_data(user_file_name) # results data
        user_file_name = 'test_debris2.txt'
        z = import_gp_data(user_file_name) # test data
    elif obj == 'knob':
        user_file_name = 'data_knob.txt'
        x = import_gp_data(user_file_name) # training data
        user_file_name = 'results.txt'
        y = import_gp_data(user_file_name) # results data
        user_file_name = 'test_knob.txt'
        z = import_gp_data(user_file_name) # test data
    elif obj == 'drill':
        user_file_name = 'data_driller.txt'
        x = import_gp_data(user_file_name) # training data
        user_file_name = 'results.txt'
        y = import_gp_data(user_file_name) # results data
        user_file_name = 'test_drill.txt'
        z = import_gp_data(user_file_name) # test data

    #-----------END LOADING DATA----------------------------------------

    global recent_takktile_data
    z = np.array([recent_takktile_data])
    print 'this is x',x.shape
    print 'this is y',y.shape
    print 'this is z', z , "shape: ", z.shape
    
    #-------------START GP----------------------------------------------
    model = pyGPs.GPR()           # start from a new model
    model.getPosterior(x, y)
    print 'Initial negative log marginal likelihood = ', round(model.nlZ,3)
    model.optimize(x,y)
    #ym, ys2, fm, fs2, lp = model.predict(z)
    print 'Optimized negative log marginal likelihood:', round(model.nlZ,3)
    post = model.posterior
    ym, ys2, fmu, fs2, lp = model.predict_with_posterior(post,z)
    print ym
    print ys2

    #----------------------------END GP---------------------------------
    return ym, ys2

if __name__ == "__main__":
    rospy.init_node("robotiq_gp_classifier")
    print "Control of GP routed to main"

    takktile_sub = rospy.Subscriber("/gp_contacts", Touch, tactile_callback)
    
    while True:
        raw_input("Press enter to run GP.")
        run_gp("cylinder")








