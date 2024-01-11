# 9th Inter-IIT Tech Meet - DRDO Vision Based MAV Software Stack

Clone the repo to your catkin workspace `src` directory.

Build your workspace.

Add the `models` and `worlds` folders to the `GAZEBO_MODEL_PATH` and `GAZEBO_RESOURCE_PATH` respectively. Also add the `scripts` folder to the PATH env variable in order to make the launch script accessible from anywhere.

Add the following lines to your .bashrc / .zshrc file and **save the changes**. 

``` bash
source <path-to-your-catkin-ws>/devel/setup.bash
export GAZEBO_MODEL_PATH=<path-to-your-catkin-ws>/src/InterIIT/interiit21-drdo-iitm/models:${GAZEBO_MODEL_PATH}
export GAZEBO_RESOURCE_PATH=<path-to-your-catkin-ws>/src/InterIIT/interiit21-drdo-iitm/worlds:${GAZEBO_RESOURCE_PATH}
export PATH=<path-to-your-catkin-ws>/src/InterIIT/interiit21-drdo-iitm/scripts:${PATH}
export PATH=<path-to-ardupilot>/Tools/autotest:${PATH}
```
Replace `<path-to-your-catkin-ws>` by absolute path of your catkin workspace root directory and `<path-to-ardupilot>` with the absolute path to your cloned Ardupilot repo root folder.

Open a new terminal window.

Start the simulation by running:

```bash
run_sim.sh
```

This will launch APM SITL, Gazebo Simulation, Mavros node and RViz. It will also load the custom parameter list located at the `cfg/apm_params/` directory.

To takeoff the drone:

```bash
roslaunch interiit21-drdo-iitm apm_takeoff.launch takeoff_hgt:=<enter_takeoff_height_here>
```






