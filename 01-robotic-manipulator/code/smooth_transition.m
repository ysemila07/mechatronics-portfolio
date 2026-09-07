clc; clear; close all;

%% Define workspace geometry (platforms / environment)
figure('Color','w','Name','Trajectory Visualization');
hold on; grid on; view(140,30);
xlabel('X (m)'); ylabel('Y (m)'); zlabel('Z (m)');
title('Smooth Trajectory Line Between Nut Feeder and Bolt_1');

% Base platform
fill3([-3 3 3 -3],[-3 -3 3 3],[0 0 0 0],'c','FaceAlpha',0.5,'EdgeColor','none');

% Add raised block (to mimic upper platform)
[X,Y] = meshgrid(-1:0.1:2,-1:0.1:2);
Z = zeros(size(X)) + 1.5; % height of upper platform
surf(X,Y,Z,'FaceColor',[0 0.6 0.6],'EdgeColor','none','FaceAlpha',0.8);

%% Define Cartesian points for trajectory
% Nut Feeder position
P_pick = [-3.0, -2.0, 0.4];
% Via (mid-air)
P_via  = [-0.5,  0.5, 2.5];
% Bolt (upper left bolt)
P_place = [2.8,  1.2, 1.6];

% Combine for path line
path = [P_pick; P_via; P_place];

%% Plot trajectory and frames 
% Trajectory line
plot3(path(:,1),path(:,2),path(:,3),'r-','LineWidth',3);
scatter3(P_pick(1),P_pick(2),P_pick(3),80,'k','filled');
scatter3(P_place(1),P_place(2),P_place(3),80,'m','filled');

% Add coordinate frames (X,Y,Z arrows)
quiver3(P_pick(1),P_pick(2),P_pick(3),0.3,0,0,'r','LineWidth',1.5);
quiver3(P_pick(1),P_pick(2),P_pick(3),0,0.3,0,'g','LineWidth',1.5);
quiver3(P_pick(1),P_pick(2),P_pick(3),0,0,0.3,'b','LineWidth',1.5);
text(P_pick(1),P_pick(2),P_pick(3)+0.2,'Z_{Feeder}','FontSize',10,'FontWeight','bold');

quiver3(P_place(1),P_place(2),P_place(3),0.3,0,0,'r','LineWidth',1.5);
quiver3(P_place(1),P_place(2),P_place(3),0,0.3,0,'g','LineWidth',1.5);
quiver3(P_place(1),P_place(2),P_place(3),0,0,0.3,'b','LineWidth',1.5);
text(P_place(1),P_place(2),P_place(3)+0.2,'Z_{Bolt1}','FontSize',10,'FontWeight','bold');

quiver3(P_via(1),P_via(2),P_via(3),0.3,0,0,'r','LineWidth',1.5);
quiver3(P_via(1),P_via(2),P_via(3),0,0.3,0,'g','LineWidth',1.5);
quiver3(P_via(1),P_via(2),P_via(3),0,0,0.3,'b','LineWidth',1.5);
text(P_via(1),P_via(2),P_via(3)+0.2,'Z_{TCP}','FontSize',10,'FontWeight','bold');

% Annotate points
text(P_pick(1),P_pick(2)-0.2,P_pick(3),'Nut Feeder','FontSize',10);
text(P_place(1),P_place(2)+0.2,P_place(3),'Bolt_1','FontSize',10);

%% Adjust appearance
axis equal;
xlim([-3.5 3.5]); ylim([-3.5 3.5]); zlim([0 3]);
set(gca,'FontSize',11);