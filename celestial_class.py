import numpy
import pygame

def simplify_consecutive(lst):
    """remove consecutive repeated values
    in lists contained in a dict"""
    if not lst:
        return []

    simplified = [lst[0]]
    for val in lst[1:]:
        if val != simplified[-1]:
            simplified.append(val)
    return simplified

WIDTH, HEIGHT = 900, 900
def scale(position, width, height, simu_scale):
    """I know it is awful to code like that
    but I want to get to the next project now so f it"""
    x = position[0] * simu_scale + width / 2
    y = position[1] * simu_scale + height / 2
    return x,y

class Celestial:
    """
    This class defines celestials bodies like planets especially.
    It defines also method to calc forces applied to a body by other bodies
    and the velocity variation that this forces produce.

    Two class attribute (simu_SCALE and simu_TIMESTEP) are concerning a simulation
    and need to be set in order to use update_position.
    """
    AU = 1.495979e11 #Astronomical Unit in meters (distance Sun-Earth)
    epsilon = 3e5 #avoid divergence of force for low distance
    list_bodies = []

    #Next block is concerning the simulation
    simu_SCALE = None
    simu_TIMESTEP = None
    trail = None #nb pts disp in trail of celestial bodies, OoM:240 is Mercury full cycle
    @classmethod
    def set_simu_SCALE(cls, scale):
        """set simu scale in         """ #to think about
        cls.simu_SCALE = scale
    @classmethod
    def set_simu_TIMESTEP(cls, time_scale):
        """set delta time in sec : the simu elapsed time between each update_position
        nb second passed per frame of the simu"""
        cls.simu_TIMESTEP = time_scale
    @classmethod
    def get_simu_TIMESTEP(cls):
        return cls.simu_TIMESTEP

    def __init__(self, name, x, y, x_vel, y_vel, radius, color, mass, perceived_mass=None, sun=False):
        """ TBD """
        self.name = name
        self.x = x #meters away from the Sun (center)
        self.y = y
        self.radius = radius
        self.color = color
        self.mass = mass
        if not perceived_mass: #mass that will feel the spaceship in order to allow satellites
            self.perceived_mass = mass
        else:
            self.perceived_mass = perceived_mass
        self.orbit = [] #keep track of all the pts the planet as traveled along
        self.sun = sun #if the planet is the Sun we will not display orbit
        self.distance_to_sun = 0
        self.x_vel = x_vel #x_axis velocity in m/s
        self.y_vel = y_vel #y_axis velocity in m/s
        self.list_bodies.append(self)

        if self.__class__ == Celestial:
            if self.sun:
                self._leftrect = pygame.Rect(0, 0, 900, 20)  # checkpoint that will follow sun's position ...
                self._rightrect = pygame.Rect(0, 0, 900, 20)  # ... will be used to detect if a ship is orbiting around the sun
            else:
                self._leftrect = pygame.Rect(0, 0, 55, 20)  # checkpoint that will follow planet position
                self._rightrect = pygame.Rect(0, 0, 55, 20)
            self._leftrect.midright = (scale((x, y), WIDTH, HEIGHT, Celestial.simu_SCALE))
            self._rightrect.midleft = (scale((x, y), WIDTH, HEIGHT, Celestial.simu_SCALE))

    @property
    def rect(self):
        self._leftrect.midright = (scale((self.x, self.y), WIDTH, HEIGHT, Celestial.simu_SCALE))
        self._rightrect.midleft = (scale((self.x, self.y), WIDTH, HEIGHT, Celestial.simu_SCALE))
        return self._leftrect, self._rightrect

    def attraction(self, other):
        """
        This method returns the force of attraction between two planets (in Newton)
        returns : force_x : x-axis force
                  force_y : y-axis force

                  the gravitational force is softened by a epsilon coef for it not to diverge
        """

        distance_x = other.x - self.x
        distance_y = other.y - self.y
        distance = numpy.sqrt(distance_x**2 + distance_y**2)

        if other.sun:
            self.distance_to_sun = distance

        force = self.mass * other.mass / (distance**2 + self.epsilon)
        theta = numpy.atan2(distance_y, distance_x)
        force_x = numpy.cos(theta) * force
        force_y = numpy.sin(theta) * force

        return force_x, force_y

    def update_position(self, planets, timestep):
        """
        Update the position of a given planet
        DO NOT use self.simu_TIMESTEP as default value it would bypass the split_step implemented in main
        """
        if timestep == 0:
            return None
        total_fx = total_fy = 0
        for planet in planets:
            if self == planet: #when iterating we will skip the planet for which we are calculation applied forces
                continue

            fx, fy = self.attraction(planet)
            total_fx += fx
            total_fy += fy

        self.x_vel += (total_fx / self.mass) * timestep #F=m*a --> accel = F/m | a = dv/dt --> dv = a * dt
        self.y_vel += (total_fy / self.mass) * timestep

        self.x += self.x_vel * timestep
        self.y += self.y_vel * timestep
        self.orbit.append((self.x, self.y))

    @classmethod
    def reset_class(cls):
        """method that reset the class to factory settings :
        all instances of the class will be deleted"""
        for body in cls.list_bodies:
            del body
        cls.list_bodies = []
        cls.simu_SCALE = None
        cls.simu_TIMESTEP = None
        cls.trail = None

