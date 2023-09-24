import gymnasium as gym
from gymnasium import spaces
import numpy as np
import pygame
from math import sqrt, pow, sin, cos, tan, atan, pi, degrees
from pygame.locals import *
import pygame, sys
from Track import race_track
from CarDynamics import *


# Custom RaceCar Environment
class Race_Car_Env(gym.Env):
    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 1000}

    def __init__(self, render_mode="human", track_type = "track_1"):
        self.windowLenWidth=(1200, 800)
        self.track_type = track_type

        self.setpoints = {"track_1":[(100, 300),1.57, (100, 500)], "track_2" : [(50, 400), 0, (1150, 400)], "track_3": [(650, 110), 0, (470, 110)]}

        self.start_point = self.setpoints[self.track_type][0]
        self.start_orient = self.setpoints[self.track_type][1]
        self.end_point = self.setpoints[self.track_type][2]

        self.observation_space = spaces.Dict(
            {"agent": spaces.Box(0, 30, shape=(5,), dtype=int)}
        )

        self.action_space = spaces.Discrete(4)

        assert render_mode is None or render_mode in self.metadata["render_modes"]
        self.render_mode = render_mode

        self.window = None
        self.clock = None
        self.track = None

        self.player = None
        self.alive = None

    def _get_obs(self):
        return {"agent": self.player.distances}
    
    def _get_info(self):
        return {"agent": (self.player.rect.x, self.player.rect.y)}
    
    def step(self, action):
        self.player.updateDynamics(action)
        self.player.collision_check()
        self.player.getDistances()
    
        if self.player.collision_check():
            self.alive = False 

        reward = self.get_reward()
        terminated = self.isAgentDead

        observation = self._get_obs()
        info = self._get_info()

        if self.render_mode == "human":
            self._render_frame()

        return observation, reward, terminated, False, info

    def isAgentDead(self):
        return not self.alive
    
    def dist(self, p1, p2):
        return sqrt(pow(p1[0]-p2[0], 2) + pow(p1[1]-p2[1], 2))
    
    def drawInfo(self, text):
        font = pygame.font.Font('freesansbold.ttf', 20)
        string="Generation #"+str(text)
        text = font.render( string , True, WHITE, None)
        textRect = text.get_rect()
        textRect.center = (1000,10)
        self.screen.blit(text, textRect)
    
    def get_reward(self):
        sweep_r = (self.player.cur_pose - self.player.prev_pose)*0.0

        if not self.alive:
                return -1000 
        else:
            x = self.player.rect.x
            y = self.player.rect.y
            if self.dist(self.end_point, (x, y)) <= 5:
                self.alive = False
                return 1000 + sweep_r
                print('yup')
            else:
                return -0.5 + sweep_r
            
    
    def reset(self, seed=None, options=None):
        # We need the following line to seed self.np_random
        super().reset(seed=seed)
        render = False

        # Initializing display
        pygame.init()
        pygame.display.init()
        self.window = pygame.display.set_mode(self.windowLenWidth)
        self.track=race_track(self.window, self.windowLenWidth, track=self.track_type)

        # Initializing the agent's location 
        self.player =  Player(self.window, self.track, position=pos(self.start_point[0], self.start_point[1]))
        self.player.orientation = self.start_orient
        self.player.prev_orientation = self.start_orient

        self.player.cur_pose = atan((self.start_point[1]-600)/(self.start_point[0]-400)) % (2*pi)
        self.player.prev_pose = self.player.cur_pose

        self.alive = True

        self.player.getDistances()

        observation = self._get_obs()
        info = self._get_info()

        if self.render_mode == "human":
            self._render_frame()

        return observation, info
    

    def render(self):
        if self.render_mode == "rgb_array":
            return self._render_frame()

    def _render_frame(self):
        if self.window is None and self.render_mode == "human":
            pygame.init()
            pygame.display.init()
            self.window = pygame.display.set_mode(self.windowLenWidth)
            self.track=race_track(self.window, self.windowLenWidth, track=self.track_type)

        if self.clock is None and self.render_mode == "human":
            self.clock = pygame.time.Clock()

        self.track.draw()
        self.player.draw()

        if self.render_mode == "human":
            # The following displays our window
            # pygame.event.pump()
            pygame.display.flip()
            pygame.display.update()

            # We need to ensure that human-rendering occurs at the predefined framerate.
            # The following line will automatically add a delay to keep the framerate stable.
            # self.clock.tick(self.metadata["render_fps"])

        else:  # rgb_array
            return None
            # return np.transpose(
            #     np.array(pygame.surfarray.pixels3d(self.window)), axes=(1, 0, 2)
            # )

    def close(self):
        if self.window is not None:
            pygame.display.quit()
            pygame.quit()
