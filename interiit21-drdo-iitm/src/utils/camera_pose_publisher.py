#!/usr/bin/python
import rospy
import math
import tf
import tf_conversions
from geometry_msgs.msg import PoseStamped,Quaternion

if __name__ == '__main__':
    rospy.init_node('camera_pose_publisher')

    parent_frame = rospy.get_param('~parent_frame', 'map')
    camera_frame = rospy.get_param('~child_frame','camera_link')
    pose_topic = rospy.get_param('~pose_topic','camera/pose')

    pose_pub = rospy.Publisher(pose_topic, PoseStamped, queue_size=1)

    listener = tf.TransformListener()

    rate = rospy.Rate(100.0)
    while not rospy.is_shutdown():
        try:
            (trans,rot) = listener.lookupTransform('/'+parent_frame, '/'+camera_frame, rospy.Time(0))
        except (tf.LookupException, tf.ConnectivityException, tf.ExtrapolationException):
            continue

        pose_msg = PoseStamped()
        pose_msg.header.frame_id = parent_frame
        pose_msg.header.stamp = rospy.Time.now()
        pose_msg.pose.position.x = trans[0]
        pose_msg.pose.position.y = trans[1]
        pose_msg.pose.position.z = trans[2]
        pose_msg.pose.orientation.x = rot[0]
        pose_msg.pose.orientation.y = rot[1]
        pose_msg.pose.orientation.z = rot[2]
        pose_msg.pose.orientation.w = rot[3]
        del_yaw = 0
        pose_rpy = tf_conversions.transformations.euler_from_quaternion([pose_msg.pose.orientation.x,pose_msg.pose.orientation.y,pose_msg.pose.orientation.z,pose_msg.pose.orientation.w])
        new_att = tf_conversions.transformations.quaternion_from_euler(pose_rpy[0],pose_rpy[1],pose_rpy[2]+del_yaw)
        pose_msg.pose.orientation = Quaternion(new_att[0],new_att[1],new_att[2],new_att[3])
        pose_pub.publish(pose_msg)

        rate.sleep()


