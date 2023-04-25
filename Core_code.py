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

def make_Trips_File(Round_name,net_file,start_edges=[],end_edges=[],dependencies=[],num_trips=-1,use_random_trips=False,maximum_release_time=500,Random_trips=False):
    #Round_name - id for this set of vehicle origin destination matrix.
    #net_file - name of the network
    #start_edges set of valid origins
    #end_edges - set of valid destinations
    #
    if num_trips == -1:
        return
    
    
    
    
    if not os.path.isdir("./configurations/Rounds/"+Round_name):
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
        for x in range(0,num_trips):
            release_times.append(random.randint(0,maximum_release_time)) # 400
        release_times = sorted(release_times)

        #Use this for random trips please.
        if Random_trips or not start_edges:
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
        #data2Csv_Deadlines(deadlines,Round_name) #insert file name into this as argument

        xml_str = root.toprettyxml(indent ="\t") 
        trip_file = "./configurations/Rounds/"+Round_name+'/Trips_File.rou.xml'
        with open(trip_file,"w") as f:
            f.write(xml_str)
            f.flush()
            f.close
        #exit()
       
def run_SUMO(out_dir,x,net_file):
    sumoBinary = sumolib.checkBinary("sumo")
    sumoCmd = [sumoBinary,#from duaiterate
                '--save-configuration',  out_dir +"/%03i"%x+'/myconfig.sumocfg', #/myconfig_0.sumocfg",
                '--log', out_dir +"/%03i"%x+ "/log.sumo.log",
                '--net-file', os.getcwd() + "\\configurations\\maps\\"+net_file,#net_file_temp,# "../../../../../maps/"+net_file,
                '--route-files',out_dir+"/%03i"%x+"/Trips_File_%03i.rou.xml"%x ,#old_directory+'/'+trip_file,
                '--no-step-log',
                '--begin', '0',
                '--summary-output',out_dir +"/%03i"%x+ "/summary.xml",
                '--statistic-output',out_dir+"/%03i"%x+"/stats_output.xml"
                    ]
                #print("the directory:", the_directory)

                #print("SUMOCMD:",sumoCmd)
    subprocess.call(sumoCmd)
    subprocess.call([sumoBinary, "-c", out_dir+"/%03i"%x+'/myconfig.sumocfg', \
                "--tripinfo-output", out_dir+"/%03i"%x+'/trips.trips.xml', \
                "--quit-on-end" ])