class Spaceship(Celestial):
    list_bodies = []

    def attraction(self, other):
        """
        This method returns the force of attraction undergone by a Spaceship object by another body (in Newton)
        returns : force_x : x-axis force
                  force_y : y-axis force

                  the gravitational force is softened by a epsilon coef for it not to diverge

                  the gravitational force is increased if the other body is not the sun
                        (because it funnier if the ship feels the attraction not only caused by the sun)
                        and due to it's insignificant mass it is not possible with Celestial.attraction method)
        """

        distance_x = other.x - self.x
        distance_y = other.y - self.y
        distance = numpy.sqrt(distance_x**2 + distance_y**2)

        if other.sun:
            self.distance_to_sun = distance

        force = self.mass * other.perceived_mass / (distance ** 2 + self.epsilon)
        theta = numpy.atan2(distance_y, distance_x)
        force_x = numpy.cos(theta) * force
        force_y = numpy.sin(theta) * force

        return force_x, force_y

    last_ship = None
    def __init__(self, name, x, y, x_vel, y_vel, radius, color, mass, perceived_mass=None, sun=False):
        super().__init__(name, x, y, x_vel, y_vel, radius, color, mass, perceived_mass, sun)
        Spaceship.last_ship = self
        self._state_dict = {"Sun":[], #each of these lists will contain general postion arount a given planet
                           "Earth":[],  # 3 states possible : "left", "right", "space"
                           "Venus":[],    # left mean ship on leftrect of the planet
                           "Mars":[],        #right mean ship on rightrect
                           "Mercury":[],        #space mean ship on neither rect
                                        }

    @property
    def state_dict(self):
        for key in self._state_dict:
            self._state_dict[key] = simplify_consecutive(self._state_dict[key])
        return self._state_dict


class Moon(Spaceship):
    list_bodies = []

if __name__ == "__main__":
    def matches_pattern(lst):
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

    print(matches_pattern(["left", "space", "right", "space"]))  # True
    print(matches_pattern(["left", "space", "right", "space", "left"]))  # True
    print(matches_pattern(["space"]))  # True
    print(matches_pattern(["right", "space"]))  # True
    print(matches_pattern(["right", "space", "right"]))  # False
    print("\n")
    print(matches_pattern(["left", "space", "right", "space"]))  # ✅ True
    print(matches_pattern(["space"]))  # ✅ True
    print(matches_pattern(["right", "space"]))  # ✅ True
    print(matches_pattern(["right", "space", "right"]))  # ❌ False
    print(matches_pattern(["space", "right", "space", "left"]))  # ✅ True
    print(matches_pattern(["left", "space", "right", "left"]))  # ❌ False
    print(matches_pattern([]))

    class test():
        def __init__(self):
            Spaceship.last_ship = self
            self._state_dict = {"Sun": [],  # each of these lists will contain general postion arount a given planet
                                "Earth": [],  # 3 states possible : "left", "right", "space"
                                "Venus": [],  # left mean ship on leftrect of the planet
                                "Mars": [],  # right mean ship on rightrect
                                "Mercury": [],  # space mean ship on neither rect
                                }


        @property
        def state_dict(self):
            self._state_dict = simplify_consecutive(self._state_dict)
            return self._state_dict

    a = test()



