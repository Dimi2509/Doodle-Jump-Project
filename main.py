# Imports
import pygame
import random
import neat
import os
import visualize

# Initialize pygame
pygame.init()

# Screen Dimensions
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600

# Create screen / Set title
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Doodle - Game")

# Create Sprite Groups
platform_group = pygame.sprite.Group()

# Set frame rate
clock = pygame.time.Clock()
FPS = 60

# Game variables
GRAVITY = 1
MAX_PLATFORMS = 6
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


def create_platform(platform):
    p_w = random.randint(40, 60)
    p_x = random.randint(0, SCREEN_WIDTH-p_w)
    p_y = platform.rect.y - random.randint(80, 120)

    # 80 20 % to spawn green and blue platforms respectively
    if random.random() < 0.8:
        platform = Platform(p_x, p_y, p_w)
    else:
        platform = BluePlatform(p_x, p_y, p_w)

    return platform


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

    def move(self):
        # Reset Variables
        dx = 0
        dy = 0
        scroll = 0
        # Keeypresses
        key = pygame.key.get_pressed()
        if key[pygame.K_LEFT]:
            dx -= 10
            self.flip = True
        if key[pygame.K_RIGHT]:
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
                        self.rect.bottom = platform.rect.top
                        dy = 0
                        self.vel_y = -20
        
        # Scroll scenario
        if self.rect.top <= SCROLL_THRESH:
            if self.vel_y < 0:
                # Move platforms opposite to player movement only when going up
                scroll = -dy
                # Add score
                self.score += abs(dy//10)

        # Update rectangle position
        self.rect.x += dx
        self.rect.y += dy + scroll

        return scroll
    

    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False),(self.rect.x - 20, self.rect.y - 15))

        # Draw Score, this will be removed later.
        font = pygame.font.Font("freesansbold.ttf", 20)
        text = font.render(str(self.score), True, BLACK)
        text_rect = text.get_rect()
        text_rect.center = (SCREEN_WIDTH // 2, 20)
        screen.blit(text, text_rect)


# Platform class
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(platform_image, (width, 10))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self, scroll):
        self.rect.y += scroll

        if self.rect.top > SCREEN_HEIGHT:
            self.kill()


class BluePlatform(pygame.sprite.Sprite):
    def __init__(self, x, y, width):
        #super().__init__(x, y, width)
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(blue_platform_image, (width, 10))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.direction = 1
        self.max_distance = 30
        self.initial_x = x

    def update(self, scroll):
        self.rect.y += scroll
     
        self.rect.x += self.direction  # Move the platform horizontally
        # Change direction if the platform reaches the maximum distance or screen edges
        if abs(self.rect.x - self.initial_x) >= self.max_distance or self.rect.right >= SCREEN_WIDTH or self.rect.left <= 0:
            self.direction *= -1

        if self.rect.top > SCREEN_HEIGHT:
            self.kill()


class Game():
    # Player Instance
    doodler = Doodle(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 150)

    # Create starting platform
    platform = Platform(SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT - 50, 100)
    platform_group.add(platform)

    # Game loop
    running = True
    while running:
        # Setting FPS limit
        clock.tick(FPS)

        if restart_game == False:
            # Draw Background and score
            screen.blit(background_img, (0, 0))

            # Move Character
            scroll = doodler.move()

            # Create new platforms
            if len(platform_group) < MAX_PLATFORMS:
                platform = create_platform(platform)
                platform_group.add(platform)

            # Draw Character
            platform_group.draw(screen)
            doodler.draw()
            
            platform_group.update(scroll)

            # Restart game if player falls
            if doodler.rect.top > SCREEN_HEIGHT:
                restart_game = True 
            
        else:
            # If player falls, restart game resetting all variables
            restart_game = False
            doodler.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 150)
            doodler.vel_y = 0
            doodler.score = 0
            platform_group.empty()
            # Create starting platform
            platform = Platform(SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT - 50, 100)
            platform_group.add(platform)


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Update Display
        pygame.display.update()

    pygame.quit()


if __name__ == "__main__":
    Game()