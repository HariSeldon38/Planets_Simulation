import pygame
import math
from celestial_class import Celestial

"""SETTING UP PYGAME WINDOW"""
pygame.init()
WIDTH, HEIGHT = 800, 800 #capitals cause constants
WIN = pygame.display.set_mode((WIDTH,HEIGHT)) #this is our window (a pygame surface)
pygame.display.set_caption("Planet Simulation")

FPS = 30

WHITE = (255,255,255) #RGB values
YELLOW = (255,255,0)
BLUE = (100,149,237)
RED = (188,39,50)
DARK_GREY = (80,78,81)

FONT = pygame.font.SysFont("comicsans", 16)

Celestial.set_simu_SCALE(250/ Celestial.AU) #1AU=100px
Celestial.set_simu_TIMESTEP(3600 *24) #1day


def draw(celestial_body, win, display_distance_to_sun=True):
    """
    This method is used to draw a celestial body in the window as well as its trajectory
    """
    simu_scale = Celestial.simu_SCALE
    x = celestial_body.x * simu_scale + WIDTH / 2  # we need to offset cause distance to the Sun (center)
    y = celestial_body.y * simu_scale + HEIGHT / 2  # ... and pygame origin is at top left corner    DOES IT CREATE A PB IF SUN IS MOVING ????

    if len(celestial_body.orbit) > 2:
        scaled_points = []
        for point in celestial_body.orbit:
            x_past, y_past = point
            x_past = x_past * simu_scale + WIDTH / 2
            y_past = y_past * simu_scale + HEIGHT / 2
            scaled_points.append((x_past, y_past))

        pygame.draw.lines(win, celestial_body.color, False, scaled_points, 1)
    pygame.draw.circle(win, celestial_body.color, (x, y), celestial_body.radius)

    if not celestial_body.sun and display_distance_to_sun:
        distance_text = FONT.render(f"{round(celestial_body.distance_to_sun / Celestial.AU, 3)}au", 1, WHITE)
        position_x_dist_text = x
        position_y_dist_text = y
        if position_x_dist_text < 0: position_x_dist_text = 0
        if position_x_dist_text > WIDTH - 70: position_x_dist_text = WIDTH - 70  # would be better to not hardcore margin here ans follow Tim footstep but to tired for that today
        if position_y_dist_text < 0: position_y_dist_text = 0
        if position_y_dist_text > HEIGHT - 20: position_y_dist_text = HEIGHT - 20  # why -20 is needed this time ? no idea
        win.blit(distance_text, (position_x_dist_text, position_y_dist_text))

def main():
    """
    This function create an infinite loop
    this is used to keep track of the events that are occuring
    here the only event is closing the window
    """
    clock = pygame.time.Clock() #needed in to ctrl speed of the sim and not let it be the speed of our computer
    run = True

    sun = Celestial(0,0, 30, YELLOW, 1.98892e30) #radius is randomly picked, mass is accurate and in kg
    sun.sun = True
    earth = Celestial(-1 * Celestial.AU, 0, 16, BLUE, 5.9742e24)
    earth.y_vel = 29.783 *1000
    mars = Celestial(-1.524 * Celestial.AU, 0, 12, RED, 6.39e23)
    mars.y_vel = 24.077 * 1000
    mercury = Celestial(0.387*Celestial.AU, 0, 8, DARK_GREY, 3.30e23)
    mercury.y_vel = -47.4 * 1000
    venus = Celestial(0.723*Celestial.AU, 0, 14, WHITE, 4.8685e24)
    venus.y_vel = -35.02  * 1000

    planets = [sun, earth, mars, mercury, venus]

    while run:
        clock.tick(FPS)
        WIN.fill("black") #fill the backgrnd to overwrite the planets from the previous frame
        #pygame.display.update() #update all the drawing done to the display

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        for planet in planets:
            planet.update_position(planets)
            draw(planet, WIN)

        pygame.display.update()

    pygame.quit

main()

"""what to do now : 
button to speed up or slow down the simulation (with display current speed in days/s
 
random asteroid that croses the screen (add it to planet list wich will be a class attribute and delete after too far away x or y

move planet list into planet class

day * 365 does not work why ?

ajouter display vitesse et acceleration

flèche qui pointe vers planet si dispariat de l'ecran ac la distance et le nom de la planete (peut se servir du display de base)
 """