import pygame
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

class Slider:
    def __init__(self, pos: tuple, size: tuple, initial_val: float, min: float, max: float, value_unit: str):
        """
        This object defines a slider button that will change a continuous value while the program is running
        :param pos: position of the top left of the slider (tupple)
        :param size: (tupple)
        :param initial_val: (float)
        :param min: (float)
        :param max: (float)
        :param value_unit: what is displayed right next to slider after value
        """

        width_button = 10

        self.pos = pos
        self.size = size
        self.right_pos = self.pos[0] + size[0] #right pos only for x-axis
        self.slider_top_pos = self.pos[1] - (size[1]//2) #top pos only for y-axis
        # remember 0,0 is top left in pygame and y-axis is oriented downward

        self.min = min
        self.max = max
        self.initial_percentage = (initial_val-min)/(max-min)

        self.value_unit = value_unit

        self.container_rect = pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])
        x_pos = self.pos[0] + self.initial_percentage*(self.right_pos - self.pos[0])-width_button/2
        self.button_rect = pygame.Rect(x_pos, self.pos[1], width_button, self.size[1])
    def move_slidder(self, mouse_pos):
        self.button_rect.centerx = mouse_pos[0]
    def get_value(self):
        """return value that correspond to the position of the slider's button"""
        val_range = self.right_pos - self.pos[0]
        button_val = self.button_rect.centerx - self.pos[0]
        return (button_val/val_range)*(self.max-self.min)+self.min
    def render(self):
        pygame.draw.rect(WIN, 'darkgray', self.container_rect)
        pygame.draw.rect(WIN, 'blue', self.button_rect)
        slider_text = FONT.render(f"{round(self.get_value())} {self.value_unit}", 1, WHITE)
        WIN.blit(slider_text, (self.right_pos+5, self.pos[1]))
simu_TIMESTEP_slider = Slider((40,40), (600,15), 24, 1, 600, "hour/sec")

def main():
    """
    This function create an infinite loop
    this is used to keep track of the events that are occuring
    here the only event is closing the window
    """
    clock = pygame.time.Clock() #needed in to ctrl speed of the sim and not let it be the speed of our computer
    run = True

    sun = Celestial("Sun", 0,0, 30, YELLOW, 1.98892e30) #radius is randomly picked, mass is accurate and in kg
    sun.sun = True
    earth = Celestial("Earth", -1 * Celestial.AU, 0, 16, BLUE, 5.9742e24)
    earth.y_vel = 29.783 *1000
    mars = Celestial("Mars", -1.524 * Celestial.AU, 0, 12, RED, 6.39e23)
    mars.y_vel = 24.077 * 1000
    mercury = Celestial("Mercury", 0.387*Celestial.AU, 0, 8, DARK_GREY, 3.30e23)
    mercury.y_vel = -47.4 * 1000
    venus = Celestial("Venus", 0.723*Celestial.AU, 0, 14, WHITE, 4.8685e24)
    venus.y_vel = -35.02  * 1000

    while run:
        clock.tick(FPS)
        WIN.fill("black") #fill the backgrnd to overwrite the planets from the previous frame
        simu_TIMESTEP_slider.render()

        mouse_pos = pygame.mouse.get_pos()
        mouse_press = pygame.mouse.get_pressed()
        if simu_TIMESTEP_slider.container_rect.collidepoint(mouse_pos) and mouse_press[0]:
            simu_TIMESTEP_slider.move_slidder(mouse_pos)
            Celestial.set_simu_TIMESTEP(3600*simu_TIMESTEP_slider.get_value())

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        for planet in Celestial.list_bodies:
            planet.update_position(Celestial.list_bodies)
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

bouton pour reset view sur soleil

faire en sorte de cal plusieur fois la dérivé pr éviter siscretization trop brusque si timestep haut (garder le même fps mais fair eplus sieur fois le update avec un timestec limité)
faire test ou on prend plusieur TIMESTEP et au terme d'un temps de simulation égal comparer les résultat
    tester avec et sans le slipstep

bug : get_value not correspond to value set in first place
selon gpt c'est une erreur d'arondis
en effet si je passe de max vlaue 732 à 48 il n'y a plus d'erreur, le slider a assez de px par rapport à ce qu'il rpz
test anecdotique : faire en sorte que la valeur qu'on met dans le slider correspond à celle qui est récupérer par le script

 """