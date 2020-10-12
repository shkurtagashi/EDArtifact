
# EDArtifact_Dashboard 
EDArtifact_Dashboard is a dashboard for labeling physiological signals. It is initially developed to label artifacts in physiological data such as electrodermal activity (EDA). But it can easily be extended to label any other type of signals such as, e.g., blood volume pulse or skin temperature. 

If you use the dashboard or the guidelines for manual labeling of artifacts (Artifacts_Labeling_Instructions.pdf) please cite the paper [1]: 

[1] S. Gashi, E. Di Lascio, B. Stancu, V. Das Swain, V. Mishra, M. Gjoreski, S. Santini: "Detection of Artifacts in Ambulatory Electrodermal Activity Data". In:  Proceedings of the ACM on Interactive, Mobile, Wearable and Ubiquitous Technologies (PACM IMWUT), Vol. 4, Issue 2, June 2020. 31 pages. 

The paper is available at https://dl.acm.org/doi/10.1145/3397316. 

Please do not hesitate to contact us at silvia.santini@usi.ch if you have any questions in general or experience issues with the tool.


## Install Instructions

1. Git clone: https://github.com/shkurtagashi/EDArtifact

2. Install the following `Dash` repositories 

	- pip install dash==1.0.2  
	- pip install dash-daq==0.1.0
	- pip install dash-auth 

3. Move to EDArtifact_Dashboard folder
	- cd /yourpathtofolder/EDArtifact/EDArtifact_Dashboard

4. Create *static* folder inside EDArtifact_Dashboard 

5. Create a CSV file `auth_details.csv` with columns: `username` and `password` and add username and password of your choice. 
Place the file inside static folder.


6. From the terminal run the `dashboard.py` script with the python version you installed the packages 

	- python dashboard.py

7. In browser go to: http://127.0.0.1:8050/ and start using the dashboard

Comment: In case of issues to install. Please first check whether you have the same python version of pip as the default python version. You could do this using:
	- Which pip
	- Which python


## EDArtifact_Dashboard: Technical specifications

EDArtifact_Dashboard was developed using Dash, a Python framework built on top of Flask, Plotly.js, and React.js. It is primarily used for data visualization in web applications. To get familiar with `Dash` you may use the tutorials in https://dash.plot.ly/ and utilize the different `Dash` Core Components presented in https://dash.plot.ly/dash-core-components. 


## EDArtifact_Dashboard: Usage instructions
To start labelling a session you should first upload the data using the Upload button. You will then need to choose one csv file that contains two columns: `EDA_Filtered` and `Time`. To ensure a certain degree of reliability, a backup ﬁle is generated after ﬁnishing the labelling of the first 10-minute window. This allows you to reload it in case of a crash, as well as temporarily stop and continue later, using the Continue labelling button. The backup feature sometimes might not work properly. If you wish to delete all the provided labels in a session and restart labelling the session, you may use the Reset button. If the majority of the segments in a 10-minute window are clean or artifacts you may use the Mark all as clean or Mark all as artifact buttons respectively and then go to specific 5-second windows to change the label. Once you are done you may click the Finish button to save your labels. 

`Label`: Artifact, Clean, Unsure

`Type of artifact`: Abrupt peak /drop, Out of range, Changes quickly, Invalid-left/right, Drops/Rises quickly

Each typee of artifact is defined in the labeling instructions (Artifacts_Labelling_Instructions.pdf).

`Confidence`: the confidence level for the provided label: high, low. Please ignore the confidence. 

### Tips 
-	To make the process easier and faster please use the buttons “Mark all as clean” or “Mark all as artifact” first and then go to more specific 5-second windows to modify the artifact. You can utilize the zoom in/out and pan buttons on the right corner of each plot to make the navigation through the signal easier. 
-	While labelling, the first suggestion is to look at the maximum and minimum value of the EDA signal on the y-axis of 10-min view. In many cases, the difference between the maximum and minimum is less than 0.1 μS, which means they are small fluctuations that should be labels as clean.
-	We highly recommend to mainly use the 10-min view to see whether there are peaks/drops in the signal that seem to be an artifact. To verify it you could zoom in the 10-min window and see whether the peak matches any of the rules above. Only then you should move to the 5-second view to provide the actual label.
-	Be careful and patient with the dashboard because sometimes it might take a few seconds to load the next window and by clicking twice the arrow, the 10-minute window moves twice and labels all the segments in the skipped window as unsure. 
-	When there are more than two artifacts in a window provide as label the artifact type that seems more reasonable to you
-	This blog might also be interesting for you to read  https://support.mindwaretech.com/2017/12/improving-data-quality-eda/#one-more-point


