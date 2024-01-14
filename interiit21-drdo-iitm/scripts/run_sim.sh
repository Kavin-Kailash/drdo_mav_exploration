#!/bin/bash

gnome-terminal -- roslaunch interiit21-drdo sim_main.launch &&
cd ~ && sim_vehicle.py --add-param-file=$(rospack find interiit21-drdo)/cfg/apm_params/default_params.parm -v ArduCopter -f gazebo-iris --mavproxy-args="--streamrate=-1"



