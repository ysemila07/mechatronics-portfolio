% Parameter file for robot_arm
function robot = parameters()

robot.name = 'robot_arm';

% Path under ARTE's robots/ tree
robot.path = 'Project/robot_arm';

% DH table (in meters and rad)
robot.DH.theta = '[pi/2 -pi/2 0 q(4)-pi/2 q(5)]';
robot.DH.d     = '[q(1)+0.63  q(2)+3.64 q(3)+1.75 0 0.08]';   
robot.DH.a     = '[0             0          0.02   0  0  ]';  
robot.DH.alpha = '[pi/2  pi/2  -pi   -pi/2  0   ]';

% DH table: without the 'home' offsets' to obtain the same Jacobian matrix
% as Section A
%robot.DH.theta = '[pi/2 -pi/2 0 q(4) q(5)]';          % Remove -pi/2 offset
%robot.DH.d     = '[q(1)  q(2) q(3) 0 0.08]';          % Remove constant offsets
%robot.DH.a     = '[0     0     0.02   0  0  ]';       % Keep 0.02m for joint 3
%robot.DH.alpha = '[pi/2  pi/2  -pi   -pi/2  0   ]';   % No change required

% Jacobian placeholder (ARTE fills)
robot.J = [];

% IK/DK function handles
robot.inversekinematic_fn = 'inversekinematic_robot_arm(robot,T)';
robot.directkinematic_fn  = 'directkinematic(robot, q)';

% Robot structure
robot.DOF  = 5;
robot.kind = ['T','T','T','R','R'];   % 3 prismatic, 2 revolute

% Robot limits (in meters and radians)
% For prismatic joints, 'teach' confuses the length and still converts all
% values to degrees, therefore the distances are presented in rad here.
robot.maxangle = [ deg2rad(-0.630) 0;
                   deg2rad(-3.640) 0;   
                   deg2rad(-1.750) 0;  
                  -pi/2    pi/2;  
                  -pi      2*pi ];

% Robot velocities
robot.velmax = [ deg2rad(0.50);           
                 deg2rad(0.50);         
                 deg2rad(0.20);          
                 deg2rad(150);   
                 deg2rad(120) ]; 

robot.accelmax = robot.velmax/0.1;   % simple accel profile assumption

% End-effector max linear speed (choose one value)
robot.linear_velmax = 2.5;

% Base frame
robot.T0 = eye(4);

% init sim variables
robot = init_sim_variables(robot);

% Robot graphics
robot.graphical.has_graphics    = 1;
robot.graphical.color           = [255 20 40]./255;
robot.graphical.draw_transparent= 0;
robot.graphical.draw_axes       = 1;
robot.graphical.axes_scale      = 1;
robot.axis = [-3 3 -3 3 0 3];

robot = read_graphics(robot);

% Robot dynamics
robot.has_dynamics = 0;

end