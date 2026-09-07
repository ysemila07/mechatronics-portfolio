%% Initialise robot
% move 'Project' folder to /ARTE-master/robots file
% change the path names below to match your file path to ARTE-master
% run this file -> and you're good to go!

addpath(genpath('/Users/ysemila07/Desktop/Yr 4 Sem 2/ECTE471/ARTE-master')); % add your file path here
global configuration robot
configuration = struct();
configuration.libpath = '/Users/ysemila07/Desktop/Yr 4 Sem 2/ECTE471/ARTE-master'; % add your file path here
configuration.figure.robot = 1;     
%% Run robot
robot = load_robot('Project','robot_arm');
teach