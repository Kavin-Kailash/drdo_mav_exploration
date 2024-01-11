#!/bin/bash

gnome-terminal -- roslaunch interiit21-drdo-iitm sim_main.launch &&

cd $APM_HOME/ArduCopter/ && sim_vehicle.py --add-param-file=$(rospack find interiit21-drdo-iitm)/cfg/apm_params/default_params.parm -v ArduCopter -f gazebo-iris --mavproxy-args="--streamrate=-1"
