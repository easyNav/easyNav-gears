# easyNav-gears

Serves as the hardware platform for easyNav

# Raspberry PI ROS

Uses ROS for communication

Start ROS by typing:
	roscore

Building:
	cd CG3002_CG3002_ROS_WS
	source devel/setup.bash
	catkin_make clean
	catkin_make

Accessing Projects:
	roscd beginner_tutorials/

Running Projects:
	rosrun beginner_tutorials talker
	rosrun beginner_tutorials listener

Create New Package:
	cd CG3002_CG3002_ROS_WS/src
	catkin_create_pkg <NEWPACKAGE> std_msgs rospy roscpp
	cd CG3002_CG3002_ROS_WS
	source devel/setup.bash
	catkin_make

Add CPP to Package:
	roscd <NEWPACKGE>
	nano src/program.cpp
	Update CMakeLists.txt with new CMake Data
	-- Now go back to CG3002_CG3002_ROS_WS and build

Add Python to Package:
	roscd <NEWPACKGE>
	mkdir scripts
	nano scripts/script.py
	chmod +x scripts/script.py
	-- Now go back to CG3002_CG3002_ROS_WS and build

# Arduino Free RTOS