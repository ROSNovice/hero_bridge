#!/usr/bin/env python
# -*- coding: utf-8 -*-

# '''
# This node listens to a service call for a joint trajectory planner.
# These will be bridged to the Toyota safe pose changer.
# '''

import rospy
import actionlib

from tmc_manipulation_msgs.srv import SafeJointChange
from sensor_msgs.msg import JointState
from tue_manipulation_msgs.msg import GripperCommandAction
#from control_msgs.msg import FollowJointTrajectoryAction
import sys

reload(sys)
sys.setdefaultencoding('utf8')

class JointTrajectory(object):
    def __init__(self):

        # topics
        # self.pub_speak = rospy.Publisher("/talk_request", Voice, queue_size=10)

        # server
        self.srv_safe_joint_change = actionlib.SimpleActionServer('/hero/left_arm/gripper/action',
                                                                  GripperCommandAction,
                                                                  execute_cb=self.safe_joint_change_srv,
								  auto_start=False)
	self.srv_safe_joint_change.start()

        # clients
        self.client_safe_joint_change = rospy.ServiceProxy('/safe_pose_changer/change_joint', SafeJointChange)

    def safe_joint_change_srv(self, goal):
        '''
        Here the follow joint trajectory action is translated to a SafeJointChange message type
        :param action: the FollowJointTrajectoryAction type
        :return: the SafeJointChange message type
        '''

        # helper variables
        r = rospy.Rate(1)
        success = True
           
        # append the seeds for the fibonacci sequence
	safeJointChange = JointState()
        safeJointChange.header.seq = 0 
	safeJointChange.header.stamp.secs = 0
	safeJointChange.header.stamp.nsecs = 0
	safeJointChange.header.frame_id = ''

	safeJointChange.name = ['hand_motor_joint']
	safeJointChange.position = [0]
	safeJointChange.velocity = [0]
	safeJointChange.effort = [0]
           
	if goal.command.direction is goal.command.OPEN:
          safeJointChange.position=[1.0]
        elif goal.command.direction is goal.command.CLOSE:
          safeJointChange.position=[0.0] 
        else:
          rospy.loginfo('Trajectory bridge: received gripper goal that is nor OPEN or CLOSE')
          succes = False
        # check that preempt has not been requested by the client
        if self.srv_safe_joint_change.is_preempt_requested():
          rospy.loginfo('Trajectory bridge: Preempted')
          self.srv_safe_joint_change.set_preempted()
          success = False
         
	
        self.client_safe_joint_change(safeJointChange) 
             
        if success:
          rospy.loginfo('Trajectory bridge: Succeeded')
          self.srv_safe_joint_change.set_succeeded()
       

if __name__ == "__main__":
    rospy.init_node('gripper_bridge')
    joint_trajectory = JointTrajectory()

    rospy.spin()
