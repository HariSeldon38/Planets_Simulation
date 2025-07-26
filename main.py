import pygame
import math
import copy
from celestial_class import Celestial, Spaceship, Moon



pygame.init()
WIDTH, HEIGHT = 900, 900 #capitals cause constants
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
SHIP_TRAIL = 40
LAUNCH_SPEED = 1.7e-6
#Sligshot effet :
SHIP_MASS = 1e5 #approx 5% sun's mass
SHIP_SIZE = 4
CONTROL_RATE = 1000 #how much we'll ctrl the last ship with zqsd

def matches_pattern(lst):
    """
    return True if list match ANYHOW the pattern
    return False if
            values 'right' and 'left' are conscutive
            value 'space' is surronded by only 'right' or only 'left'
        (if repeated consecutive values we don't care list will be simplified beforehand)
            """
    pattern = ["left", "space", "right", "space"]
    n = len(lst)

    for offset in range(len(pattern)):
        match = True
        for i in range(n):
            if lst[i] != pattern[(offset + i) % len(pattern)]:
                match = False
                break
        if match:
            return True
    return False

def scale(position, width, height, simu_scale):
    """return position scaled to be displayed properly"""
    x = position[0] * simu_scale + width / 2
    y = position[1] * simu_scale + height / 2
    return x,y
def unscale(scaled_position, width, height, simu_scale):
    """return de-scaled position"""
    x = (scaled_position[0] - WIDTH / 2) / simu_scale
    y = (scaled_position[1] - HEIGHT / 2) / simu_scale
    return x, y

def draw(celestial_body, win, display_distance_to_sun=True, hitboxes=False):
    """
    This method is used to draw a celestial body in the window as well as its trajectory
    If body is a Spaceship, no need to scale it, drawn directly where mouse clicks

    :param: trail : nb pts disp in trail of celestial bodies, OoM:240 is Mercury full cycle
                    (speed simul affects it)
    :param: ship_trail : nb pts disp in trail of spaceship
    """
    position = (celestial_body.x, celestial_body.y)
    x,y = scale(position, WIDTH, HEIGHT, Celestial.simu_SCALE)

    if len(celestial_body.orbit) > 2 and celestial_body.trail:
        scaled_points = []
        for point in celestial_body.orbit[-celestial_body.trail:]:
            x_past, y_past = scale(point, WIDTH, HEIGHT, Celestial.simu_SCALE)
            scaled_points.append((x_past, y_past))
        pygame.draw.lines(win, celestial_body.color, False, scaled_points, 1)

    pygame.draw.circle(win, celestial_body.color, (x, y), celestial_body.radius)

    if not celestial_body.sun and display_distance_to_sun:
        distance_text = FONT.render(f"{round(celestial_body.distance_to_sun / Celestial.AU, 3)} AU", 1, WHITE)
        text_x = min(max(x, 0), WIDTH - 70)
        text_y = min(max(y, 0), HEIGHT - 20)
        win.blit(distance_text, (text_x, text_y))

    if hitboxes:
        if not type(celestial_body) == Celestial:
            raise TypeError("Non strict Celestial object do not have a hitbox")
        pygame.draw.rect(win, "red", celestial_body.rect[0], 1)
        pygame.draw.rect(win, "red", celestial_body.rect[1], 1)

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
    sun = Celestial("Sun", 0, 0, 0, 0, 30, YELLOW, 1.32746090e+20, sun=True) #radius is randomly picked, mass is accurate and in kg
    earth = Celestial("Earth", -1 * Celestial.AU, 0,  0, 29.783 *1000, 16, BLUE, 3.98734836e+14, 3.98734836e+19)
    mars = Celestial("Mars", -1.524 * Celestial.AU, 0, 0, 24.077 * 1000, 14, RED, 4.26486492e+13, 6.67428000e+18)
    mercury = Celestial("Mercury", 0.387*Celestial.AU, 0, 0, -47.4 * 1000, 8, DARK_GREY, 2.20251240e+13, 6.67428000e+14)
    venus = Celestial("Venus", 0.723*Celestial.AU, 0, 0, -35.02 * 1000, 11, WHITE, 3.24937322e+14, 3.33714000e+16)
    moon = Moon("Moon", -1.1 * Celestial.AU, 0, 0, 84 *1000, 3, WHITE, 4.90292609e+12)

