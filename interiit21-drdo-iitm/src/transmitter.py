import pygame
import random
import rospy
import math
from geometry_msgs.msg import TwistStamped
from geometry_msgs.msg import PoseStamped

rospy.init_node('make_a_circle', anonymous=True)

current_pos = PoseStamped()

def main():
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    clock = pygame.time.Clock()

    x_curser1 = 160
    y_curser1 = 240
    x_curser2 = 480
    y_curser2 = 240
    mode= ''
    count = 0
    radius = 10
    screen.fill((0, 0, 0))

    color_curser1 = (0,255,0)
    color_curser2 = (0,255,0)
    pygame.draw.circle(screen, color_curser1, (x_curser1, y_curser1), radius)
    pygame.draw.circle(screen, color_curser2, (x_curser2, y_curser2), radius)

    

    while True:
        
        screen.fill((0, 0, 0))
        x_curser1 = 160
        y_curser1 = 240
        x_curser2 = 480
        y_curser2 = 240    

        pressed = pygame.key.get_pressed()
        
        alt_held = pressed[pygame.K_LALT] or pressed[pygame.K_RALT]
        ctrl_held = pressed[pygame.K_LCTRL] or pressed[pygame.K_RCTRL]
        
        for event in pygame.event.get():
            
            # determin if X was clicked, or Ctrl+W or Alt+F4 was used
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w and ctrl_held:
                    return
                if event.key == pygame.K_F4 and alt_held:
                    return
                if event.key == pygame.K_ESCAPE:
                    return
            
                # determine if a letter key was pressed
                if event.key == pygame.K_w:
                    mode = 'up'
                elif event.key == pygame.K_s:
                    mode = 'down'
                elif event.key == pygame.K_d:
                    mode = 'right'
                elif event.key == pygame.K_a:
                    mode = 'left'
                elif event.key == pygame.K_SPACE:
                    mode = 'jump'
                elif event.key == pygame.K_q:
                    mode = 'yaw'
                elif event.key == pygame.K_e:
                    mode = 'yawri8'
                elif event.key == pygame.K_LCTRL:
                    mode = 'low'     
                elif event.key == pygame.K_h:
                    mode = 'hold'  


        color_curser1 = (255,0,0)
        color_curser2 = (255,0,0)
        color_curser3 = (0,0,255)
        color_curser4 = (0,0,255)

        pygame.draw.circle(screen, color_curser1, (x_curser1, y_curser1), radius)
        pygame.draw.circle(screen, color_curser2, (x_curser2, y_curser2), radius)
        
        x_curser1,y_curser1,x_curser2,y_curser2 = curserControl(screen,x_curser1,y_curser1,x_curser2,y_curser2,mode,count,color_curser1,color_curser1,radius)

        pygame.draw.circle(screen, color_curser3, (x_curser1, y_curser1), radius)
        pygame.draw.circle(screen, color_curser4, (x_curser2, y_curser2), radius)

        pygame.display.flip()
        
        clock.tick(60)

def curserControl(screen,x_curser1,y_curser1,x_curser2,y_curser2,mode,count,color_curser1,color_curser2,radius):

    publish_velocity=rospy.Publisher('/mavros/setpoint_velocity/cmd_vel', TwistStamped,queue_size=20)
    vel=TwistStamped()


    if mode == 'up':

        vel.twist.linear.x= 0.8
        publish_velocity.publish(vel)
        vel.twist.linear.x= 0
        y_curser1= y_curser1 -20
        pygame.draw.circle(screen, color_curser1, (x_curser1, y_curser1), radius)
        print("up")
    elif mode == 'down':
        vel.twist.linear.x= -0.8
        publish_velocity.publish(vel)
        vel.twist.linear.x= 0
        y_curser1= y_curser1 +20
        pygame.draw.circle(screen, color_curser1, (x_curser1, y_curser1), radius)
        print("down")
    elif mode == 'right':
        vel.twist.linear.y= -0.8
        publish_velocity.publish(vel)
        vel.twist.linear.y= 0
        x_curser1= x_curser1 +20
        pygame.draw.circle(screen, color_curser1, (x_curser1, y_curser1), radius)
        print("right")
    elif mode == 'left':

        vel.twist.linear.y= 0.8
        publish_velocity.publish(vel)
        vel.twist.linear.y= 0
        x_curser1= x_curser1 -20
        pygame.draw.circle(screen, color_curser1, (x_curser1, y_curser1), radius)  
        print("left")
    elif mode == 'jump':

        vel.twist.linear.z= 1
        publish_velocity.publish(vel)
        vel.twist.linear.z= 0
        y_curser2= y_curser2 -20
        pygame.draw.circle(screen, color_curser2, (x_curser2, y_curser2), radius)

        print("jump")
    elif mode == 'low':

        vel.twist.linear.z= -0.5
        publish_velocity.publish(vel)
        vel.twist.linear.z= 0
        y_curser2= y_curser2 +20
        pygame.draw.circle(screen, color_curser2, (x_curser2, y_curser2), radius)
        print("low")  
  
    elif mode == 'yaw':

        vel.twist.angular.z= 0.8
        publish_velocity.publish(vel)
        vel.twist.linear.z= 0
        x_curser2= x_curser2 -20
        pygame.draw.circle(screen, color_curser2, (x_curser2, y_curser2), radius)
        print("yawleft")

    elif mode == 'yawri8':

        vel.twist.angular.z= -0.8
        publish_velocity.publish(vel)
        vel.twist.linear.z= 0
        x_curser2= x_curser2 +20
        pygame.draw.circle(screen, color_curser2, (x_curser2, y_curser2), radius)
        print("yawri8") 
    elif mode == 'hold':

        vel.twist.angular.z= 0
        publish_velocity.publish(vel)
        print("hold")              

    return x_curser1, y_curser1 ,x_curser2, y_curser2    
    


main()
