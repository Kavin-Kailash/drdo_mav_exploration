#!/usr/bin/python

import random
import rospy
import math as m
from mavros_msgs.msg import LandingTarget, State
from mavros_msgs.srv import SetMode
from fiducial_msgs.msg import FiducialTransformArray

rospy.init_node('PL', anonymous=True)

current_state = State()
def call_back_state(msg):
    global state
    current_state = msg

def call_back(aruco):
    aruco_value = FiducialTransformArray()
    aruco_value = aruco
    landing_pos = LandingTarget()
    if len(aruco_value.transforms) !=0 :

        x = aruco_value.transforms[0].transform.translation.x
        y = aruco_value.transforms[0].transform.translation.y
        z = aruco_value.transforms[0].transform.translation.z

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

        print("assigned")

        publisher = rospy.Publisher('/mavros/landing_target/raw',LandingTarget,queue_size=10)
        publisher.publish(landing_pos)
        if current_state.mode != 'LAND':
            set_mode_client(base_mode = 0, custom_mode = 'LAND')
    else:
        print('no marker in sight')
set_mode_client = rospy.ServiceProxy('mavros/set_mode', SetMode)
sub_state = rospy.Subscriber('/mavros/state', State, call_back_state )
subscriber = rospy.Subscriber("/fiducial_transforms", FiducialTransformArray, call_back)

rospy.spin()