# http://ros.org/doc/groovy/api/catkin/html/user_guide/supposed.html
cmake_minimum_required(VERSION 2.8.3)
project(takktile_ros)
find_package(catkin REQUIRED COMPONENTS
    rospy
    message_generation
    std_msgs
    std_srvs
    geometry_msgs
)

#set the default path for built executables to the "bin" directory
set(EXECUTABLE_OUTPUT_PATH ${PROJECT_SOURCE_DIR}/bin)
#set the default path for built libraries to the "lib" directory
set(LIBRARY_OUTPUT_PATH ${PROJECT_SOURCE_DIR}/lib)

###################################
## catkin message generation     ##
###################################
add_message_files(
  FILES
  Contact.msg
  Info.msg
  Raw.msg
  Touch.msg
)

catkin_python_setup()

 generate_messages(
   DEPENDENCIES   geometry_msgs std_msgs std_srvs
 )

###################################
## catkin specific configuration ##
###################################
## The catkin_package macro generates cmake config files for your package
## Declare things to be passed to dependent projects
## LIBRARIES: libraries you create in this project that dependent projects also need
## CATKIN_DEPENDS: catkin_packages dependent projects also need
## DEPENDS: system dependencies of this project that dependent projects also need
catkin_package(
    INCLUDE_DIRS ${catkin_INCLUDE_DIRS}
    CATKIN_DEPENDS
    rospy
    std_msgs
    std_srvs
    geometry_msgs
)

###########
## Build ##
###########

## Specify additional locations of header files
include_directories(include
  ${catkin_INCLUDE_DIRS}
)

#############
## Install ##
#############

# all install targets should use catkin DESTINATION variables
# See http://ros.org/doc/groovy/api/catkin/html/adv_user_guide/variables.html

#install(PROGRAMS src/takktile_node.py src/dot_display.py
#        src/viz_array.py DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION})
