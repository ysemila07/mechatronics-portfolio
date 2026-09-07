clear; 
clc;

% Define via-points (meters)
AP = [1.750, -1.750, 0.562];   % Above-pick
P  = [1.750, -1.750, 0.502];   % Pick
AL = [2.770, -0.250, 0.165];   % Above-place (corrected)
L  = [2.770, -0.250, 0.105];   % Place (corrected)

% Segment durations
dt = 0.02;               % sample time (s)
d1 = 1.0;                % AP -> P
d2 = 1.0;                % P -> AP
dist_AP_AL = norm(AL - AP);
d3 = dist_AP_AL / 0.2;   % AP -> AL at ~0.2 m/s
d4 = 1.0;                % AL -> L
d5 = 1.0;                % L -> AL

% Helper function
linseg = @(p0,p1,dur,dt) deal( ...
    (0:dt:dur)', ...
    (0:dt:dur)' .* (p1-p0)/dur + p0, ...
    repmat((p1-p0)/dur, length(0:dt:dur), 1) );

% Build trajectory
segments = {AP,P,d1; P,AP,d2; AP,AL,d3; AL,L,d4; L,AL,d5};

t_all = []; p_all = []; v_all = [];
t_offset = 0;
for i=1:size(segments,1)
    [t,p,v] = linseg(segments{i,1},segments{i,2},segments{i,3},dt);
    if ~isempty(t_all)
        % drop duplicate first point of each segment
        t = t(2:end); p = p(2:end,:); v = v(2:end,:);
    end
    t_all = [t_all; t + t_offset];
    p_all = [p_all; p];
    v_all = [v_all; v];
    t_offset = t_offset + segments{i,3};
end

% Joint velocities (fixed wrist)
qdot = [v_all, zeros(size(v_all,1),2)]; % [q1dot,q2dot,q3dot,q4dot,q5dot]


% Plot TCP trajectory
figure;
plot3(p_all(:,1), p_all(:,2), p_all(:,3), 'b-','LineWidth',1.5); hold on;
scatter3([AP(1) P(1) AL(1) L(1)], [AP(2) P(2) AL(2) L(2)], ...
         [AP(3) P(3) AL(3) L(3)], 60, 'r','filled');
grid on; axis equal;
xlabel('X [m]'); ylabel('Y [m]'); zlabel('Z [m]');
title('TCP trajectory (AP→P→AP→AL→L→AL)');

% Plot joint velocities
figure;
plot(t_all, qdot(:,1),'r','LineWidth',1.5); hold on;
plot(t_all, qdot(:,2),'g','LineWidth',1.5);
plot(t_all, qdot(:,3),'b','LineWidth',1.5);
plot(t_all, qdot(:,4),'k--','LineWidth',1.0);
plot(t_all, qdot(:,5),'m--','LineWidth',1.0);
xlabel('Time [s]');
ylabel('Joint velocity [m/s or rad/s]');
title('Joint velocities (PPPRR, fixed wrist)');
legend('q1dot','q2dot','q3dot','q4dot','q5dot');
grid on;
