import pygame
from celestial_class import Celestial, Spaceship

pygame.init()
WIDTH, HEIGHT = 1000, 1000 #capitals cause constants
FPS = 30 #speed of simu depend s also on fps... not good
WHITE = (255,255,255) #RGB values
YELLOW = (255,255,0)
BLUE = (100,149,237)
RED = (188,39,50)
DARK_GREY = (80,78,81)
JUPITER = pygame.transform.scale(pygame.image.load("jupiter.png"), (25*2,25*2))
FONT = pygame.font.SysFont("comicsans", 16)
BACKGND = pygame.transform.scale(pygame.image.load("background.jpg"), (WIDTH, HEIGHT))
TRAIL = 120 #nb pts disp in trail of celestial bodies, OoM:240 is Mercury full cycle
SHIP_TRAIL = 15
LAUNCH_SPEED = 1e-6

#Sligshot effet :
SHIP_MASS = 1e5 #approx 5% sun's mass
SHIP_SIZE = 4

def scale(position):
    """return position scaled to be displayed properly"""

def unscale(scaled_position):
    """return de-scaled position"""

def draw(celestial_body, win, display_distance_to_sun=True):
    """
    This method is used to draw a celestial body in the window as well as its trajectory
    If body is a Spaceship, no need to scale it, drawn directly where mouse clicks

    :param: trail : nb pts disp in trail of celestial bodies, OoM:240 is Mercury full cycle
                    (speed simul affects it)
    :param: ship_trail : nb pts disp in trail of spaceship
    """
    simu_scale = Celestial.simu_SCALE
    x = celestial_body.x * simu_scale + WIDTH / 2
    y = celestial_body.y * simu_scale + HEIGHT / 2

    if len(celestial_body.orbit) > 2 and celestial_body.trail:
        scaled_points = []
        for point in celestial_body.orbit[-celestial_body.trail:]:
            x_past, y_past = point
            x_past = x_past * simu_scale + WIDTH / 2
            y_past = y_past * simu_scale + HEIGHT / 2
            scaled_points.append((x_past, y_past))
        pygame.draw.lines(win, celestial_body.color, False, scaled_points, 1)

    pygame.draw.circle(win, celestial_body.color, (x, y), celestial_body.radius)

    if not celestial_body.sun and display_distance_to_sun:
        distance_text = FONT.render(f"{round(celestial_body.distance_to_sun / Celestial.AU, 3)} AU", 1, WHITE)
        text_x = min(max(x, 0), WIDTH - 70)
        text_y = min(max(y, 0), HEIGHT - 20)
        win.blit(distance_text, (text_x, text_y))

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
    def render(self, win):
        pygame.draw.rect(win, 'darkgray', self.container_rect)
        pygame.draw.rect(win, 'blue', self.button_rect)
        slider_text = FONT.render(f"{round(self.get_value())} {self.value_unit}", 1, WHITE)
        win.blit(slider_text, (self.right_pos+5, self.pos[1]))

def init_planets():
    sun = Celestial("Sun", 0, 0, 0, 0, 30, YELLOW, 1.98892e30, sun=True) #radius is randomly picked, mass is accurate and in kg
    earth = Celestial("Earth", -1 * Celestial.AU, 0,  0, 29.783 *1000, 16, BLUE, 5.9742e24)
    mars = Celestial("Mars", -1.524 * Celestial.AU, 0, 0, 24.077 * 1000, 12, RED, 6.39e23)
    mercury = Celestial("Mercury", 0.387*Celestial.AU, 0, 0, -47.4 * 1000, 8, DARK_GREY, 3.30e23)
    venus = Celestial("Venus", 0.723*Celestial.AU, 0, 0, -35.02 * 1000, 14, WHITE, 4.8685e24)

def create_ship(loc, mouse):
    """Basic decomposition of velocity in function of position object and position mouse
    just draw a triangle if unclear"""
    simu_scale = Celestial.simu_SCALE
    x = (loc[0] - WIDTH / 2) / simu_scale #adjust scale to fit with how we position the planets
    y = (loc[1] - HEIGHT / 2) / simu_scale
    x_mouse = (mouse[0] - WIDTH / 2) / simu_scale #adjust scale to fit with how we position the planets
    y_mouse = (mouse[1] - HEIGHT / 2) / simu_scale
    x_vel = (x_mouse - x) * LAUNCH_SPEED
    y_vel = (y_mouse - y) * LAUNCH_SPEED
    obj = Spaceship("Spaceship", x, y, x_vel, y_vel, SHIP_SIZE, "red", SHIP_MASS)
    return obj

