%% Question 7: Jacobian Matrix Analysis
clear; clc;

% First run the robot initialization
addpath(genpath('PROJECT\ARTE\ARTE-master\ARTE-master'));
global configuration robot

% Initialize configuration properly
configuration = struct();
configuration.libpath = 'PROJECT\ARTE\ARTE-master\ARTE-master';
configuration.figure = struct();
configuration.figure.robot = 1;  

% Load the robot 
robot = load_robot('Project','robot_arm');

% Turn off graphics to prevent figure errors
robot.graphical.has_graphics = 0;

%% Question 7: Jacobian for M3 Screw Operations
disp('=== QUESTION 7: JACOBIAN MATRIX ANALYSIS ===');

% Define joint configurations
q_pick_screw = [0.562, 1.750, -1.750, 0, 0];  
q_deposit_screw = [0.562, 2.770, -0.250, 0, 0]; 

% Calculate Jacobians
J_pick = manipulator_jacobian(robot, q_pick_screw);
J_deposit = manipulator_jacobian(robot, q_deposit_screw);

% Display results
fprintf('Joint configuration when PICKING screw:\n');
fprintf('q = [%.3f, %.3f, %.3f, %.3f, %.3f]\n\n', q_pick_screw);

disp('Jacobian Matrix (6x5) when PICKING M3 screw:');
disp(J_pick);

fprintf('\nJoint configuration when DEPOSITING screw:\n');
fprintf('q = [%.3f, %.3f, %.3f, %.3f, %.3f]\n\n', q_deposit_screw);

disp('Jacobian Matrix (6x5) when DEPOSITING M3 screw:');
disp(J_deposit);

% Analyze singularity
fprintf('\n=== SINGULARITY ANALYSIS ===\n');
rank_pick = rank(J_pick(1:3,:)); 
rank_deposit = rank(J_deposit(1:3,:));

fprintf('Rank of position Jacobian (pick): %d/3\n', rank_pick);
fprintf('Rank of position Jacobian (deposit): %d/3\n', rank_deposit);

if rank_pick == 3
    fprintf('Robot is NOT singular at pick position\n');
else
    fprintf('Robot is SINGULAR at pick position\n');
end

if rank_deposit == 3
    fprintf('Robot is NOT singular at deposit position\n');
else
    fprintf('Robot is SINGULAR at deposit position\n');
end

% Tool positions for reference
T_pick = directkinematic(robot, q_pick_screw);
T_deposit = directkinematic(robot, q_deposit_screw);
fprintf('\nTool Position when picking: [%.3f, %.3f, %.3f] m\n', T_pick(1:3,4));
fprintf('Tool Position when depositing: [%.3f, %.3f, %.3f] m\n', T_deposit(1:3,4));
