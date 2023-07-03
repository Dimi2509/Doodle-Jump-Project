import pygame

# Screen Dimensions
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 900

# Character
x = SCREEN_WIDTH // 2
y = SCREEN_HEIGHT - 100

class Doodle:
    def __init__(self):
        self.SCREEN_WIDTH = SCREEN_WIDTH
        self.SCREEN_HEIGHT = SCREEN_HEIGHT
    
        self.x = x
        self.y = y
        self.speed = 10
        self.is_jumping = False
        self.can_jump = True
        self.jump_velocity = 40  # Increase the initial jump velocity
        self.gravity = 3.5  # Increase the gravity value for faster falling

    def draw(self):
        screen.blit(doodle_size, (self.x, self.y))

    def move(self, keys):
        if keys[pygame.K_LEFT]:
            self.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.x += self.speed

        # Jump logic
        if keys[pygame.K_SPACE] and self.can_jump:
            self.is_jumping = True
            self.jump_velocity = 40
            self.can_jump = False

        if self.is_jumping:
            self.y -= self.jump_velocity
            self.jump_velocity -= self.gravity

            if self.jump_velocity < 0:
                self.is_jumping = False

        # Apply gravity
        self.y += self.gravity

        # Border limits
        if self.x < 0:
            self.x = 0
        if self.x > self.SCREEN_WIDTH - 100:
            self.x = self.SCREEN_WIDTH - 100
        if self.y < 0:
            self.y = 0
        if self.y > self.SCREEN_HEIGHT - 100:
            self.y = self.SCREEN_HEIGHT - 100
            self.can_jump = True

pygame.init()

# Create screen
doodler = Doodle()
screen_size = (SCREEN_WIDTH, SCREEN_HEIGHT)
screen = pygame.display.set_mode(screen_size)

# Set title
pygame.display.set_caption("Doodle - Game")

# Doodle Image Configuration
doodle_img = pygame.image.load("img/doodle_right.png")
doodle_size = pygame.transform.scale(doodle_img, (100, 100))

# Background image
background_img = pygame.image.load("img/background.png")
background = pygame.transform.scale(background_img, (SCREEN_WIDTH, SCREEN_HEIGHT))

# Platform image
platform_img = pygame.image.load("img/green_plataform.png")
platform_SCREEN_WIDTH = 100
platform_SCREEN_HEIGHT = 50
platform_green = pygame.transform.scale(platform_img,(platform_SCREEN_WIDTH,platform_SCREEN_HEIGHT))
platform_x = SCREEN_WIDTH // 2 - platform_SCREEN_WIDTH // 2
platform_y = SCREEN_HEIGHT - 200

# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Key press detection
    keys = pygame.key.get_pressed()
    doodler.move(keys)

    # Check collision with platform
    if doodler.y + 100 >= platform_y and doodler.y + 100 <= platform_y + platform_SCREEN_HEIGHT and doodler.x + 100 >= platform_x and doodler.x <= platform_x + platform_SCREEN_WIDTH:
        doodler.y = platform_y - 100

    # Draw Screen
    screen.blit(background, (0, 0))
    screen.blit(platform_green, (platform_x, platform_y))
    doodler.draw()
    pygame.display.flip()

pygame.quit()
