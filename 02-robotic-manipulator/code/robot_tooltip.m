addpath(genpath('/Users/ysemila07/Desktop/Yr 4 Sem 2/ECTE471/ARTE-master'));   % ARTE path

init_lib;  
robot = load_robot; 

% tooltip and orientation calculations

QS = [ 
0.555, 0.500, -1.750, 0, 0;  
0.045, 3.640, -1.750, 0, 0;  
0.045, 2.880, -1.750, 0, 0;  
0.040, 2.880, -0.250, 0, 1.571  
]; 

for i = 1:size(QS,1) 
q = QS(i,:);  
T = directkinematic(robot, q);  
pos = T(1:3,4);  
R = T(1:3,1:3);  
eul = rotm2eul(R,'ZYX');  
rpy = rad2deg(eul([3 2 1])); 

fprintf('Configuration %d:\n', i); 
fprintf(' Joint vector q = [%.3f, %.3f, %.3f, %.3f, %.3f]\n', q); 
fprintf(' TCP Position (x,y,z) [m] = [%.3f, %.3f, %.3f]\n', pos); 
fprintf(' Orientation (roll, pitch, yaw) [deg] = [%.1f, %.1f, %.1f]\n\n', rpy); 

end 

 % visualisation
figure; hold on; grid on; 
xlabel('X (m)'); ylabel('Y (m)'); zlabel('Z (m)'); 
title('TCP positions for 4 configurations'); 
axis equal; view(120,30); 

for i = 1:4 
q = QS(i,:); 
T = directkinematic(robot,q); 
pos = T(1:3,4); 

plot3(pos(1),pos(2),pos(3),'o','MarkerSize',8,'MarkerFaceColor','r'); 

draw_axes(T,'X','Y','Z',0.6); 
text(pos(1),pos(2),pos(3)+0.05,sprintf('Config %d',i),'FontSize',10); 

end 
