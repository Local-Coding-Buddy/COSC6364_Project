# COSC6364_Project
 Code used to test Microscopic, Mesoscopic, and Macroscopic routing solutions of Simulation Of Urban MObility (SUMO) (https://github.com/eclipse/sumo).
 
## Contents:
#### Main Directory:

***Files***
- main.py main file with no input settings
- main_for_executable.py main file with custom execution settings see running experiements for details.
- core_code.py contains all nessecary scripts for running route methods and storing the information.
- Sample_inputs.txt holds a list of inptus used for testing in the report and some test inputs you can use

***Folders***
- Configurations: Contains the maps and Rounds folder
	- Maps: holds a set net.xml files with information pertaining to the maps used by SUMO.
		- Note The UH network is the network titled '4corners_neighborhoods.net.xml' , Random Network is 'Random_English.net.xml' and braess is "Braess_Homebrew_fixed1.net.xml"
	- Rounds: holds a large set of information on the trips and routes that each simulation view produced.
	
- Graph Files: Contain the ipynb files that I used to generate the graphs seen in the report. They are also available in HTML format to see the code and the output.
	- Average Travel Time Bar graph: used to make the overall performance bar graphs.
	- Computation time: used to make the computation time bar graphs.
	- Project_report_final: used to make the convergence charts
	- Traffic incidents: used to make the traffic incidents bar graphs.

- Images: Contains images for this readme.

- History: Contains a csv with output of information which is used in the graphs in the paper and presentation. WHEN TESTING PLEASE CHECK THE BOTTOM OF THE CSV FOR RESULTS.

- SUMO_Tools: Contains several SUMO tools that I use to generate routes for vehicles (duaIterate and marouter both mentioned in the report).
	
## Running Experiements:
 
### Requirements: 
- This project using python please make sure to
- Please run this Repository in Windows as this is the only OS I can gaurentee no errors for!!!
- Please ensure all the requirements from the requirements.txt file are installed. You may use the command:
```
 pip3 install -r requirements.txt
```
- Afterward you will need to install SUMO and intialize SUMO_HOME as an environmental variable, the guides for which can be found here:

***Installing SUMO on Windows***
```
https://sumo.dlr.de/docs/Installing/index.html#windows
```

***SUMO_HOME on Windows***
```
https://sumo.dlr.de/docs/Basics/Basic_Computer_Skills.html#sumo_home
```


### Running the Code:


#### Using main.py
***It is recommended to use main_for_executable.py instead***
In the main directory please use the command "python main.py" to run the program using python.
The main variables needed to recreate the tests are "network_file" on line 19, "Round_name_base" on line 20, "round_min" and "round_max" on lines 23 and 24, and "num_iterations" on line 22, . 
- You can change the network used in an experiment by changing the value of "network_file".
- You can change the test ID (name) by modifying the value of "Round_name_base"
- You can change the range of Round to be run by modifying "Round_min" and "round_max".
- You can modifying the number of iterations that duaiterate/marouter run for by modifying the value of "num_iterations".

To compile and run the code you can either use the main.py file or the main_for_executable.py file which includes options.

#### Using main_for_executable.py
Run the file using the command: "python main_for_executable.py"
***Additional options/flags:***
- "-r", "--random", "Use Random assignment of vehicle origins and destination." (boolean)
- "-V","--Number_of_vehicles", "Set the number of vehicles for trip creation, if trips already created has no effect, also better to leave default." (int)
- "-t","--Release_time", "Set the period in which the number of vehicles will be released, if trips already created has no effect, also better to leave default." (int)
- "-I","--Iterations", "Set the number of iterations to be run recommended 5 for testing." (int)
- "-R","--Rounds", "Set the number of rounds to be executed recommend 1 for testing." (int)
- "-n","--network", "Network file please include the .net.xml when selecting a network." (str)
- "-D","--round_ID", "ID to select the setup for a network, basically a name for Origin-Destination setup." (str)

#### Evaluating correctness: 
***Recommended execution***
- Running the main_for_executable file with default settings will have a small test occur with 5 iterations per simulation view.
- You can check the last 15 lines of the results.csv for matching results. 
- I also have a small graph being output but this is not very relavent as this is basically a duplicate in the data. 
- Running main_for_executable.py should run output a graph like the one pictured in the /images/Image_from_default_execution.png
- PLEASE NOTE: COLUMNS A-I SHOULD MATCH IF YOU RUN THE DEFAULT CODE. COLUMN J SHOULD BE DIFFERENT AS YOU ARE RUNNING ON A DIFFERENT COMPUTER.

#### Commands for running tests used on report (INPUT):
***There are 3 network files that I have provided in the configurations/maps folder.***
```
Braess_Homebrew_fixed1.net.xml (braess network)
4corners_neighborhoods.net.xml (UH network)
Random_English.net.xml (Random network)
```
Images of them are provided in the report. 
***WARNING: Please note these tests can take up to 5 hours: ***
```
- python main_for_executable.py -r -I 30 -R 5 -n Braess_Homebrew_fixed1.net.xml -D test
- python main_for_executable.py -I 30 -R 5 -n 4corners_neighborhoods.net.xml -D test
- python main_for_executable.py -I 30 -R 5 -n Random_English.net.xml -D test
```

***Recommened tests *** 
Either run main with the default settings aka: 
```
python main_for_executable.py
```
or set the number of iterations low to soemthing like 5 and the number of rounds to 1 example:
```
python main_for_executable.py -I 5 -R 1 -n 4corners_neighborhoods.net.xml -D TA_test
```
Note that the above test has not actually been created yet so the make_trips() method will be called to actually create the trips for you. 
(Since it's the braess network you should have something comparible to what I had in terms of output.)
	
	
#### Results.csv Format
- Column A denotes the Network + vehicle Id + Round + Iteration number
- Column C denotes the simulation view which is split between Micro-DUE.9.5, Macro-DUE.9.5, Meso-DUE.9.5
- Column D denotes the amount of time the simulation took in simulation time (simulated-seconds).
- Column E denotes the total accumulated travel time of all (simulated-seconds).
- Column F Denotes the average travel time of all vehicles in the network (simulated-seconds).
- Column G denotes the maximum travel time of 1 vehicle in the network
- Column H & I list the number of vehicles and the number of vehicles that finished respectively.
- Column J Denotes the time this particular iteration (in the case of macro) took to execute. Otherwise in the micro and meso case, the amount of time all iterations took to execute (seconds).
- Columns k - O are used to collect data regarding traffic incidents.

#### Running the Executable: 
Since running the executable will still require the installation of SUMO I am ommiting this after gaining permission from Rishabh. I have included a video demo instead. 
## Acknowledgements
A Special thank you to Guangli Dai, Pavan Kumar Plarui, Thomas Carmichael, Albert M. K. Cheng and Risto Miikkulainen for their work on the original STR SUMO repository that this code is based on.
https://github.com/guangli-dai/Selfless-Traffic-Routing-Testbed