def main(duration=None):
    """
    This function create an infinite loop
    this is used to keep track of the events that are occuring
    here the only event is closing the window

    param: duration: in sec, duration before the simulation is closed
                     if None, simu ends only if manually closed
                     if 0, simu will not run

    """
    WIN = pygame.display.set_mode((WIDTH, HEIGHT))  # this is our window (a pygame surface)
    pygame.display.set_caption("Planet Simulation")
    simu_TIMESTEP_slider = Slider((40, 40), (600, 15), Celestial.simu_TIMESTEP/3600, 1, 600, "hour/sec")

    clock = pygame.time.Clock() #needed in to ctrl speed of the sim and not let it be the speed of our computer
    run = True

    tmp_obj_pos = None

    if duration or duration==0:
        count = duration * FPS #nb of frame before exit
    else: count = 1
    while run and count>0:
        if duration:
            count -= 1

        clock.tick(FPS)
        WIN.blit(BACKGND, (0,0))
        simu_TIMESTEP_slider.render(WIN)

        mouse_pos = pygame.mouse.get_pos()
        mouse_press = pygame.mouse.get_pressed()
        if simu_TIMESTEP_slider.container_rect.collidepoint(mouse_pos) and mouse_press[0]:
            simu_TIMESTEP_slider.move_slidder(mouse_pos)
            Celestial.set_simu_TIMESTEP(3600*simu_TIMESTEP_slider.get_value())

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if tmp_obj_pos:
                    spaceship = create_ship(tmp_obj_pos, mouse_pos)
                    tmp_obj_pos = None
                else:
                    tmp_obj_pos = mouse_pos

        if tmp_obj_pos:
            pygame.draw.line(WIN,"white", tmp_obj_pos, mouse_pos, 2)
            pygame.draw.circle(WIN, "red", tmp_obj_pos, SHIP_SIZE)

        nb_days_TIMESTEP = Celestial.get_simu_TIMESTEP()/(3600*24) #we divide the timestep in days
        nb_complete_days = round(nb_days_TIMESTEP)
        remains = nb_days_TIMESTEP - nb_complete_days #we keep the rest
        for body in Celestial.list_bodies[:]:
            for i in range(nb_complete_days): #we will update 1 day at the time
                body.update_position(Celestial.list_bodies, timestep=3600*24)
            body.update_position(Celestial.list_bodies, timestep=remains*3600*24)
            draw(body, WIN, display_distance_to_sun=False)
        for ship in Spaceship.list_bodies[:]:
            for i in range(nb_complete_days):  # we will update 1 day at the time
                ship.update_position(Spaceship.list_bodies + Celestial.list_bodies, timestep=3600 * 24)
            ship.update_position(Spaceship.list_bodies, timestep=remains * 3600 * 24)
            draw(ship, WIN, display_distance_to_sun=False)

            #off_screen = body.x < -1000 or body.x > WIDTH+1000 or body.y < -1000 or body.y > HEIGHT+1000
            #if off_screen:
            #Celestial.list_bodies.remove(body)


        pygame.display.update()

    pygame.quit

if __name__ == "__main__":
    Celestial.set_simu_SCALE(250/ Celestial.AU) #1AU=100px
    Celestial.set_simu_TIMESTEP(3600*24) #1day
    Celestial.trail = TRAIL
    Spaceship.trail = SHIP_TRAIL
    init_planets()
    main()

"""what to do now : 
 
random asteroid that croses the screen (add it to planet list wich will be a class attribute and delete after too far away x or y

day * 365 does not work why ? fps control speed need to investigate that as well

bouton pour reset view sur soleil

bug : get_value not correspond to value set in first place
selon gpt c'est une erreur d'arondis
en effet si je passe de max vlaue 732 à 48 il n'y a plus d'erreur, le slider a assez de px par rapport à ce qu'il rpz
test anecdotique : faire en sorte que la valeur qu'on met dans le slider correspond à celle qui est récupérer par le script

adding reverse time and delete old value of trajectory

ajouter test : (GUI test)
default parameter works, circles
using slider works, it indeed speed up simul

do not display UA for ship or simplify

make slider not producing ships

make ship disapear
or rebound
or merge with body
create a chrono and best score to make is stay the longer (but need to make it disapear if border of screen


fix background
fix middle button creating ships

downscale all number by 1e15 in order to ease my computer

lower influence of sun if close to a planet in order to make it possible to create sattelite


best idea so far :
    collide = merge, size and mass increase
    objectifs : - last longer
                - orbits around the sun (the more the better)
                - sattelite, ultimate goat
        dont want to create score but could find a way to check success and grant smth in return
 """