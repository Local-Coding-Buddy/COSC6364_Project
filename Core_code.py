import os
import sys
import copy
import random
import time
import xml.etree.ElementTree as ET
from xml.dom.minidom import parse, parseString
from Route_setup.Make_Trips_file import *
from datetime import datetime
import sumolib
import winsound
from core.SUMO_Execute import *

if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("No environment variable SUMO_HOME!")


def make_Trips_File(Round_name,net_file,start_edges,end_edges,dependencies,num_trips,use_random_trips):
    #Round_name - id for this set of vehicle origin destination matrix.
    #net_file - name of the network
    #start_edges set of valid origins
    #end_edges - set of valid destinations
    #
    if num_trips == -1:
        return
    cwd = os.getcwd()
    
    if not os.path.isdir("./configurations/rounds/"+Round_name):
        os.mkdir("./configurations/Rounds/"+Round_name)
        #file_name = "str_sumo.rou.xml" # this should stay the same shouldn't have to change to dynamic I believe
        vehicle_dict = {}
        root = minidom.Document()
        xml = root.createElement('routes')
        xml.setAttribute('xmlns:xsi','"http://www.w3.org/2001/XMLSchema-instance"')
        xml.setAttribute('xsi:noNamespaceSchemaLocation','"http://sumo.dlr.de/xsd/routes_file.xsd"')
        root.appendChild(xml)


        # release times have to be sorted in the route file.
        release_times =[]
        #TODO look into how random.randint generates trips.
        

        #Use this for random trips please.
        if not start_edges:
            net = sumolib.net.readNet('./configurations/maps/'+net_file)
            edges = net.getEdges()
            for current_edge in edges:
                current_edge_id = current_edge.getID()
                
                # add edge to edge list if it allows passenger vehicles
                # "passenger" is a SUMO defined vehicle class
                if current_edge.allows("passenger"):
                    start_edges.append(current_edge_id)
                    end_edges.append(current_edge_id)
                    dependencies[current_edge_id] = [current_edge_id]#to prevent trips to and from the same edge aka very short trips

        for x in range(0,num_trips):
            
            start_iterator = random.randint(0,len(start_edges)-1)
            start_edge = start_edges[start_iterator]
            while True:
                end_iterator = random.randint(0,len(end_edges)-1)
                end_edge = end_edges[end_iterator]
                if start_edge in dependencies.keys(): # this should allow for the format of edge dependencies to be much easier.
                    if end_edge not in dependencies[start_edge]:
                        break
            
            child = root.createElement('trip')
            child.setAttribute('id',str(x+2))
            child.setAttribute('depart',str(release_times[x]))
            child.setAttribute('from',str(start_edge))
            child.setAttribute('to',str(end_edge))

            xml.appendChild(child)
            
            #v_now = Util.Vehicle(str(x+2),start_edge, end_edge, float(release_times[x]), int(ddl_now))

            
            #vehicle_dict[str(x+2)]=v_now
        #print("why are you empty:",deadLines2Push)
        data2Csv_Deadlines(deadlines,Round_name) #insert file name into this as argument

        xml_str = root.toprettyxml(indent ="\t") 
        trip_file = "./configurations/Rounds/"+Round_name+'/Trips_File.rou.xml'
        with open(trip_file,"w") as f:
            #print(xml_str)
            f.write(xml_str)
            f.flush()
            f.close
        duaBinary = sumolib.checkBinary("duarouter")
        
       
    