import os
import sys
import copy
import random
import time
import shutil
from xml.dom import minidom
from datetime import datetime
import sumolib
import subprocess
import csv  

if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("No environment variable SUMO_HOME!")

csv_data = []
#data2Push = [] #new data aquired that will be pushed
# creates the trips for each round. Trips in this case are the vehicles their departure time, and their origin and destination.
def make_Trips_File(Round_name,net_file,start_edges=[],end_edges=[],dependencies=[],num_trips=-1,use_random_trips=False,maximum_release_time=500):
    if num_trips == -1: # if no number of trips given.
        return
    #creating the round directory and trip information
    if not os.path.isdir("./configurations/Rounds/"+Round_name):#if there does not aleady exist trips for the round
        os.mkdir("./configurations/Rounds/"+Round_name)
        vehicle_dict = {}
        root = minidom.Document()#creating xml file
        xml = root.createElement('routes')
        xml.setAttribute('xmlns:xsi','"http://www.w3.org/2001/XMLSchema-instance"')
        xml.setAttribute('xsi:noNamespaceSchemaLocation','"http://sumo.dlr.de/xsd/routes_file.xsd"')
        root.appendChild(xml)


        # release times have to be sorted in the route file.
        release_times =[]
        for x in range(0,num_trips):
            release_times.append(random.randint(0,maximum_release_time)) # getting random release times.
        release_times = sorted(release_times)

        #Use this for random trips please.
        if use_random_trips or not start_edges: #random origin-destination generation.
            net = sumolib.net.readNet('./configurations/maps/'+net_file)
            edges = net.getEdges()
            start_edges = []
            end_edges = []
            dependencies = {}
            for current_edge in edges:
                current_edge_id = current_edge.getID()
                
                # add edge to edge list if it allows passenger vehicles
                # "passenger" is a SUMO defined vehicle class
                if current_edge.allows("passenger"):
                    start_edges.append(current_edge_id)
                    end_edges.append(current_edge_id)
                    dependencies[current_edge_id] = [current_edge_id]#to prevent trips to and from the same edge aka very short trips

        for x in range(0,num_trips):#generation of random origins and destinations
             
            start_iterator = random.randint(0,len(start_edges)-1)
            start_edge = start_edges[start_iterator]
            while True:# ensuring that no vehicle has the same origin and destination.
                end_iterator = random.randint(0,len(end_edges)-1)
                end_edge = end_edges[end_iterator]
                if start_edge in dependencies.keys(): # this should allow for the format of edge dependencies to be much easier.
                    if end_edge not in dependencies[start_edge]:
                        break
            # building the xml file this is for 1 vehicle
            child = root.createElement('trip')
            child.setAttribute('id',str(x+2))
            child.setAttribute('depart',str(release_times[x]))
            child.setAttribute('from',str(start_edge))
            child.setAttribute('to',str(end_edge))

            xml.appendChild(child)
            
        # writing the trips files to the rounds _folder.
        xml_str = root.toprettyxml(indent ="\t") 
        trip_file = "./configurations/Rounds/"+Round_name+'/Trips_File.rou.xml'
        with open(trip_file,"w") as f:
            f.write(xml_str)
            f.flush()
            f.close
        #exit()
       
def run_SUMO(out_dir,x,net_file): #x here is the iteration number
    # this entire function is run by all 3 views for each iteration in order to have an even set of circumstances when comparing results
    sumoBinary = sumolib.checkBinary("sumo")
    sumoCmd = [sumoBinary,#from duaiterate.py seting up command to call sumo
                '--save-configuration',  out_dir +"/%03i"%x+'/myconfig.sumocfg', #/myconfig_0.sumocfg",
                '--log', out_dir +"/%03i"%x+ "/log.sumo.log",
                '--net-file', os.getcwd() + "\\configurations\\maps\\"+net_file,#net_file_temp,# "../../../../../maps/"+net_file,
                '--route-files',out_dir+"/%03i"%x+"/Trips_File_%03i.rou.xml"%x ,#old_directory+'/'+trip_file,
                '--no-step-log',
                '--begin', '0',
                '--summary-output',out_dir +"/%03i"%x+ "/summary.xml",
                '--statistic-output',out_dir+"/%03i"%x+"/stats_output.xml"
                    ]
    subprocess.call(sumoCmd)
    subprocess.call([sumoBinary, "-c", out_dir+"/%03i"%x+'/myconfig.sumocfg', \
                "--tripinfo-output", out_dir+"/%03i"%x+'/trips.trips.xml', \
                "--quit-on-end" ])

