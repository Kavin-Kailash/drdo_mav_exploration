#!/usr/bin/python

# Pyhton System utilities
import subprocess
import signal
import os
import atexit
import time

# ROS wrappers
import rospy
import rosgraph
from geometry_msgs.msg import PoseStamped
from mavros_msgs.msg import State
from sensor_msgs.msg import PointCloud2
from std_msgs.msg import Bool, String

# Map Size Bounds
import map_bounds
bounds = map_bounds.bounds
args = map_bounds.key_list

def cleanup():
    # Cleans up child processes on exit/termination
    # WARNING : won't be called if parent process is killed (Eg: kill -9 12345)
    #           won't Kill Terminal applications like gnome-terminal, xterm etc.
    global child_process
    for p in child_process.values():  # list of your processes
        os.killpg(os.getpgid(p.pid), signal.SIGTERM)


def pcl_cb(msg):
    # PCL Callback for detecting exploration initialization
    global exploration_init
    if not exploration_init:
        exploration_init = True


def pose_cb(msg):
    # Pose Callback for detecting GPS_FIX
    global gps_fix, current_pose
    if not gps_fix:
        gps_fix = True
    current_pose = msg


def state_cb(state):
    # MAV State Callback
    global current_state, aruco_detected
    current_state = state
    if not aruco_detected:
        aruco_msg.data = "Marker ID: none, looking for marker"
        aruco_msg_pub.publish(aruco_msg)



def dist(height):
    return abs(height-current_pose.pose.position.z)

def aruco_cb(status):
    # Aruco Detecition Callback
    global aruco_detected
    if (not aruco_detected) and status:
        aruco_detected = True



child_process = {}
atexit.register(cleanup)  # register Cleanup Process
gps_fix = False
exploration_init = False
aruco_detected = False
current_state = State()
current_pose = PoseStamped()
aruco_msg = String()



if __name__ == '__main__':

    # Initialize script as ROS Node
    rospy.init_node('commander', anonymous=True)
    rate = rospy.Rate(1)

    pose_sub = rospy.Subscriber('/mavros/local_position/pose', PoseStamped, pose_cb)
    state_sub = rospy.Subscriber('/mavros/state', State, state_cb)
    pcl_sub = rospy.Subscriber('/sdf_map/occupancy_all', PointCloud2, pcl_cb)
    trigger = rospy.Publisher('/move_base_simple/goal', PoseStamped, queue_size=10)
    aruco_state_sub = rospy.Subscriber('/aruco/detect_status', Bool,aruco_cb)
    aruco_msg_pub = rospy.Publisher('Aruco/message', String, queue_size=10)
    
    # Get user params
    gui_flag = rospy.get_param("/commander_node/gui")
    world_id = rospy.get_param('/commander_node/world_id')
    takeoff_ht = rospy.get_param("/commander_node/takeoff_ht")

    # Launch APM SITL
    os.system("gnome-terminal -- sim_vehicle.py --add-param-file=$(rospack find interiit21-drdo)/cfg/apm_params/default_params.parm -v ArduCopter -f gazebo-iris --mavproxy-args='--streamrate=-1'")

    # Launch Gazebo (Headless) and Rviz
    sim_str = "roslaunch interiit21-drdo sim_main.launch gui:="
    sim_str = sim_str + str(gui_flag) +" "+ "world:=" + str(world_id)
    child_process['SIM'] = subprocess.Popen(
        [sim_str], shell=True, preexec_fn=os.setsid,
        stdout=open(os.devnull, 'wb'),
        stderr=open(os.devnull, 'wb'))

    # Wait for FCU connection
    rospy.loginfo("Waiting for FCU connection ...")
    while not rospy.is_shutdown() and not current_state.connected:
        rate.sleep()
    rospy.loginfo("FCU connection Established")

    # Launch Aruco Detection and Precision Landing Module
    child_process['PL'] = subprocess.Popen(
        ["roslaunch interiit21-drdo aruco_detect.launch"], shell=True, preexec_fn=os.setsid,
        stdout=open(os.devnull, 'wb'),
        stderr=open(os.devnull, 'wb'))
    rospy.loginfo("Aruco detection and Precision landing module started")

    # Wait for GPS Lock
    rospy.loginfo("Waiting for GPS Fix ...")
    while not rospy.is_shutdown() and not gps_fix:
        rate.sleep()
    rospy.loginfo("GPS Fix Confirmed")

    # Launch Exploration Planner
    exp_str = "roslaunch interiit21-drdo exploration.launch"
    for key,val in bounds[world_id-1].iteritems():
        exp_str = exp_str + " " + key + ":=" + str(val)
    
    rospy.loginfo("Launching Exploration Module ...")
    child_process['EXPLORATION'] = subprocess.Popen(
        [exp_str], shell=True, preexec_fn=os.setsid,
        stdout=open(os.devnull, 'wb'),
        stderr=open(os.devnull, 'wb'))

    # Wait for Exploration Planner to Initialize to Idle state
    while not rospy.is_shutdown() and not exploration_init:
        rate.sleep()
    rospy.sleep(1)
    rospy.loginfo("Exploration Module Initialized")

    # Launch Trajectory Controller
    traj_str = "roslaunch interiit21-drdo traj_control.launch takeoff_height:=" + str(takeoff_ht)
    
    rospy.loginfo("Launching Trajectory Controller Module ...")
    child_process['CONTROLLER'] = subprocess.Popen(
        [traj_str], shell=True, preexec_fn=os.setsid,
        stdout=open(os.devnull, 'wb'),
        stderr=open(os.devnull, 'wb'))

    # Wait for Trajectory Controller Initialization
    while not rospy.is_shutdown() and not rospy.has_param('/geometric_controller/to_hgt'):
        rate.sleep()
    tgt_ht = rospy.get_param('/geometric_controller/to_hgt')

    # Begin Takeoff (Performed automoatically by the Trajectory Controller)
    rospy.loginfo("Trajectory Controller Initialized")
    rospy.sleep(2)
    rospy.loginfo("Takeoff Started ...")

    # Wait for Takeoff completition
    while not rospy.is_shutdown() and dist(tgt_ht) > 0.5:
        rate.sleep()
    rospy.loginfo("Takeoff Completed")

    # Record current time (for )
    now = rospy.Time.now()
    rospy.loginfo("Mission Start %i %i", now.secs, now.nsecs)

    # Trigger the exploration planner to start the planning
    trigger.publish(current_pose)
    
    # Wait for Aruco Marker Detection
    while not rospy.is_shutdown():
        rospy.Rate(10).sleep()
        if aruco_detected:
            break

    # Kill the Exploration and Trajectory Controller Modules
    os.killpg(os.getpgid(child_process['CONTROLLER'].pid), signal.SIGTERM)
    os.killpg(os.getpgid(child_process['EXPLORATION'].pid), signal.SIGTERM)

    rospy.loginfo("Aruco marker with ID0 Detected!")
    rospy.loginfo("Initiated Precision Landing ...")
    rospy.loginfo("Stopping Exploration Planner ...")
    rospy.loginfo("Stopping Trajectory Controller ...")

    flag = 0
    while not rospy.is_shutdown():
        if (current_pose.pose.position.z < 0.10) and flag==0:
            # On Landing, print the total Mission Time
            end_time = rospy.Time.now()
            flag = 1
            rospy.loginfo("Mission End %i %i", end_time.secs, end_time.nsecs)
            rospy.loginfo("Mission Time: %i", end_time.secs-now.secs)
            aruco_msg.data = "Marker ID : 0, Landed"
            aruco_msg_pub.publish(aruco_msg)    
        rospy.sleep(0.5)
