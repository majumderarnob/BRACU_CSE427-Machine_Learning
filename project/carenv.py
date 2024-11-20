
import gymnasium as gym
from gymnasium import spaces
import time
import pygame
import numpy as np

class CarEnv(gym.Env):
    def __init__(self):
        self.SCREEN_WIDTH = 360
        self.SCREEN_HEIGHT = 600
        self.render_mode= None

        pygame.init()
        pygame.display.set_caption('')
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        self.font = pygame.font.SysFont('Arial_bold', 36)
        
        self.fps = 60

        self.car_height = 100
        self.car_width = 60
        self.speed = 25

        self.lane = 4
        self.lane_width = self.SCREEN_WIDTH//self.lane

        self.road_line_height = 50
        self.road_line_width = 8
        self.road_line_gap = 100
        self.road_line_speed = 2

        self.clock = pygame.time.Clock()

        self.font_size = 36

        self.maximum_npc_cars = 3

        self.spawn_prob_list = [0.7 , 0.1 , 0.1, 0.05 ,0.05]

        low = -1
        high = 1
        
        self.observation_space=spaces.Box(low=low, high=high, shape=(6,), dtype = np.float32)
        self.action_space=spaces.Discrete(5)

    def step(self, action):
        x = self.user_car.x
        y = self.user_car.y
        if action == 0:
            if self.user_car.y < self.SCREEN_HEIGHT - self.car_height:
                self.user_car.y = self.speed + self.user_car.y
        if action == 1:
            if self.user_car.y >= 0:
                self.user_car.y = -self.speed + self.user_car.y
        if action == 2:
            if self.user_car.x < self.SCREEN_WIDTH - self.car_width:
                self.user_car.x = self.speed + self.user_car.x
        if action == 3:
            if self.user_car.x >= 0:
                self.user_car.x = -self.speed + self.user_car.x

        if self.alive == True:
            self.distroy_old_npc()
            if self.num == 20:
                self.spawn_npc_car()
                self.num = 0
            self.move_npc()
            self.reward = 5
            self.collision_detect()
        else:
            self.run = False
            self.done = True
            self.reward = - 100
        self.observation = self.get_obs()

        for a in self.observation[2:]:
            if int(a) == 0:
                self.reward -= 1
        self.num += 1

        if self.point == 30:
            self.reward = 200
            self.done = True

        if self.render_mode == "human":
            self.render()


        return self.observation, self.reward , self.done ,False,  {}

    def reset(self, seed=None, options=None):
        super().reset(seed=seed, options=options)
        
        self.point = 0

        self.user_car = pygame.Rect((self.SCREEN_WIDTH - self.car_width)//2, 500, self.car_width , self.car_height)
        self.npc_cars = []
        self.road_lines = []
        self.alive = True
        
        self.observation = self.get_obs()
        self.reward = 0
        self.num = 0
        self.mode = ""
        self.done = False

        if self.render_mode == 'human':
            self.render()
        
        return self.observation , {}

    def get_obs(self):
        # list_x = [self.user_car.x/self.SCREEN_WIDTH]
        # list_y = [self.user_car.y/self.SCREEN_HEIGHT]
        # for car , lane in self.npc_cars:
        #     list_x.append(car.x/self.SCREEN_WIDTH)
        #     list_y.append(car.y/self.SCREEN_HEIGHT)
        # while len(list_x) <= self.maximum_npc_cars:
        #     list_x.append(-1)
        #     list_y.append(-1)
        # return np.concatenate((list_x, list_y))
        obs_list = [self.user_car.x/self.SCREEN_WIDTH , self.user_car.y / self.SCREEN_HEIGHT ,True ,True ,True ,True]
        for car, lane in self.npc_cars:
            if car.x < self.user_car.x:
                obs_list[2] = self.user_car.x - (car.x + self.car_width) > 0 and obs_list[2]
            else:
                obs_list[3] = self.user_car.x + self.car_width - (car.x) < 0 and obs_list[3]

            if car.y <= self.user_car.y:
                obs_list[4] = self.user_car.y - (car.y + self.car_height) > 0 and obs_list[4]
            else:
                obs_list[5] = self.user_car.y + self.car_height - (car.y) < 0 and obs_list[5]
        
        for a in obs_list:
            a = float(a)

        return obs_list

        

    def render(self, render_mode = "human"):  
        self.screen.fill((75,75,75))
        self.draw_road()
        self.draw_npc_car()
        pygame.draw.rect(self.screen , (255,0,0) , self.user_car)
        str1 = str(self.point) + " | " + str(self.reward)
        text = self.font.render(str1, True, (255, 255, 255))
        self.screen.blit(text, (self.SCREEN_WIDTH // 2 - (len(str1) * self.font_size / 2), 0))
        pygame.display.update()
        self.clock.tick(self.fps)

        if self.done:
            time.sleep(0.5)

    def close(self):
        pygame.quit()

    def spawn_npc_car(self):
        if len(self.npc_cars) < self.maximum_npc_cars:
            num = np.random.choice([0,1,2,3,4], p=self.spawn_prob_list)
            if num != 0:
                num = num - 1
                self.npc_cars.append((pygame.Rect(num * self.lane_width + self.car_width // 2 - self.road_line_width, - self.car_height , self.car_width, self.car_height), num))

    def distroy_old_npc(self):
        i = 0
        while i < len(self.npc_cars):
            if self.npc_cars[i][0].y > self.SCREEN_HEIGHT:
                self.npc_cars.pop(i)
                self.point += 1
            else:
                i+=1

    def move_npc(self):
        for car , lane_index in self.npc_cars:
            car.y += self.road_line_speed + 2

    def draw_npc_car(self):
        for car , speed in self.npc_cars:
            pygame.draw.rect(self.screen , (0,255,255) , car)

    def collision_detect(self):
        collide = False
        wall_collide = (self.user_car.x < 0) or (self.user_car.x - self.car_width > self.SCREEN_WIDTH)
        for npc_rect, lane in self.npc_cars:
            collide = pygame.Rect.colliderect(self.user_car, npc_rect)
            if collide or wall_collide:
                self.reward = -100
                self.alive = False

    def draw_road(self):
        if len(self.road_lines) == 0:
            i = 0
            while i < self.SCREEN_HEIGHT // (self.road_line_gap + self.road_line_height) + 1:
                j = 0
                while j < self.lane - 1:
                    self.road_lines.append(pygame.Rect(self.lane_width * (j+1) - self.road_line_width//2 , i * (self.road_line_gap + self.road_line_height), self.road_line_width, self.road_line_height))
                    j += 1
                i += 1
        
        if self.road_lines[-1].y > self.SCREEN_HEIGHT:
            for i in range(self.lane-1):
                self.road_lines.pop(-1)
                self.road_lines.insert(0 , pygame.Rect(self.lane_width * (i+1) - self.road_line_width//2 , -(self.road_line_gap + self.road_line_height), self.road_line_width, self.road_line_height))

        for line in self.road_lines:
            line.y += self.road_line_speed
            pygame.draw.rect(self.screen, (255,255,255), line)