def make_Route_file(micro_meso_macro,Round_name,net_file,Num_Iterations):# code for running the 3 views
    # creating the route files
    cmd = []
    if micro_meso_macro == 1: # microscopic view
        #
        out_dir= "./configurations/Rounds/"+Round_name+"/Microscopic_DUE" # output directory
        if not os.path.isdir(out_dir):
            os.mkdir(out_dir)

        #Need to run these each time in order to get computation time. #Will overwrite results!!!!
        #running SUMO tool duaIterate
        cmd = ["python", "./SUMO_Tools/duaIterate.py", "-t", "./configurations/Rounds/"+Round_name+"/Trips_File.rou.xml",\
                "-n","./configurations/maps/"+net_file,"-l",str(Num_Iterations)] #command using duaIterate.py
        c_time = time.time()# calculating time
        subprocess.call(cmd)#execution of iterative process
        c_time = time.time()-c_time        
        for x in range(0,Num_Iterations): 
            #the output folders will dispence themselves in the main directory so this moves them to the output directory for storage.
            try:
                #currently set to overwrite any already existing solution (solution will be the same as long as random number is the same can just leave at default)
                if os.path.isdir(out_dir+"/%03i"%x): 
                    shutil.rmtree(out_dir+"/%03i"%x)
                shutil.move("%03i"%x,out_dir)
            except Exception:
                pass
            run_SUMO(out_dir,x,net_file)
        for x in range(0,Num_Iterations):recording data and writing it to the results.csv file
            report("./configurations/Rounds/"+Round_name+'/Microscopic_DUE/%03i'%x, Round_name,x,"duaIterate","Micro-DUE.9.5",time = c_time)
        pass


    if micro_meso_macro == 2: # mesoscopic

        out_dir="./configurations/Rounds/"+Round_name+"/Mesoscopic_DUE"
        if not os.path.isdir(out_dir):
            os.mkdir("./configurations/Rounds/"+Round_name+"/Mesoscopic_DUE")
        #Need to run these each time in order to get computation time. #Will overwrite results!!!!
        #Running SUMO tool duaIterate.
        cmd = ["python", "./SUMO_Tools/duaIterate.py", "-t", "./configurations/Rounds/"+Round_name+"/Trips_File.rou.xml",\
                "-n","./configurations/maps/"+net_file,"-l",str(Num_Iterations), "-m"] # same command as micro but with the -m flag for mesoscopic view
        c_time = time.time()
        subprocess.call(cmd)
        c_time = time.time()-c_time  

        for x in range(0,Num_Iterations): 
            #the output folders will dispence themselves in the main directory so this moves them to the output directory for storage.
            try:
                #currently set to overwrite any already existing solution (solution will be the same as long as random number is the same can just leave at default)
                if os.path.isdir(out_dir+"/%03i"%x):
                    shutil.rmtree(out_dir+"/%03i"%x)

                shutil.move("%03i"%x,"./configurations/Rounds/"+Round_name+"/Mesoscopic_DUE")
            except Exception:
                pass
            run_SUMO(out_dir,x,net_file)# running sumo on all iterations so that the output is comparable
                        
        for x in range(0,Num_Iterations): #recording data and writing it to the results.csv file
            report("./configurations/Rounds/"+Round_name+'/Mesoscopic_DUE/%03i'%x, Round_name,x,"duaIterate","Meso-DUE.9.5",time = c_time)
        pass

    #macroscopic
    if micro_meso_macro == 3: # macroscopic.
        out_dir = "./configurations/Rounds/"+Round_name+"/Macroscopic_DUE"
        if not os.path.isdir(out_dir):
            os.mkdir(out_dir)
            
        #Need to run these each time in order to get computation time. #Will overwrite results!!!!
        for x in range(0,Num_Iterations):
            try:
                os.mkdir("%03i"%x)
                if os.path.isdir(out_dir+"/%03i"%x):
                    shutil.rmtree(out_dir+"/%03i"%x)
                
            except Exception:
                pass
            #Using SUMO tool marouter
            cmd = ["./SUMO_TOOls/marouter", "-r" , "./configurations/Rounds/"+Round_name+"/Trips_File.rou.xml","-n",\
            "./configurations/maps/"+net_file,"-i",str(x+1),"-o", "./%03i"%x+'/Trips_File_%03i.rou.xml'%x]
            #generating marouter command
            c_time = time.time()# recording execution/computaiton time.
            subprocess.call(cmd)#running marouter
            c_time = time.time()-c_time  
            shutil.move("%03i"%x,"./configurations/Rounds/"+Round_name+"/Macroscopic_DUE")    
            #need to run sumo here...
            run_SUMO(out_dir,x,net_file)# running sumo on all iterations so that the output is comparable
                
            report("./configurations/Rounds/"+Round_name+'/Macroscopic_DUE/%03i'%x, Round_name,x,"duaIterate","Macro-DUE.9.5",time = c_time)

    pass

    
