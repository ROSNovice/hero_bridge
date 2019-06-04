#!/usr/bin/env python
# -*- coding: utf-8 -*-

#'''
#This node listens to a service call and a topic for text to speech
#requests. These will be processed by the festival or the philips tts module.
#'''

import rospy
import actionlib

from std_msgs.msg import String
from tmc_msgs.msg import TalkRequestAction, TalkRequestGoal, Voice
from text_to_speech.srv import Speak, SpeakRequest


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class TTS(object):
    def __init__(self):
        self.samples_path = rospy.get_param("~samples_path", "~/MEGA/media/audio/soundboard")

        # topics
        self.sub_speak = rospy.Subscriber("~input", String, self.speak)
        # self.pub_speak = rospy.Publisher("/talk_request", Voice, queue_size=10)

        # services
        self.srv_speak = rospy.Service('~speak', Speak, self.speak_srv)

        # clients
        self.speech_client = actionlib.SimpleActionClient('/talk_request_action', TalkRequestAction)
        self.speech_client.wait_for_server()

        # buffer and goal state
        self.buffer = []
        self.goal_state = actionlib.SimpleGoalState

    def do_tts(self, req):
        # rospy.loginfo('TTS: Toyota TTS, through bridge node. "' + bcolors.OKBLUE + req.sentence + bcolors.ENDC + '"')

        self.buffer += [req]

        # rospy.loginfo(self.speech_client.simple_state)

        while not rospy.is_shutdown() and self.buffer and self.speech_client.simple_state == self.goal_state.ACTIVE \
                and self.buffer[0].blocking_call:
            rospy.loginfo("Currently waiting to finish previous speech input.")
            rospy.sleep(0.1)

        # rospy.loginfo("after: {}".format(self.speech_client.simple_state))

        goal = TalkRequestGoal()
        out = Voice()
        out.interrupting = False
        out.queueing = True
        out.language = 1
        out.sentence = self.buffer[0].sentence
        goal.data = out

        self.speech_client.send_goal(goal)

        if self.buffer:
            self.buffer.pop(0)

        # if req.blocking_call:
        #     self.speech_client.wait_for_result()

    def speak(self, sentence_msg):
        req = SpeakRequest()
        req.sentence = sentence_msg.data
        # req.character = self.character
        # req.language = self.language
        # req.voice = self.voice
        # req.emotion = self.emotion
        req.blocking_call = True

        self.do_tts(req)

    def speak_srv(self, req):
        self.do_tts(req)
        return ""


if __name__ == "__main__":
    rospy.init_node('text_to_speech')
    tts = TTS()

    rospy.spin()
