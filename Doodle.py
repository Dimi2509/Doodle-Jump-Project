import pygame
import random
import os
from enum import Enum

# # Initialize pygame
# pygame.init()

# Screen Dimensions
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600

# Create screen / Set title
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Doodle - Game")

# Create Sprite Groups
#platform_group = pygame.sprite.Group()

# # Set frame rate
# clock = pygame.time.Clock()
# FPS = 60

# Game variables
GRAVITY = 1
MAX_PLATFORMS = 8 # 6
SCROLL_THRESH = 225
restart_game = False

# Colours
WHITE = (255,255,255)
RED = (255,0,0)
BLACK = (0,0,0)

# Load images
background_img = pygame.image.load("img/background.png").convert_alpha()
doodle_img = pygame.image.load("img/doodle.png").convert_alpha()
platform_image = pygame.image.load("img/green_plataform.png").convert_alpha()
blue_platform_image = pygame.image.load("img/blue_plataform.png").convert_alpha()



class Actions(Enum):
    NONE = 0
    LEFT = 1
    RIGHT = 2

class Doodle():
    def __init__(self, x ,y):
        self.image = pygame.transform.scale(doodle_img, (70, 70))
        self.width = 30
        self.height = 50
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.center = (x, y)
        self.vel_y = 0
        self.flip = False
        self.score = 0
        self.last_platform = None
        self.visited_platforms = []
        self.platform_reused_count = 0
        self.reward = 0
        self.debug_mode = False
        self.current_height = 0
        self.different_platform_jumps = 0
        self.collision = False

    def move(self, action, platform_group):
        # Reset Variables
        dx = 0
        dy = 0
        scroll = 0
        
        # If action is 0, do not move, if action is 1, move left, if action is 2, move right
        if action == 1:
            dx = -10
            self.flip = True

        if action == 2:
            dx = 10
            self.flip = False

        # Gravity
        self.vel_y += GRAVITY 
        dy += self.vel_y

        # Limit Screen
        if self.rect.left + dx < 0:
            dx = self.rect.left
        if self.rect.right + dx > SCREEN_WIDTH:
            dx = SCREEN_WIDTH - self.rect.right

        #print(self.rect.left," ", self.rect.right)
        
        # Platform Collision
        for platform in platform_group:
            # Collision in the y direcction
            if platform.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                # Apply collision only when falling
                if self.rect.bottom < platform.rect.centery:
                    if self.vel_y > 0:
                        if platform.collided != True:
                            platform.collision_count = 0
                            platform.collided = True  
                            self.last_platform = platform  
                            self.different_platform_jumps += 1   # Count the number of individual platforms jumped on in a row
                                                                 # for an extra reward     
                        else:
                            platform.collision_count += 1
                            self.different_platform_jumps = 0
                            self.reward -= platform.collision_count * 1

                        self.collision = True
                        self.rect.bottom = platform.rect.top
                        dy = 0
                        self.vel_y = -20
        
        # Scroll scenario
        if self.rect.top <= SCROLL_THRESH:
            if self.vel_y < 0:
                # Move platforms opposite to player movement only when going up
                scroll = -dy
                self.current_height += scroll
                #print(self.current_height)
                # Add score
                self.score += abs(dy//10)

        # Update rectangle position
        self.rect.x += dx
        
        #print(f"Doodler current height: {self.current_height}")
        self.rect.y += dy + scroll

        return scroll
    

    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False),(self.rect.x - 20, self.rect.y - 10)) #-15

        keys = pygame.key.get_pressed()
        if keys[pygame.K_h]:
            self.debug_mode = not self.debug_mode
        
        if self.debug_mode:
            pygame.draw.rect(screen, (255, 0, 0), self.rect, 2)
            # Draw threshold line 10 pixels below doodler
            threshold_y_bot = self.rect.bottom + 25
            pygame.draw.line(screen, (0, 255, 0), (0, threshold_y_bot), (SCREEN_WIDTH, threshold_y_bot), 2)
        
            threshold_y_top = self.rect.centery + 15
            pygame.draw.line(screen, (0, 255, 0), (0, threshold_y_top), (SCREEN_WIDTH, threshold_y_top), 2)
        

        # Draw Score, this will be removed later.
        font = pygame.font.Font("freesansbold.ttf", 20)
        text = font.render(str(self.score), True, BLACK)
        text_rect = text.get_rect()
        text_rect.center = (SCREEN_WIDTH // 2, 20)
        screen.blit(text, text_rect)

        # Debug mode text
        font2 = pygame.font.Font("freesansbold.ttf", 8)
        text = font2.render("H for DebugMode", True, BLACK)
        text_rect = text.get_rect()
        text_rect.center = (SCREEN_WIDTH // 5, 20)
        screen.blit(text, text_rect)

# Platform class
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, image):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(image, (width, 10))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.collided = False
        self.collision_count = 0
        self.platform_distance_to_doodler = 0

    def update(self, scroll, visited_platforms):
        self.rect.y += scroll
        # Check if self in visited_platforms list and if so, remove it
        if self.rect.top > SCREEN_HEIGHT:
            if self in visited_platforms:
                visited_platforms.pop(0)
            self.kill()
        

    @classmethod
    def create_platform(cls, platform_group):
        p_w = random.randint(60, 120) # 40 ,80
        p_x = random.randint(0, SCREEN_WIDTH-p_w)
        p_y = (platform_group.sprites()[-1].rect.y) - random.randint(60, 110) # 80, 120

        #if Platform.platform_count < MAX_PLATFORMS:
        if len(platform_group) < MAX_PLATFORMS:
            #print(len(platform_group))
            # 80 20 % to spawn green and blue platforms, respectively
            if random.random() < 0.8:
                platform_group.add(Platform(p_x, p_y, p_w, platform_image))
            else:
                platform_group.add(BluePlatform(p_x, p_y, p_w, blue_platform_image))

            Platform.create_platform(platform_group)


class BluePlatform(Platform):
    def __init__(self, x, y, width, image, max_distance=30):
        super().__init__(x, y, width, image)
        self.direction = 1
        self.max_distance = max_distance
        self.initial_x = x

    def update(self, scroll, visited_platforms):
        super().update(scroll, visited_platforms)
        self.rect.x += self.direction  # Move the platform horizontally

        # Change direction if the platform reaches the maximum distance or screen edges
        if abs(self.rect.x - self.initial_x) >= self.max_distance or self.rect.right >= SCREEN_WIDTH or self.rect.left <= 0:
            self.direction *= -1

# class GameEnv():
#     # Player Instance
#     doodler = Doodle(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 150)

#     # Create starting platform
#     platform = Platform(SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT - 50, 100, platform_image)
#     platform_group.add(platform)

#     # Game loop
#     running = True
#     while running:
#         # Setting FPS limit
#         clock.tick(FPS)

#         if restart_game == False:
#             # Draw Background and score
#             screen.blit(background_img, (0, 0))

#             # Create new platforms
#             if len(platform_group) < MAX_PLATFORMS:
#                 Platform.create_platform()

#             # Move Character
#             scroll = doodler.move(random.randint(0, len(Actions)))
#             platform_group.update(scroll)

#             # Draw Character and platforms
#             platform_group.draw(screen)
#             doodler.draw()
            
            

#             # Restart game if player falls
#             if doodler.rect.top > SCREEN_HEIGHT:
#                 restart_game = True 
            
#         else:
#             # If player falls, restart game resetting all variables
#             restart_game = False
#             doodler.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 150)
#             doodler.vel_y = 0
#             doodler.score = 0
#             platform_group.empty()
#             # Create starting platform
#             platform = Platform(SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT - 50, 100, platform_image)
#             platform_group.add(platform)


#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 running = False

#         # Update Display
#         pygame.display.update()

#     pygame.quit()


# if __name__ == "__main__":
#     GameEnv()