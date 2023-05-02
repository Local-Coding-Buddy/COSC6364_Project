import os
import sys
import copy
import random
import time
from datetime import datetime
import sumolib
from Core_code import *
import argparse
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("No environment variable SUMO_HOME!")

#input parameters 
parser = argparse.ArgumentParser(description = 'Inputs.')

parser.add_argument("-r", "--random", action="store_true",
                           default=False, help="Use Random assignment of vehicle origins and destination.")

parser.add_argument("-V","--Number_of_vehicles", 
type=int, default =1000, help ="Set the number of vehicles for trip creation, if trips already created has no effect, also better to leave default.")

parser.add_argument("-t","--Release_time", 
type=int, default =1000, help ="Set the period in which the number of vehicles will be released, if trips already created has no effect, also better to leave default.")

parser.add_argument("-I","--Iterations", 
type=int, default =5, help ="Set the number of iterations to be run recommended 5 for testing.")

parser.add_argument("-R","--Rounds", 
type=int, default =1, help ="Set the number of rounds to be executed recommend 1 for testing.")

parser.add_argument("-n","--network", type=str,
 default ="Braess_Homebrew_fixed1.net.xml", help ="Network file please include the .net.xml when selecting a network.")

parser.add_argument("-D","--round_ID", type=str,
 default ="small_test", help ="ID to select the setup for a network, basically a name for Origin-Destination setup.")
args = parser.parse_args()
#sources:
#From https://github.com/Local-Coding-Buddy/Recursive-DUE-STR
#https://github.com/eclipse/sumo

#all input hyper parameters
network_file =args.network#'Braess_Homebrew_fixed1.net.xml'#"Braess_Homebrew_fixed1.net.xml" #'4corners_neighborhoods.net.xml'#'Random_English.net.xml'#"Braess_Homebrew_fixed1.net.xml"#"4corners_neighborhoods.net.xml" #Avenue_E_stafford_Texas.net.xml
Round_name_base =args.round_ID#'small_test'# "On_Project"#be sure to add _Random here if you want to use the random trips 
#(not a requirement just to keep track of which trips were generated randomly)
num_iterations = args.Iterations
round_min = 0 
round_max = args.Rounds
use_micro = True #False #run the microscopic view
use_meso = True#run the mesoscopic view
use_macro = True#run the macroscopic view
Number_of_vehicles = args.Number_of_vehicles #number of vehicles when creating new trip files (rounds).
Random_trips = args.random # use random trip assignment otherwise specifiy edges in start_edges and end_edges
MRT = args.Release_time # Maximum Release time if not
#for building new trip files (rounds).
start_edges = []
end_edges = []
edge_dependencies = {}

if network_file == 'Braess_Homebrew_fixed1.net.xml': #by default will use these edges for braess network.
    start_edges = ["E0"]
    end_edges = ["E3"]
    edge_dependencies = {"E0":[]}
elif network_file == '4corners_neighborhoods.net.xml': #by default will use these edges for the UH network
    start_edges = ["597602756#0","-260998164#3","105681660#12","597602753#0","422688973","918280985","422685671#2",\
    "318908683#0"]
    end_edges = ["-597602756#0","260998164#0","-105681660#20","-597602753#1","422688976#1","918280984",\
    "15374898#0-AddedOffRampEdge","-318908683#1"]
    edge_dependencies = {"597602756#0":["-597602756#0"],"-260998164#3":["260998164#0"],"105681660#12":["-105681660#20"],\
    "597602753#0":["-597602753#1"],"422688973":["422688976#1","918280984"],"918280985":["422688976#1","918280984"],\
    "422685671#2":["15374898#0-AddedOffRampEdge","-318908683#1"],"318908683#0":["15374898#0-AddedOffRampEdge","-318908683#1"]}

else:#other wise random
    Random_trips = True

if Random_trips or not start_edges: #for identifying rounds
    Round_name_base +="_R"


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

        #exit()
        if use_micro:
            make_Route_file(1,Round_name,network_file,num_iterations)

        if use_meso :
            make_Route_file(2,Round_name,network_file,num_iterations)

        if use_macro:
            make_Route_file(3,Round_name,network_file,num_iterations)



directory = os.getcwd()
df = pd.read_csv("./History/results.csv")
#code block for generating a convergence chart from what just ran.
base_name =  network_file +"-"+Round_name_base+"-"
criteria = 'Average_travel_Time'#"Deadline Misses" # should literally be called criterion lmao


lst = ['Micro-DUE.9.5', 'Meso-DUE.9.5', 'Macro-DUE.9.5']
range_min = 0
range_max = round_max

iterations = num_iterations
for i in range(range_min,range_max):#number of tests
    data_results = []
    for i3 in range(0,len(lst)):#number of models
        data_results.append([])
    cnt = 0

    for i4 in lst:
        
        for i2 in range(0,iterations):#number of iterations.
            working_name_SE = base_name + str(i)+"-Iteration-" + str(i2)# remember with my method I start at 1
            x=df[criteria].loc[(df['Version']==i4)&(df['Round_name']==working_name_SE)]
            if len(x.values) > 0:
                data_results[cnt].append(x.values[0])
        cnt+=1
    print(data_results)
    plt.xlabel('Iteration')
    plt.ylabel(criteria+" (Seconds)")
    plt.title("Round "+str(i)+" For Network: "+str(network_file))
    cnt = 0
    for i4 in lst:
        
        plt.plot(data_results[cnt],label=i4,linewidth = 7.5)
        cnt+=1
    plt.xticks(np.arange(0,iterations+1,10), np.arange(0,iterations+1,10))
    plt.legend()
    plt.grid()
    plt.show()    