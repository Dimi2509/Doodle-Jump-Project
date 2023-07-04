import pygame

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

# Colours
WHITE = (255,255,255)

# Load images
background_img = pygame.image.load("img/background.png").convert_alpha()
doodle_img = pygame.image.load("img/doodle_right.png").convert_alpha()

class Doodle():
    def __init__(self, x ,y):
        self.image = pygame.transform.scale(doodle_img, (45, 45))
        self.width = 30
        self.height = 40
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.center = (x, y)
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

        # Limit Screen
        if self.rect.left + dx < 0:
            dx = - self.rect.left
        if self.rect.right + dx > SCREEN_WIDTH:
            dx = SCREEN_WIDTH - self.rect.right

        # Update rectangle position
        self.rect.x += dx
        self.rect.y += dy

    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False),(self.rect.x, self.rect.y))
        pygame.draw.rect(screen , WHITE, self.rect, 2)

doodler = Doodle(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 150)

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
    doodler.draw()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update Display
    pygame.display.update()

pygame.quit()