def create_ship(loc, mouse):
    """Basic decomposition of velocity in function of position object and position mouse
    just draw a triangle if unclear"""
    x, y = unscale(loc, WIDTH, HEIGHT, Celestial.simu_SCALE) #adjust scale to fit with how we position the planets
    x_mouse, y_mouse = unscale(mouse, WIDTH, HEIGHT, Celestial.simu_SCALE)

    x_vel = (x_mouse - x) * LAUNCH_SPEED
    y_vel = (y_mouse - y) * LAUNCH_SPEED
    obj = Spaceship("Spaceship", x, y, x_vel, y_vel, SHIP_SIZE, "red", SHIP_MASS)
    return obj

def remove_lost_ship(ship):
    """Check if ship has gone far offscreen or has collided with a planet and remove it if so."""
    console_text_lost_ship = None

    #CHECK IF GO OFFSCREEN AND REMOVE
    tol = 0 #how much pixels afar from screen to consider lost
    x, y = scale((ship.x,ship.y), WIDTH, HEIGHT, Celestial.simu_SCALE)
    off_screen = x < -tol or x > WIDTH+tol or y < -tol or y > HEIGHT+tol
    if off_screen:
        Spaceship.list_bodies.remove(ship)
        console_text_lost_ship = FONT.render(
            f"{ship.name} drifts eternally through space, there are {len(Spaceship.list_bodies)} ships left.", 1, "lightgray")

    #CHECK IF COLLIDE AND REMOVE
    for planet in Celestial.list_bodies: #could improve perf to scale it once, after update pos
        x_planet, y_planet = scale((planet.x,planet.y),WIDTH,HEIGHT,Celestial.simu_SCALE)
        collided = math.sqrt((x-x_planet)**2 + (y-y_planet)**2) <= planet.radius
        if collided:
            Spaceship.list_bodies.remove(ship)
            planet.mass += 6e16
            planet.radius += 0.1
            console_text_lost_ship = FONT.render(
                f"{ship.name} has merged with {planet.name}. Don't feed it too much ! "
                f"There are {len(Spaceship.list_bodies)} ships left.", 1, "red")
    return console_text_lost_ship

