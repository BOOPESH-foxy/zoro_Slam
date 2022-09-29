#!/usr/bin/python3
import rospy
from sensor_msgs.msg import Joy
from std_msgs.msg import Float32
import Jetson.GPIO as GPIO
import contextlib

import subprocess
import shlex

def constrain(val, min_val, max_val):
    return min(max_val, max(min_val, val))

class JoyClass:
    def __init__(self, scale=1.0, offset=0.0, deadband=0.1):
        rospy.init_node("joyz_node")
        self.joy_sub = rospy.Subscriber("/joy", Joy, self.joy_callback)
        self.wheel1_pub = rospy.Publisher("/wheel1_vel", Float32, queue_size=10)
        self.wheel2_pub = rospy.Publisher("/wheel2_vel", Float32, queue_size=10)
        self.wheel3_pub = rospy.Publisher("/wheel3_vel", Float32, queue_size=10)
        self.wheel4_pub = rospy.Publisher("/wheel4_vel", Float32, queue_size=10)
        #self.test = rospy.Publisher("/test", Float32, queue_size=10)
        self.rate = rospy.Rate(10)
        self.shutd = 0

    def joy_callback(self, msg):
        wheel1, wheel2, wheel3, wheel4,  = 0.0, 0.0, 0.0, 0.0
        rightTrig = (abs(msg.axes[3]-1.0)/2) 
        leftTrig = (-abs(msg.axes[4]-1.0)/2)
        if(rightTrig!=0 and leftTrig!=0):
            angular = 0.0
        elif(rightTrig>0.0 and leftTrig == 0.0):
            angular = rightTrig
        elif(leftTrig<0.0 and rightTrig == 0.0):
            angular = leftTrig
        #wheel1 = (msg.axes[0]+msg.axes[6]+angular)*1.5
        #wheel3 = (-msg.axes[0]-msg.axes[6]+angular)*1.5
        #wheel2 = (-msg.axes[1]-msg.axes[7]-angular)*1.5
        #wheel4 = (msg.axes[1]+msg.axes[7]-angular)*3.5      
        wheel1 = (msg.axes[0]*1.7) + (msg.axes[6]*1.7) + (angular * 0.6)
        wheel2 = (msg.axes[1]*1.7) + (msg.axes[7]*1.7) + (angular * 0.6)
        wheel3 = (-msg.axes[0]*1.7) + (-msg.axes[6]*1.7) + (angular * 0.6)
        wheel4 = (-msg.axes[1]*1.7) + (-msg.axes[7]*1.7) + (angular * 0.6)  #angular negative due to inward placement of wheels
        #wheel1 = (msg.axes[6])
        #wheel2 = (msg.axes[7])
        #wheel3 = (-msg.axes[6])
        #wheel4 = (-msg.axes[7])  
        self.wheel1_pub.publish(constrain(wheel1,-1.7,1.7))
        self.wheel2_pub.publish(constrain(wheel2,-1.7,1.7))
        self.wheel3_pub.publish(constrain(wheel3,-1.7,1.7))
        self.wheel4_pub.publish(constrain(wheel4,-1.7,1.7))
        #self.test.publish(angular)
              
        if(msg.buttons[0]):
            self.shutd += 1
            if(self.shutd == 3):
                cmd = shlex.split("sudo shutdown -h now")
                subprocess.call(cmd)
if __name__=="__main__":
    try:
      with contextlib.suppress(rospy.ROSInterruptException):
        JoyClass()
        rospy.spin()
    except Exception:
      pass
