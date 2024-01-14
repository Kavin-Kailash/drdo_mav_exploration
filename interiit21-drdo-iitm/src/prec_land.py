#!/usr/bin/python
import random
import rospy
import math as m
from mavros_msgs.msg import LandingTarget, State
from mavros_msgs.srv import SetMode
from fiducial_msgs.msg import FiducialTransformArray
from visualization_msgs.msg import Marker
from geometry_msgs.msg import Pose
import tf2_ros
import tf2_geometry_msgs
from std_msgs.msg import Bool
 

rospy.init_node('PL', anonymous=True)
assigned = False
detect_status = Bool()
cnt = 0

marker = Marker()
current_state = State()
marker.type = Marker.CUBE
marker.scale.x = 0.38
marker.scale.y = 0.1
marker.scale.z = 0.38
marker.color.a = 1.0
marker.color.r = 0.0
marker.color.g = 1.0
marker.color.b = 0.0
marker.header.frame_id = 'camera_link'
   
def call_back_state(msg):
    global state
    current_state = msg

def call_back(aruco):
    global marker
    global assigned
    global detect_status
    global cnt
    aruco_value = FiducialTransformArray()
    aruco_value = aruco
    landing_pos = LandingTarget()
    n = len(aruco_value.transforms)
    for i in range(n):
        if aruco_value.transforms[i].fiducial_id == 0:
            cnt+=1
            detect_status.data = True
            correct_aruco = aruco_value.transforms[i]

            x = correct_aruco.transform.translation.x
            y = correct_aruco.transform.translation.y
            z = correct_aruco.transform.translation.z

            marker.pose.position.x = y
            marker.pose.position.y = -z
            marker.pose.position.z = x
            marker.pose.orientation.w = 1
            
            
            x_offset_rad = m.atan(x/z)
            y_offset_rad = m.atan(y/z)

            distance = m.sqrt(x**2 + y**2 +z**2)

            landing_pos.header.frame_id = aruco_value.header.frame_id 
            landing_pos.header.stamp= rospy.Time.now()
            landing_pos.target_num = 0
            landing_pos.frame = 8 #MAV_FRAME_BODY_NED

            landing_pos.angle[0] = x_offset_rad
            landing_pos.angle[1] = y_offset_rad
            landing_pos.pose.orientation.w = 1
            landing_pos.distance = distance
            
            
            landing_pub.publish(landing_pos)

            if current_state.mode != 'LAND' and cnt > 5:
                viz_pub.publish(marker)
                set_mode_client(base_mode = 0, custom_mode = 'LAND')
                aruco_state_pub.publish(detect_status)

landing_pub = rospy.Publisher('/mavros/landing_target/raw', LandingTarget, queue_size=10)
viz_pub = rospy.Publisher('/aruco_viz', Marker, queue_size=10)
set_mode_client = rospy.ServiceProxy('mavros/set_mode', SetMode)
sub_state = rospy.Subscriber('/mavros/state', State, call_back_state )
subscriber = rospy.Subscriber("/fiducial_transforms", FiducialTransformArray, call_back)
aruco_state_pub = rospy.Publisher("/aruco/detect_status", Bool, queue_size=10)

rospy.spin()