def report(location, Round_name,iter,run_id,version,deadline_dict={},time=0): #From https://github.com/Local-Coding-Buddy/Recursive-DUE-STR
        #function used to record and write data to csv file 
        
        doc2 = minidom
        try:# will need 3 output files the summary file, stats_output (traffic incidents) and the trips file
            doc2 = minidom.parse(location+'/summary.xml')
        except Exception as e:
            #print("exception 2:",e)
            try: 
                doc2 = minidom.parse(location+'/summary_%03i.xml'%iter)
            except Exception as e:
                #print("exception 2:",e)
                pass
            pass
        step_info = doc2.getElementsByTagName("step")
        last_entry = step_info[len(step_info)-1]
        #print(last_entry)
        total_timespan = last_entry.getAttribute("time") #getting the time of the last entry to the time it took to run.
        #print(total_timespan)
        vehicles_finished = float(last_entry.getAttribute("arrived")) #number of vehicles to finish.
        doc = minidom
        try:
            doc = minidom.parse(location+'/trips.trips.xml')
        except Exception:
            try: 
                doc = minidom.parse(location+'/trips_%03i.trips.xml'%iter)
            except Exception:
                try: 
                    doc = minidom.parse(location+'/tripinfo_%03i.xml'%iter)
                except Exception:
                    pass
        pass

        trip_infos = doc.getElementsByTagName("tripinfo")

        try:
            doc = minidom.parse(location+'/stats_output.xml')
        except Exception:
            pass

        Teleports = doc.getElementsByTagName("teleports")
        Safety = doc.getElementsByTagName("safety")
        #parsing information from output files
        total_travel_time = 0
        max_travel_time = 0
        for x in trip_infos:
            veh_id= float(x.getAttribute("id"))
            veh_fin = float(x.getAttribute("arrival"))
            tt =  float(x.getAttribute("duration"))
            total_travel_time += tt
            if tt > max_travel_time:
                max_travel_time = tt

        round_name_temp = Round_name
        if iter>-1:    
            round_name_temp += '-Iteration-'+str(iter)
        # aggregating all information for output to the results.csv file
        average_travel_time = total_travel_time/len(trip_infos)
        temp = []
        overall = []
        temp.append(round_name_temp)
        temp.append(run_id)
        temp.append(version)
        temp.append(total_timespan)
        temp.append(total_travel_time)
        temp.append(average_travel_time)
        temp.append(max_travel_time)
        temp.append(len(trip_infos))
        temp.append(vehicles_finished)
        temp.append(time)
        temp.append(Teleports[0].getAttribute("jam"))
        temp.append(Teleports[0].getAttribute("yield"))
        temp.append(Teleports[0].getAttribute("wrongLane"))
        temp.append(Safety[0].getAttribute("collisions"))
        temp.append(Safety[0].getAttribute("emergencyStops"))
        overall.append(temp)
        csv2Data('./History/results.csv') # getting data from results.csv
        data2Csv_general(overall,'./History/results.csv') #writing data to results.csv

def data2Csv_general(data_selected,directory): 
    with open(directory, 'w',newline='') as f:
        global csv_data
        # using csv.writer method from CSV package
        # literally just used to write data I get from report to results.csv
        write = csv.writer(f)
        pushing = []
        if not csv_data:#csv_data global value I should get from a csv2data method
            pushing = data_selected
        else:
            pushing = csv_data+data_selected
        write.writerows(pushing)    
        f.flush()
        f.close    
 

def csv2Data(file_name_and_directory):
    global csv_data
    #reading csv data from file to be added onto in report and the data2Csv method
    csv_data = []
    with open(file_name_and_directory,'r',encoding='cp932', errors='ignore') as f2:
        reader = csv.reader(f2)
        for item in reader:
            csv_data.append(item)