import gym
import rospy
import roslaunch
import time
import numpy as np

from gym import utils, spaces
from gym_gazebo.envs import gazebo_env
from geometry_msgs.msg import Twist, Vector3
from std_srvs.srv import Empty

from sensor_msgs.msg import LaserScan

from gym.utils import seeding


class GazeboMazeTurtlebotLidarEnv(gazebo_env.GazeboEnv):

    def __init__(self):
        # Launch the simulation with the given launchfile name
        gazebo_env.GazeboEnv.__init__(self, "GazeboMazeTurtlebotLidar_v0.launch")
        self.vel_pub = rospy.Publisher('/mobile_base/commands/velocity', Twist, queue_size=5)
        self.unpause = rospy.ServiceProxy('/gazebo/unpause_physics', Empty)
        self.pause = rospy.ServiceProxy('/gazebo/pause_physics', Empty)
        self.reset_proxy = rospy.ServiceProxy('/gazebo/reset_simulation', Empty)

        self.action_space = spaces.Discrete(3)  # F,L,R
        self.reward_range = (-np.inf, np.inf)

        self._seed()

    def discretize_observation(self, data, new_ranges):
        discretized_ranges = []
        mod = len(data.ranges) / new_ranges
        for i, item in enumerate(data.ranges):
            if item == float('Inf'):
                discretized_ranges.append(100)
            elif np.isnan(item):
                discretized_ranges.append(0)
            else:
                discretized_ranges.append(item)
        return discretized_ranges, False

    def _seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def _step(self, action):

        rospy.wait_for_service('/gazebo/unpause_physics')
        try:
            self.unpause()
        except rospy.ServiceException, e:
            print("/gazebo/unpause_physics service call failed")

        if action == 0:  # FORWARD
            vel_cmd = Twist()
            vel_cmd.linear.x = 0.1
            self.vel_pub.publish(vel_cmd)
        elif action == 1:  # LEFT
            vel_cmd = Twist()
            vel_cmd.angular.z = 0.1
            self.vel_pub.publish(vel_cmd)
        elif action == 2:  # RIGHT
            vel_cmd = Twist()
            vel_cmd.angular.z = -0.1
            self.vel_pub.publish(vel_cmd)
        elif action == 3:  # BACK
            vel_cmd = Twist()
            vel_cmd.linear.x = -0.1
            self.vel_pub.publish(vel_cmd)
        else:
            vel_cmd = Twist()
            vel_cmd.linear.x = 0.0
            vel_cmd.angular.z = 0.0
            self.vel_pub.publish(vel_cmd)


        data = None
        while data is None:
            try:
                data = rospy.wait_for_message('/scan', LaserScan, timeout=5)
            except:
                pass

        rospy.wait_for_service('/gazebo/pause_physics')
        try:
            #resp_pause = pause.call()
            self.pause()
        except rospy.ServiceException, e:
            print("/gazebo/pause_physics service call failed")

        obs, done = self.discretize_observation(data, 20)

        if not done:
            if action == 0:
                reward = 3
            else:
                reward = 1
        else:
            reward = -200

        return obs, reward, done, {}

    def _reset(self):

        # Resets the state of the environment and returns an initial observation.
        rospy.wait_for_service('/gazebo/reset_simulation')
        try:
            # reset_proxy.call()
            self.reset_proxy()
        except rospy.ServiceException, e:
            print("/gazebo/reset_simulation service call failed")

        # Unpause simulation to make observation
        rospy.wait_for_service('/gazebo/unpause_physics')
        try:
            #resp_pause = pause.call()
            self.unpause()
        except rospy.ServiceException, e:
            print("/gazebo/unpause_physics service call failed")

        # read laser data
        data = None
        while data is None:
            try:
                data = rospy.wait_for_message('/scan', LaserScan, timeout=5)
            except:
                pass

        rospy.wait_for_service('/gazebo/pause_physics')
        try:
            #resp_pause = pause.call()
            self.pause()
        except rospy.ServiceException, e:
            print("/gazebo/pause_physics service call failed")

        state = self.discretize_observation(data, 5)

        return state
