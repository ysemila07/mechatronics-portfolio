%% Question 6: Derive Kinematic Model using ARTE
clear; clc;

% Initialize ARTE
addpath(genpath('D:\MD\Study\UOW\FY\ECTE471\PROJECT\ARTE\ARTE-master\ARTE-master'));
global configuration robot
configuration = struct();
configuration.libpath = 'D:\MD\Study\UOW\FY\ECTE471\PROJECT\ARTE\ARTE-master\ARTE-master';
configuration.figure = struct();
configuration.figure.robot = 1;

% Load the robot
robot = load_robot('Project','robot_arm');
robot.graphical.has_graphics = 0;

%% Derive Kinematic Model
disp('QUESTION 6: DERIVE KINEMATIC MODEL USING ARTE');

% test values
q = [0.3, 1.0, -0.8, 0, 0];
fprintf('Using test configuration: q = [%.1f, %.1f, %.1f, %.1f, %.1f]\n', q);

% extract DH parameters
fprintf('\nDH Parameters:\n');
fprintf('Theta: %s\n', robot.DH.theta);
fprintf('d:     %s\n', robot.DH.d);
fprintf('a:     %s\n', robot.DH.a);
fprintf('Alpha: %s\n', robot.DH.alpha);

% calculate transformation matrices
Theta = eval(robot.DH.theta);
d = eval(robot.DH.d);
a = eval(robot.DH.a);
alpha = eval(robot.DH.alpha);

% calculate and display T01, T12, T23, T34, T45
T01 = dh(Theta(1), d(1), a(1), alpha(1));
fprintf('T01 (Base to Joint 1):\n'); 
disp(T01);

T12 = dh(Theta(2), d(2), a(2), alpha(2));
fprintf('T12 (Joint 1 to Joint 2):\n'); 
disp(T12);

T23 = dh(Theta(3), d(3), a(3), alpha(3));
fprintf('T23 (Joint 2 to Joint 3):\n'); 
disp(T23);

T34 = dh(Theta(4), d(4), a(4), alpha(4));
fprintf('T34 (Joint 3 to Joint 4):\n'); 
disp(T34);

T45 = dh(Theta(5), d(5), a(5), alpha(5));
fprintf('T45 (Joint 4 to Joint 5):\n'); 
disp(T45);

% calculate and display T05
T05 = T01 * T12 * T23 * T34 * T45;

fprintf('\nFinal Transformation Matrix T05:\n');
disp(T05);
