# COSC6364_Project
 Code used to test Microscopic, Mesoscopic, and Macroscopic routing solutions of Simulation Of Urban MObility (SUMO) (https://github.com/eclipse/sumo).
 
## Contents:
 
## Running Experiements:
 
### Requirements: 
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
In the main directory please use the command "python main.py" to run the program using python.
The main variables needed to recreate the tests are "network_file" on line 19, "Round_name_base" on line 20, "round_min" and "round_max" on lines 23 and 24, and "num_iterations" on line 22, . 
- You can change the network used in an experiment by changing the value of "network_file".
- You can change the test ID (name) by modifying the value of "Round_name_base"
- You can change the range of Round to be run by modifying "Round_min" and "round_max".
- You can modifying the number of iterations that duaiterate/marouter run for by modifying the value of "num_iterations".

#### Running the Executable: 
TODO create executable.
## Acknowledgements
A Special thank you to Guangli Dai, Pavan Kumar Plarui, Thomas Carmichael, Albert M. K. Cheng and Risto Miikkulainen for their work on the original STR SUMO repository that this code is based on.
https://github.com/guangli-dai/Selfless-Traffic-Routing-Testbed

