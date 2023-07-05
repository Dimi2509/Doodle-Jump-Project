# Imports
import pygame
import random

# Initialize pygame
pygame.init()

# Screen Dimensions
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600

# Create screen / Set title
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Doodle - Game")

# Set frame rate
clock = pygame.time.Clock()
FPS = 60

# Game variables
GRAVITY = 1
MAX_PLATFORMS = 10

# Colours
WHITE = (255,255,255)
RED = (255,0,0)
# Load images
background_img = pygame.image.load("img/background.png").convert_alpha()
doodle_img = pygame.image.load("img/doodle.png").convert_alpha()
platform_image = pygame.image.load("img/green_plataform.png").convert_alpha()

class Doodle():
    def __init__(self, x ,y):
        self.image = pygame.transform.scale(doodle_img, (70, 70))
        self.width = 30
        self.height = 50
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.center = (x, y)
        self.vel_y = 0
        self.flip = False

    def move(self):

        # Reset Variables
        dx = 0
        dy = 0
        
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
                # Check if above platform
                if self.rect.bottom < platform.rect.centery:
                    if self.vel_y > 0:
                        self.rect.bottom = platform.rect.top
                        dy = 0
                        self.vel_y = -20

        # Limit Screen Ground
        if self.rect.bottom + dy > SCREEN_HEIGHT:
            dy = 0
            self.vel_y = -20

        # Update rectangle position
        self.rect.x += dx
        self.rect.y += dy

    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False),(self.rect.x - 20, self.rect.y - 15))
        pygame.draw.rect(screen , WHITE, self.rect, 2)
        pygame.draw.circle(screen, RED, self.rect.center, 2)
        pygame.draw.circle(screen, RED, self.rect.topright, 2)

# Platform class
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(platform_image, (width, 10))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y



# Player Instance
doodler = Doodle(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 150)

# Create Sprite Groups
platform_group = pygame.sprite.Group()

# Create Temporary Platforms
for p in range(MAX_PLATFORMS):
    p_w = random.randint(40, 60)
    p_x = random.randint(0, SCREEN_WIDTH-p_w)
    p_y = p * random.randint(80, 120)
    platform = Platform(p_x, p_y, p_w)
    platform_group.add(platform)

# Game loop
running = True
while running:

    # Setting FPS limit
    clock.tick(FPS)

    # Move Character
    doodler.move()

    # Draw Background
    screen.blit(background_img, (0, 0))

    # Draw Character
    platform_group.draw(screen)
    doodler.draw()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update Display
    pygame.display.update()

pygame.quit()
