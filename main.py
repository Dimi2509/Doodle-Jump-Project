# Imports
import pygame
import random
import neat
import os
from visualize import draw_net, plot_stats
import math

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
MAX_PLATFORMS = 12
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
        self.scroll = 0
        self.platcoll = False
    def move_l(self):
        # Update x position
        self.rect.x -= 10

    def move_r(self):
        # Update x position
        self.rect.x += 10

    def stay(self):
        # Update x position
        self.rect.x += 0

    def collide(self):
        self.scroll = 0
        self.collided = False

        dx = 10
        dy = 0
        # Gravity
        self.vel_y += GRAVITY
        dy += self.vel_y

        # Limit Screen
        if self.rect.left - dx < 0:
            self.rect.left += dx
        if self.rect.right + dx > SCREEN_WIDTH:
            self.rect.right -= dx 
        
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
                        self.collided = True

        # update y position after collision              
        self.rect.y += dy + self.scroll

        # Scroll scenario
        if self.rect.top <= SCROLL_THRESH:
            if self.vel_y < 0:
                # Move platforms opposite to player movement only when going up
                self.scroll = -dy
                # Add score
                self.score += abs(dy//10)
                


    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False),(self.rect.x - 20, self.rect.y - 15))

    def get_closest_pl(self):
        dist_top = []
        dist_bot = []

        for platform in platform_group:
            if platform.rect.top < self.rect.centery:
                dist_top.append(math.sqrt(abs(self.rect.x - platform.rect.x)**2 + abs(self.rect.y - platform.rect.y)**2))
            else:
                dist_bot.append(math.sqrt(abs(self.rect.x - platform.rect.x)**2 + abs(self.rect.y - platform.rect.y)**2))
        
        return min(dist_top, default=0), min(dist_bot, default=0)

# Platform class
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(platform_image, (width, 10))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.collide = False

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
        self.collide = False

    def update(self, scroll):
        self.rect.y += scroll
     
        self.rect.x += self.direction  # Move the platform horizontally
        # Change direction if the platform reaches the maximum distance or screen edges
        if abs(self.rect.x - self.initial_x) >= self.max_distance or self.rect.right >= SCREEN_WIDTH or self.rect.left <= 0:
            self.direction *= -1

        if self.rect.top > SCREEN_HEIGHT:
            self.kill()


def Game(genome, config):
    # NEAT variables
    nets = []
    doodlers = []
    ge = []

    # Create doodlers with unique genomes
    for _, g in genome:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        doodlers.append(Doodle(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 150))
        g.fitness = 0
        ge.append(g)


    # Create starting platform
    platform = Platform(SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT - 50, 100)
    platform_group.add(platform)

    # Game loop
    running = True
    while running:
        # Setting FPS limit
        clock.tick(FPS)

        # Draw Background
        screen.blit(background_img, (0, 0))

        # Create new platforms
        if len(platform_group) < MAX_PLATFORMS:
            platform = create_platform(platform)
            platform_group.add(platform)

        # Draw platforms
        platform_group.draw(screen)

        # Draw doodlers and check collisions
        for x, doodler in enumerate(doodlers):
            doodler.draw()
            doodler.collide()
            # Update positive fitness if doodler collides on platform only one time
            if doodler.collided and not doodler.platcoll:
                ge[x].fitness += 10
                doodler.platcoll = True
                #print(ge[x].fitness)
    
            # Update negative fitness if doodler collides on platform more than one time
            if doodler.collided and doodler.platcoll:
                ge[x].fitness -= 2   
                #print(ge[x].fitness)
            
            # Get closes platform's distances
            dist_top, dist_bot = doodler.get_closest_pl()
            first_plat = platform_group.sprites()[0].rect.x
            second_plat = platform_group.sprites()[1].rect.x

            # NN output
            output = nets[x].activate((doodler.rect.x, doodler.rect.y, dist_top, dist_bot, doodler.vel_y))
            
            # Move doodler depending on NN output
            maxOut = max(output)
            if output[0] == maxOut and output[0] > 0.5 :
                doodler.move_r()
            elif output[1] == maxOut and output[1] > 0.5:
                doodler.move_l()
            else:
                doodler.stay()

            if ge[x].fitness < 0:
                ge[x].fitness -= 2
                nets.pop(x)
                ge.pop(x)
                doodlers.pop(x)
    

        platform_group.update(doodler.scroll)

        # Remove doodler safely if it falls off the screen, decrease fitness and remove its genome and neural network
        doodlers_to_remove = []
        for x, doodler in enumerate(doodlers):
            if doodler.rect.top > SCREEN_HEIGHT:
                ge[x].fitness -= 2
                nets.pop(x)
                ge.pop(x)
                doodlers.pop(x)
                #doodlers_to_remove.append(doodler)

        # for doodler in doodlers_to_remove:
        #     doodlers_to_remove.remove(doodler)

        # Check if all doodlers have been removed
        if len(doodlers) == 0:
            running = False
            platform_group.empty()
            break

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()

        # Update Display
        pygame.display.update()


def run(config_file):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_file)

    # Create the population, which is the top-level object for a NEAT run.
    p = neat.Population(config)

    # Add a stdout reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    # Run for up to x generations.
    winner = p.run(Game, 30)
    # draw_net(config, winner, True)
    # plot_stats(stats, ylog=False, view=True)
    # show final stats
    print('\nBest genome:\n{!s}'.format(winner))


if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config.txt')
    run(config_path)
