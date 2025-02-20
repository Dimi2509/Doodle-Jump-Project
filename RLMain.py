import gymnasium as gym
import numpy as np
from gymnasium import spaces
from Doodle import Doodle, Platform, Actions, BluePlatform
import pygame
import math 


pygame.init()

# Screen Dimensions
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600

# Load images
background_img = pygame.image.load("img/background.png").convert_alpha()
doodle_img = pygame.image.load("img/doodle.png").convert_alpha()
platform_image = pygame.image.load("img/green_plataform.png").convert_alpha()
blue_platform_image = pygame.image.load("img/blue_plataform.png").convert_alpha()

# Create screen / Set title
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Doodle - Game")

# Create Sprite Groups
platform_group = pygame.sprite.Group()

FPS = 60

# Game variables
GRAVITY = 1
MAX_PLATFORMS = 6
SCROLL_THRESH = 225

# Colours
WHITE = (255,255,255)
RED = (255,0,0)
BLACK = (0,0,0)


class DoodleEnv(gym.Env):
    """Custom Environment that follows gym interface."""

    metadata = {"render_modes": ["human"], "render_fps": 60}

    def __init__(self):
        super().__init__()
        # Define action and observation space
        # They must be gym.spaces objects
        # Example when using discrete actions:
        self.action_space = spaces.Discrete(3) # 3 Actions-> Nothing : 0, Left : 1, Right : 2

        # ???¿¿¿
        #self.observation_space = spaces.Box(low=-10000, high=10000,
        #                                    shape=(21,), dtype=np.float32)
        self.observation_space = spaces.Dict({
            'doodler': spaces.Box(low=-10000, high=10000, shape=(3,), dtype=np.float32),
            'platforms': spaces.Box(low=-10000, high=10000, shape=(MAX_PLATFORMS, 5), dtype=np.float32)
        })

        pygame.init()
        pygame.display.init()
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

        self.doodler = Doodle(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 150) # 150
        self.restart_game = False

        self.last_height = 0
        self.record_height = 150 # Leave some room for the very first jumps
        self.steps_without_new_platform = 0
        self.previous_score = 0
        self.reward = 0
        self.total_reward = 0
        self.terminated = False
        self.truncated = False

        self.thershold_y_top = self.doodler.rect.bottom + 15
        self.thershold_y_bot = self.doodler.rect.bottom + 25

        # Normalization parameters
        self.MAX_VELOCITY = 20  # Estimate based on gameplay
        self.MAX_PLATFORM_WIDTH = 120  # Adjust as needed
        self.MIN_PLATFORM_WIDTH = 60  # Adjust as needed
        self.MAX_COLLISION_COUNT = 5  # Normalize by a reasonable max
        self.MAX_DISTANCE = math.sqrt(SCREEN_WIDTH**2 + SCREEN_HEIGHT**2)  # Diagonal distance


    def step(self, action): # action being the decision taken by the algorithm
        #print("step")
        self.reward = 0
        self.clock.tick(FPS)

        # Draw Background and score
        screen.blit(background_img, (0, 0))

        # Create new platforms if needed
        if len(platform_group) < MAX_PLATFORMS:
            Platform.create_platform(platform_group)

        # Move Character and platforms according to the scroll
        scroll = self.doodler.move(action, platform_group)
        platform_group.update(scroll, self.doodler.visited_platforms)

        # Draw Doodler and Platforms
        platform_group.draw(screen)
        self.doodler.draw()

        # Restart game if player falls
        if self.doodler.rect.top > SCREEN_HEIGHT:
            #self.truncated = True
            self.terminated = True
            self.reward = -50


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.close()

        pygame.display.update()

        observation = self._get_observation()
        self.reward += self._calculate_reward()
        self.total_reward += self.reward
        #print(self.total_reward)

        info = {}
        return observation, self.reward, self.terminated, self.truncated, info # Termination when fall, truncation when time limit reached

    def reset(self, seed=None, options=None):

        super().reset(seed=seed)
        print("Reset")
        self.restart_game = False
        self.truncated = False
        self.terminated = False
        self.doodler.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80) # -150
        self.doodler.vel_y = 0
        self.doodler.reward = 0
        self.doodler.score = 0
        self.doodler.current_height = 0
        self.last_height = 0
        platform_group.empty()

        # Create starting platform
        platform = Platform(SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT - 50, 100, platform_image)
        platform_group.add(platform)
        self.doodler.visited_platforms.append(platform)
        
        observation = self._get_observation()       
        info = {}
        return observation, info

    def render(self):
        ...

    def close(self):
        pygame.display.quit()
        pygame.quit()

    def _normalize_observation(self, obs):
        """ Normalize observation data """

        # Normalize doodler position and velocity
        obs["doodler"][0] = (obs["doodler"][0] / SCREEN_WIDTH) * 2 - 1  # Normalize x to [-1,1]
        obs["doodler"][1] = (obs["doodler"][1] / SCREEN_HEIGHT) * 2 - 1  # Normalize y to [-1,1]
        obs["doodler"][2] = -1 if obs["doodler"][2] < 0 else 1  # Direction-based velocity 

        # Normalize platform data
        for platform in obs["platforms"]:
            platform[0] = (platform[0] / SCREEN_WIDTH) * 2 - 1  # Normalize x
            platform[1] = (platform[1] / SCREEN_HEIGHT) * 2 - 1  # Normalize y
            platform[2] = (platform[2] - self.MIN_PLATFORM_WIDTH) / (self.MAX_PLATFORM_WIDTH - self.MIN_PLATFORM_WIDTH)  # Normalize width [0,1]
            platform[3] = np.clip(platform[3] / self.MAX_DISTANCE, 0, 1)  # Normalize distance [0,1]
            platform[4] = np.clip(platform[4] / self.MAX_COLLISION_COUNT, 0, 1)  # Normalize collision count [0,1]

        return obs

    def _get_observation(self):
        """
        Doodle:
        Doodle's center x and y coordinates and its velocity.


        Platform:
        list of shape [MAX_PLATFORMS, 5], where each item contains center x and y coordinates, the width of the platform,
        the euclidean distance between the platform and the doodle and the number of collisions that the doodle has had on
        that platform.
        """   
        platform_data = []
        for platform in platform_group:
            platform.platform_distance_to_doodler = math.sqrt(
                abs(self.doodler.rect.centerx - platform.rect.centerx)**2 + 
                abs(self.doodler.rect.centery - platform.rect.centery)**2 )
                
            platform_data.append([
                platform.rect.centerx, 
                platform.rect.centery, 
                platform.rect.width, 
                platform.platform_distance_to_doodler, 
                platform.collision_count])
        
        # Pad with zeros if needed
        while len(platform_data) < MAX_PLATFORMS:
            platform_data.append([0, 0, 0, 0, 0])
        
        obs = {
            'doodler': np.array([
                self.doodler.rect.centerx,
                self.doodler.rect.centery,
                self.doodler.vel_y
            ], dtype=np.float32),
            'platforms': np.array(platform_data, dtype=np.float32)
        }

        return self._normalize_observation(obs)
        # return {
        #     'doodler': np.array([
        #         self.doodler.rect.centerx,
        #         self.doodler.rect.centery,
        #         self.doodler.vel_y
        #     ], dtype=np.float32),
        #     'platforms': np.array(platform_data, dtype=np.float32)
        # }


    def _calculate_reward(self):
        reward = 0 

        # Velocity based reward
        reward += 0.1 if self.doodler.vel_y < 0 else -0.05
        #print(f"Test velocity based reward {reward}")
        
        # Score Based Reward
        # reward += (self.doodler.score - self.previous_score) * 1.2
        # self.previous_score = self.doodler.score

        # Height Based Reward
        reward += (self.doodler.current_height - self.last_height) * 1
        if self.doodler.current_height > 400:
            reward += 0.5 

        reward += (self.doodler.score - self.previous_score) * 1.2 

        #print(f"Reward with New Height Based system: {reward}\n")
        # print(f"Current: {self.doodler.current_height}\n")
        # print(f"Last: {self.last_height}\n")
        
        # Platform Based Reward
        if self.doodler.last_platform not in self.doodler.visited_platforms and self.doodler.last_platform != None:
            reward += 12 # Reward for visiting a new platform

            # Encourage agent to take longer horizontal jumps rather than falling 
            horizontal_distance_jump = abs(self.doodler.last_platform.rect.centerx - self.doodler.visited_platforms[-1].rect.centerx)
            if horizontal_distance_jumo > 225:
                print(f"Big horizontal jump taken with distance of {horizontal_distance_jump}")
                reward += 12

            self.doodler.visited_platforms.append(self.doodler.last_platform)
            self.doodler.last_platform = None
            self.steps_without_new_platform = 0

        
        # else:
        #     self.steps_without_new_platform += 1
        #     reward += self.steps_without_new_platform * -0.01

        #print(f"Reward after checking steps with new platform {reward}")
        # Penalize for staying in the same platform. 
        # Handled in Doodler and Platform Class. Only when collision, count the number of collisions and
        # add negative reward to self.doodler.reward. After, make it 0 and in the next collision, more negative reward
        # will be added rather than exponentially incresing it.
        reward += self.doodler.reward

        # Reward for multiple good jumps on different platforms without repeating
        if self.doodler.different_platform_jumps >= 3 and self.doodler.collision == True:
            self.doodler.collision = False
            reward += self.doodler.different_platform_jumps * 5

        #Calculate number of jumps
        if (-(self.doodler.reward / 1)) == 3:
            self.terminated = True
            reward -= 50

        self.doodler.reward = 0
        self.previous_score = self.doodler.score
        self.last_height = self.doodler.current_height
        
        if self.doodler.current_height > self.record_height:
            self.record_height = self.doodler.current_height + 50
            #print(f"New Record Height {self.record_height}")
            reward += 20  # Reward for reaching new record height
        
        #print(f"Reward: {reward}")
        return reward

if __name__ == '__main__':
    print("START")

    env = DoodleEnv() 
    #env.reset()

    total_reward = 0
    terminated = False

    for episode in range(100):
        observation, info = env.reset()
        terminated = False
        print("Starting Episode: ", episode)
        while not terminated:
            action = env.action_space.sample()
            observation, reward, terminated, truncated, info = env.step(action)

            total_reward += reward



