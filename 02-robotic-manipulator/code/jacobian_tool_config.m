% tool configuration vector (pos + (q5/pi)*approach) and its Jacobian
% Robot: 5-DOF with STANDARD DH and joints: P P P R R
% DH from your table: a=[0 0 0 0 0], alpha=[+90 +90 -90 -90 0] deg,
% d=[q1 q2 q3 0 -0.080] m, theta=[0 0 0 q4 q5] rad.

clc; clear; close all;
deg = pi/180;

%  Symbolic joint variables
syms q1 q2 q3 q4 q5 real
q = [q1 q2 q3 q4 q5];

L5 = 0.080;          % |d5| = 0.080 m  (note d5 = -L5 below)

% Standard DH: rows [a, alpha, d, theta]
DH = [ 0, +90*deg, q1,      0;
       0, +90*deg, q2,      0;
       0, -90*deg, q3,      0;
       0, -90*deg, 0,      q4;
       0,   0*deg, -L5,    q5 ];


T = sym(eye(4));
for i = 1:size(DH,1)
    T = T * dhA(DH(i,1), DH(i,2), DH(i,3), DH(i,4));
end
T = simplify(T);

% Position and approach (tool z-axis)
p = simplify(T(1:3,4));          % [x; y; z]
R = T(1:3,1:3);
a = simplify(R(:,3));            % approach vector

% Tool configuration vector: [p; (q5/pi)*a]
xi = simplify([ p; (q5/pi)*a ]);

% Tool-configuration Jacobian: J = d xi / d q
J = simplify(jacobian(xi, q));

% Display (symbolic)
disp('Tool configuration vector  xi = [x; y; z; (q5/pi)*ax; (q5/pi)*ay; (q5/pi)*az]:');
disp(xi);
disp('Tool-configuration Jacobian  J = d xi / d q:');
disp(J);

% Optional LaTeX 
try
    fprintf('\nLaTeX(xi):\n%s\n', latex(xi));
    fprintf('\nLaTeX(J):\n%s\n', latex(J));
catch
    
end

% numeric check at a sample pose 
q_num = [0.20 0.10 0.40 0.0 0.0];   % [m m m rad rad]
xi_num = double(subs(xi, q, q_num));
J_num  = double(subs(J,  q, q_num));


 % Local function (Standard DH) 
function A = dhA(a,alpha,d,theta)
    ca = cos(alpha); sa = sin(alpha);
    ct = cos(theta); st = sin(theta);
    A = [ ct, -st*ca,  st*sa, a*ct;
          st,  ct*ca, -ct*sa, a*st;
           0,     sa,     ca,    d;
           0,      0,      0,    1];
end
