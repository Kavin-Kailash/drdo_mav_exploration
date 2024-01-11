#include <ros/ros.h>
#include <mavros_msgs/CommandBool.h>
#include <mavros_msgs/CommandTOL.h>
#include <mavros_msgs/SetMode.h>
#include <mavros_msgs/State.h>
#include <geometry_msgs/PoseStamped.h>

mavros_msgs::State current_state;
mavros_msgs::CommandTOL takeoff_request;
bool gps_ok = false;
 
void state_cb(const mavros_msgs::State::ConstPtr& msg){
    current_state = *msg;
}

void mav_pose_cb(const geometry_msgs::PoseStamped::ConstPtr& msg) {
  if (!gps_ok) {
    gps_ok = true;
    ROS_INFO("Got GPS Fix! Home pose initialized.");
  }
}

int main(int argc, char **argv)
{   
    bool flag;
    ros::init(argc, argv, "offb_node");
    ros::NodeHandle nh;   

    float hgt;
    if (!(nh.getParam("/takeoff/to_hgt",hgt))){
        hgt = 2.0;     
    }
    
    ros::Subscriber mav_pose_sub = nh.subscribe<geometry_msgs::PoseStamped>
            ("mavros/local_position/pose", 10, mav_pose_cb);
    ros::Subscriber state_sub = nh.subscribe<mavros_msgs::State>
            ("mavros/state", 10, state_cb);
    ros::ServiceClient arming_client = nh.serviceClient<mavros_msgs::CommandBool>
            ("mavros/cmd/arming");
    ros::ServiceClient set_mode_client = nh.serviceClient<mavros_msgs::SetMode>
            ("mavros/set_mode");
    ros::ServiceClient takeoff_client = nh.serviceClient<mavros_msgs::CommandTOL>
            ("mavros/cmd/takeoff");

    //the setpoint publishing rate MUST be faster than 2Hz
    ros::Rate rate(50.0);

    // wait for FCU connection
    while(ros::ok() && !current_state.connected){
        ros::spinOnce();
        rate.sleep();
    }

    mavros_msgs::SetMode offb_set_mode;
    offb_set_mode.request.custom_mode = "GUIDED";

    mavros_msgs::CommandBool arm_cmd;
    arm_cmd.request.value = true;

    ros::Time last_request = ros::Time::now();

    while(ros::ok()){

        if (!gps_ok){
            ROS_WARN("Waiting for GPS Fix!");
            ros::Duration(1).sleep();
        }
        else{
            if( current_state.mode != "GUIDED" &&
            (ros::Time::now() - last_request > ros::Duration(1.0))){
            if( set_mode_client.call(offb_set_mode) &&
                offb_set_mode.response.mode_sent){
                ROS_INFO("GUIDED mode enabled");
            }
            last_request = ros::Time::now();}
            else {
                if( !current_state.armed &&
                    (ros::Time::now() - last_request > ros::Duration(1.0))){
                    if( arming_client.call(arm_cmd) &&
                        arm_cmd.response.success){
                        ROS_INFO("Vehicle armed");
                        flag = true;
                    }

                    last_request = ros::Time::now();

                    if(flag && (ros::Time::now()-last_request < ros::Duration(3))){
                        takeoff_request.request.altitude = hgt;
                        if(takeoff_client.call(takeoff_request)&&(takeoff_request.response.success)){
                            ROS_INFO("Takeoff Service Called!");
                            sleep(1);
                            break;
                        }
                        else{ 
                            ROS_ERROR("Takeoff Failed!");    
                        }
                    }
                    
                }
            }
        }
        ros::spinOnce();
        rate.sleep();
    }
    return 0;
} 