def make_Route_file(micro_meso_macro,Round_name,net_file,Num_Iterations):#
    #micro_meso_macro -> 1 micro simulation 2 meso simulation 3 macro simulation
    cmd = []
    if micro_meso_macro == 1: # microscopic

        out_dir= "./configurations/Rounds/"+Round_name+"/Microscopic_DUE"
        if not os.path.isdir(out_dir):
            os.mkdir(out_dir)
            cmd = ["python", "./SUMO_Tools/duaIterate.py", "-t", "./configurations/Rounds/"+Round_name+"/Trips_File.rou.xml",\
                    "-n","./configurations/maps/"+net_file,"-l",str(Num_Iterations)]

            subprocess.call(cmd)        
        for x in range(0,Num_Iterations):
            try:
                shutil.move("%03i"%x,out_dir)
            except Exception:
                pass
            run_SUMO(out_dir,x,net_file)
        for x in range(0,Num_Iterations):
            report("./configurations/Rounds/"+Round_name+'/Microscopic_DUE/%03i'%x, Round_name,x,"duaIterate","Micro-DUE.9.5")
        pass


    if micro_meso_macro == 2: # mesoscopic

        out_dir="./configurations/Rounds/"+Round_name+"/Mesoscopic_DUE"
        if not os.path.isdir(out_dir):
            os.mkdir("./configurations/Rounds/"+Round_name+"/Mesoscopic_DUE")

            cmd = ["python", "./SUMO_Tools/duaIterate.py", "-t", "./configurations/Rounds/"+Round_name+"/Trips_File.rou.xml",\
                    "-n","./configurations/maps/"+net_file,"-l",str(Num_Iterations), "-m"]
            subprocess.call(cmd)

        for x in range(0,Num_Iterations):
            try:
                shutil.move("%03i"%x,"./configurations/Rounds/"+Round_name+"/Mesoscopic_DUE")
            except Exception:
                pass
            run_SUMO(out_dir,x,net_file)
                        
        for x in range(0,Num_Iterations):
            report("./configurations/Rounds/"+Round_name+'/Mesoscopic_DUE/%03i'%x, Round_name,x,"duaIterate","Meso-DUE.9.5")
        pass

    if micro_meso_macro == 3: # macroscopic.
        out_dir = "./configurations/Rounds/"+Round_name+"/Macroscopic_DUE"
        if not os.path.isdir(out_dir):
            os.mkdir(out_dir)

            cmd = ["./SUMO_TOOls/marouter", "-r" , "./configurations/Rounds/"+Round_name+"/Trips_File.rou.xml","-n",\
            "./configurations/maps/"+net_file,"-i",str(Num_Iterations),"-o", out_dir+"/Macro_Routes.xml"]

            subprocess.call(cmd) 
            
            #need to run sumo here...
            run_SUMO(out_dir,x,net_file)
            
        report("./configurations/Rounds/"+Round_name+'/Macroscopic_DUE', Round_name,0,"duaIterate","Macro-DUE.9.5")

    pass
    if micro_meso_macro == 4: # mesoscopic
        out_dir = "./configurations/Rounds/"+Round_name+"/Mesoscopic_SUMO_DUE"
        if not os.path.isdir(out_dir):
            os.mkdir(out_dir)

            cmd = ["python", "./SUMO_Tools/duaIterate.py", "-t", "./configurations/Rounds/"+Round_name+"/Trips_File.rou.xml",\
                    "-n","./configurations/maps/"+net_file,"-l",str(Num_Iterations), "-m"]
            subprocess.call(cmd)

            for x in range(0,Num_Iterations):
                try:
                    shutil.move("%03i"%x,"./configurations/Rounds/"+Round_name+"/Mesoscopic_SUMO_DUE")
                except Exception:
                    pass
                sumoBinary = sumolib.checkBinary("sumo")
                run_SUMO(out_dir,x,net_file)

        for x in range(0,Num_Iterations):
            report("./configurations/Rounds/"+Round_name+'/Mesoscopic_SUMO_DUE/%03i'%x, Round_name,x,"duaIterate","Meso-SUMO-DUE.9.5")
        pass

def report(location, Round_name,iter,run_id,version,deadline_dict={},time=0): #From https://github.com/Local-Coding-Buddy/Recursive-DUE-STR
        
        doc2 = minidom
        #print("location:",location)
        #print("iter:",iter)
        try:
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



        total_travel_time = 0
        max_travel_time = 0
        deadline_overtime = 0
        deadline_misses = 0
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
        temp.append(deadline_misses)
        temp.append(deadline_overtime)
        overall.append(temp)
        csv2Data('./History/results.csv')
        data2Csv_general(overall,'./History/results.csv')

def data2Csv_general(data_selected,directory):
    with open(directory, 'w',newline='') as f:
      
        # using csv.writer method from CSV package
        write = csv.writer(f)
        pushing = []
        #write.writerow(fields)
        if not csv_data:#csv_data global value I should get from a csv2data method
            pushing = data_selected
        else:
            pushing = csv_data+data_selected
        write.writerows(pushing)    
        f.flush()
        f.close    
 

def csv2Data(file_name_and_directory):
    # with open('./history/SUMO_Trips_Data.csv','r') as f2:
    global csv_data
    #global data2Push

    csv_data = []
    #data2Push = []
    #print("is this really blank?",file_name_and_directory)
    with open(file_name_and_directory,'r',encoding='cp932', errors='ignore') as f2:
        reader = csv.reader(f2)
        #print(reader)
        for item in reader:
            #print(item)
            csv_data.append(item)