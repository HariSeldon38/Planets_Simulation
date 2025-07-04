import math

class Celestial:
    """
    This class defines celestials bodies like planets especially.
    It defines also method to calc forces applied to a body by other bodies
    and the velocity variation that this forces produce.

    Two class attribute (simu_SCALE and simu_TIMESTEP) are concerning a simulation
    and need to be set in order to use update_position.
    """
    AU = 1.495979e11 #Astronomical Unit in meters (distance Sun-Earth)
    G = 6.67428e-11 #Gravitationnal cst

    #Next block is concerning the simulation
    simu_SCALE = None
    simu_TIMESTEP = None
    @classmethod
    def set_simu_SCALE(cls, scale):
        """set simu scale in         """ #to think about
        cls.simu_SCALE = scale
    @classmethod
    def set_simu_TIMESTEP(cls, time_scale):
        """set delta time in sec : the simu elapsed time between each update_position"""
        cls.simu_TIMESTEP = time_scale


    def __init__(self, x, y, radius, color, mass):
        """ TBD """
        self.x = x #meters away from the Sun
        self.y = y
        self.radius = radius
        self.color = color
        self.mass = mass

        self.orbit = [] #keep track of all the pts the planet as traveled along
        self.sun = False #if the planet is the Sun we will not display orbit
        self.distance_to_sun = 0

        self.x_vel = 0 #x_axis velocity in m/s
        self.y_vel = 0 #y_axis velocity in m/s

    def attraction(self, other):
        """
        This method returns the force of attraction between two planets (in Newton)
        returns : force_x : x-axis force
                  force_y : y-axis force
        """
        distance_x = other.x - self.x
        distance_y = other.y - self.y
        distance = math.sqrt(distance_x**2 + distance_y**2)

        if other.sun:
            self.distance_to_sun = distance

        force = self.G * self.mass * other.mass / distance**2
        theta = math.atan2(distance_y, distance_x)
        force_x = math.cos(theta) * force
        force_y = math.sin(theta) * force

        return force_x, force_y

    def update_position(self, planets):
        """
        Update the position of a given planet
        """
        total_fx = total_fy = 0
        for planet in planets:
            if self == planet: #when iterating we will skip the planet for which we are calculation applied forces
                continue

            fx, fy = self.attraction(planet)
            total_fx += fx
            total_fy += fy

        self.x_vel += (total_fx / self.mass) * self.simu_TIMESTEP #F=m*a --> accel = F/m | a = dv/dt --> dv = a * dt
        self.y_vel += (total_fy / self.mass) * self.simu_TIMESTEP

        self.x += self.x_vel * self.simu_TIMESTEP
        self.y += self.y_vel * self.simu_TIMESTEP
        self.orbit.append((self.x, self.y))