def main(duration=None):
    """
    param: duration: in sec, duration before the simulation is closed
                     if None, simu ends only if manually closed
                     if 0, simu will not run
    """
    SCORE = 0
    ORBIT_DISCOVERED = False
    SATELLITE_DISCOVERED = False
    console_text = FONT.render(f"", 1, WHITE) #placeholder
    WIN = pygame.display.set_mode((WIDTH, HEIGHT))  # this is our window (a pygame surface)
    pygame.display.set_caption("Planet Simulation")
    simu_TIMESTEP_slider = Slider((10, 10), (450, 15), Celestial.simu_TIMESTEP/3600, 1, 100, "hour/sec")

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
            if event.type == pygame.MOUSEBUTTONDOWN and not simu_TIMESTEP_slider.container_rect.collidepoint(mouse_pos):
                if tmp_obj_pos:
                    spaceship = create_ship(tmp_obj_pos, mouse_pos)
                    tmp_obj_pos = None
                else:
                    tmp_obj_pos = mouse_pos
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    Spaceship.reset_class()
                    Spaceship.set_simu_SCALE(250/ Celestial.AU) #1AU=100px
                    Spaceship.set_simu_TIMESTEP(3600*10) #10 hours
                    Spaceship.trail = SHIP_TRAIL
                    console_text = FONT.render(f"ALL THE SHIP ARE GONE, THAT'S WHAT A CALL A CLEAN START", 1, WHITE)

        key = pygame.key.get_pressed()
        if Spaceship.last_ship:
            if key[pygame.K_z]:
                Spaceship.last_ship.y_vel -= CONTROL_RATE
            if key[pygame.K_s]:
                Spaceship.last_ship.y_vel += CONTROL_RATE
            if key[pygame.K_q]:
                Spaceship.last_ship.x_vel -= CONTROL_RATE
            if key[pygame.K_d]:
                Spaceship.last_ship.x_vel += CONTROL_RATE

        if tmp_obj_pos:
            pygame.draw.line(WIN,"white", tmp_obj_pos, mouse_pos, 2)
            pygame.draw.circle(WIN, "red", tmp_obj_pos, SHIP_SIZE)

        discretization_TIMESTEP = 3600*6 #we divide the timestep in quarter days
        nb_days_TIMESTEP = Celestial.get_simu_TIMESTEP()/(discretization_TIMESTEP)
        nb_complete_days = round(nb_days_TIMESTEP)
        remains = nb_days_TIMESTEP - nb_complete_days #we keep the rest
        
        orbit_count = 0
        for ship in Spaceship.list_bodies[:]:
            for i in range(nb_complete_days):  # we will update 1 quarter day at the time
                ship.update_position(Spaceship.list_bodies + Celestial.list_bodies, timestep=discretization_TIMESTEP)
            ship.update_position(Spaceship.list_bodies + Celestial.list_bodies, timestep=remains*discretization_TIMESTEP)
            draw(ship, WIN, display_distance_to_sun=False)
            tmp = remove_lost_ship(ship)
            if tmp:
                console_text = tmp
                SCORE -= 0.3

            # Check if ship is orbiting around a planet
            ship.previous_state_dict = copy.deepcopy(ship._state_dict) #storing precedent dict to compute score only if new cycles and not on every frame
            ship_px_position = scale((ship.x, ship.y), WIDTH,HEIGHT,Celestial.simu_SCALE)
            for body in Celestial.list_bodies:

                if body.rect[0].collidepoint(ship_px_position):
                    ship._state_dict[body.name].append("left")
                elif body.rect[1].collidepoint(ship_px_position):
                    ship._state_dict[body.name].append("right")
                else:
                    ship._state_dict[body.name].append("space")

                valid_pattern = matches_pattern(ship.state_dict[body.name]) #without underscore =simplify before returned
                if not valid_pattern:
                    ship._state_dict[body.name] = []

                elif len(ship._state_dict[body.name]) > 5:
                    if not ORBIT_DISCOVERED and body.name == "Sun":
                        console_text = FONT.render(f"Congrats ! You lauched a ship that orbits around the Sun ! What can you try now ?", 1, YELLOW)
                        ORBIT_DISCOVERED = True
                    if not SATELLITE_DISCOVERED and body.name in ['Earth', 'Mars']:
                        console_text = FONT.render(f"Wow ! You lauched a satellite around a planet ? That is impressive !", 1, BLUE)
                        SATELLITE_DISCOVERED = True
                    orbit_text = FONT.render(
                        f"{ship.name} : {int((len(ship._state_dict[body.name])-2)/4)} full cycles / {body.name}", 1, body.color)
                    text_x = 620
                    text_y = 10 + 22*orbit_count
                    WIN.blit(orbit_text, (text_x, text_y))
                    orbit_count += 1

            SCORE += ship.compute_score()

        for body in Celestial.list_bodies:
            for i in range(nb_complete_days):
                body.update_position(Celestial.list_bodies, timestep=discretization_TIMESTEP)
            body.update_position(Celestial.list_bodies, timestep=remains*discretization_TIMESTEP)
            draw(body, WIN, display_distance_to_sun=False, hitboxes=False)
        for body in Moon.list_bodies:
            for i in range(nb_complete_days):
                body.update_position(Celestial.list_bodies, timestep=discretization_TIMESTEP)
            body.update_position(Celestial.list_bodies, timestep=remains*discretization_TIMESTEP)
            draw(body, WIN, display_distance_to_sun=False)

        if ORBIT_DISCOVERED or SATELLITE_DISCOVERED:
            score_text = FONT.render(
                f"Score : {round(SCORE, 1)}", 1, body.color)
            WIN.blit(score_text, (30, 50))
        WIN.blit(console_text, (10, 870))
        pygame.display.update()

    pygame.quit

if __name__ == "__main__":
    Celestial.set_simu_SCALE(250/ Celestial.AU) #1AU=100px
    Celestial.set_simu_TIMESTEP(3600*10) #10 hours
    Celestial.trail = TRAIL
    Spaceship.trail = SHIP_TRAIL
    init_planets()
    main()

"""what to do now : 
 
 First thing to do if returning to this project :
 fix the awfull code I made to implement hitboxes

detect if orbit clockwork or anticlockwork

label Spaceship with a given name list)

random asteroid that croses the screen (add it to planet list wich will be a class attribute and delete after too far away x or y
class Asteroid(Spaceship):
    pass
function that randomly create asteroid with random params called every frames

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

make ship disapear
or rebound
or merge with body
create a chrono and best score to make is stay the longer (but need to make it disapear if border of screen


fix background
fix middle button creating ships : NO, great feature

downscale all number by 1e15 in order to ease my computer

lower influence of sun if close to a planet in order to make it possible to create sattelite

best idea so far :
    objectifs : - last longer
                - orbits around the sun (the more the better)
                - sattelite, ultimate goat
        dont want to create score but could find a way to check success and grant smth in return
        
bug : when moving slider too fast simu diverges


what happen when planet are colliding ? title screen ? credit ? easter egg ? 

easter egg == unlock key to move (there already but say it)
need also to find something to do for reaching a given score
 """