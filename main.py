import os
import sys
import copy
import random
import time
from datetime import datetime
import sumolib
from Core_code import *

if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("No environment variable SUMO_HOME!")

#sources:
#From https://github.com/Local-Coding-Buddy/Recursive-DUE-STR
#
network_file = "4corners_neighborhoods.net.xml" #Avenue_E_stafford_Texas.net.xml
Round_name_base = "test"#be sure to add _Random here if you want to use the random trips 
#(not a requirement just to keep track of which trips were generated randomly)
num_iterations = 5
round_min = 0
round_max = 1
use_micro = True
use_meso = True # TODO This might need some work aka run it on SUMO
use_meso_SUMO = True # run results through SUMO to ensure accuracy 
use_macro = True
#use_macro_SUMO = False
Number_of_vehicles = 1000
Random_trips = True

MRT = 1000 # Maximum Release time if not


start_edges = ["597602756#0","-260998164#3","105681660#12","597602753#0","422688973","918280985","422685671#2",\
"318908683#0"]
end_edges = ["-597602756#0","260998164#0","-105681660#20","-597602753#1","422688976#1","918280984",\
"15374898#0-AddedOffRampEdge","-318908683#1"]
edge_dependencies = {"597602756#0":["-597602756#0"],"-260998164#3":["260998164#0"],"105681660#12":["-105681660#20"],\
"597602753#0":["-597602753#1"],"422688973":["422688976#1","918280984"],"918280985":["422688976#1","918280984"],\
"422685671#2":["15374898#0-AddedOffRampEdge","-318908683#1"],"318908683#0":["15374898#0-AddedOffRampEdge","-318908683#1"]}
if Random_trips or not start_edges:
    Round_name_base +="_Random"

if __name__ == "__main__":
    #code from https://github.com/Local-Coding-Buddy/Recursive-DUE-STR
    
    #sumo_binary = checkBinary('sumo')#'sumo-gui' or # 'sumo'
    for increment in range(round_min,round_max): #,control_v,
        sufix = increment
        print("NUMBA ",increment)
        Round_name=Round_name_base
        Round_name = network_file +"-"+Round_name+"-"+str(increment)
        print("Round name:",Round_name)


    #make_Trips_File(Round_name,network_file,start_edges,end_edges,dependencies,num_trips=-1,use_random_trips=False):
        if not os.path.exists("./configurations/rounds/"+Round_name):  
            make_Trips_File(Round_name,network_file,start_edges,end_edges,edge_dependencies,num_trips=Number_of_vehicles,use_random_trips= Random_trips,maximum_release_time=MRT )#start_edges,end_edges,edge_dependencies,num_v,Round_name,network_file,maximum_release_time)

   # exit()
        if use_micro:
            make_Route_file(1,Round_name,network_file,num_iterations)

        if use_meso :
            make_Route_file(2,Round_name,network_file,num_iterations)

        if use_macro:
            make_Route_file(3,Round_name,network_file,num_iterations)

        if use_meso_SUMO:
            make_Route_file(4,Round_name,network_file,num_iterations)

      
    

    #todo fix random trips 
    #todo figure out marouter if there is a summary output otherwise use SUMO to get travel time estimation.