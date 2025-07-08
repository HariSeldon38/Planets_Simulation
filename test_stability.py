import unittest
import main
from celestial_class import Celestial
import numpy as np
import pygame

duration_low = [5] #in sec, real duration of test for low_TIMESTEP
low_TIMESTEP = 3600*24 #1day/frame
high_TIMESTEP = 3600*24 * 60 #2months
duration_high = [duration * low_TIMESTEP / high_TIMESTEP for duration in duration_low]
#pb : duration * FPS during simulation
#but duration_high * FPS cannot be integer so final frame should not be complete...
#we'll run main twice for high timestep in order to adjust TIMESTEP of final frame

class TestStability(unittest.TestCase):
    """"Test in order to check the stability of our model with respect to time"""

    def test_stability_time(self):
        """
        Compare the state of the simulation after the same simulated time for a low TIMESTEP and for a high TIMESTEP
        
        return : the difference of position and velocity for each defined planets between low and high TIMESTEP
        

        apprend comment display et return truc pendant un test
        apprendre aussi à paramétrer les tests
        """
        list_position_low = []
        list_position_low = []
        list_velocity_low = []
        list_velocity_low = []
        list_position_high = []
        list_position_high = []
        list_velocity_high = []
        list_velocity_high = []
        for idx_test in range(len(duration_low)):

            WIN = pygame.display.set_mode((800, 800))  # this is our window (a pygame surface)
            pygame.display.set_caption("Planet Simulation")
            #we begin with low timestep, the simu will last duration_low[idx_test] seconds
            Celestial.reset_class()
            Celestial.set_simu_SCALE(250 / Celestial.AU)
            Celestial.set_simu_TIMESTEP(low_TIMESTEP)
            main.main(duration_low[idx_test])
            #retrieve final values (position and speed)
            for planet in Celestial.list_bodies:
                list_position_low.append(planet.x)
                list_position_low.append(planet.y)
                list_velocity_low.append(planet.x_vel)
                list_velocity_low.append(planet.y_vel)
            low_tot_simu_time = Celestial.debug #in days

            WIN = pygame.display.set_mode((800, 800))  # this is our window (a pygame surface)
            pygame.display.set_caption("Planet Simulation")
            #proceed with high timestep
            Celestial.reset_class()
            Celestial.set_simu_SCALE(250 / Celestial.AU)  # 1AU=100px
            Celestial.set_simu_TIMESTEP(high_TIMESTEP)
            #main.main(int(duration_high[idx_test]))
            Celestial.set_simu_TIMESTEP(high_TIMESTEP*(duration_high[idx_test]-int(duration_high[idx_test])))
            main.main(1)
            for planet in Celestial.list_bodies:
                list_position_high.append(planet.x)
                list_position_high.append(planet.y)
                list_velocity_high.append(planet.x_vel)
                list_velocity_high.append(planet.y_vel)
            high_tot_simu_time = Celestial.debug  # in days
            position_result = np.sum(np.abs(np.array(sorted(list_position_low)) - np.array(sorted(list_position_high))))
            velocity_result = np.sum(np.abs(np.array(sorted(list_velocity_low) - np.array(sorted(list_velocity_high)))))

            print(position_result)
            print(velocity_result)
            print(low_tot_simu_time)
            print(high_tot_simu_time)

            """print(f"Pour un temps réel de {duration_low} :")
            print(f'\técart de position général: {position_result}')
            print(f'\técart de vitesse général: {velocity_result}')"""





if __name__ == "__main__":
    unittest.main()

    """result for 5 sec, 30 fps : 
    low_TIMESTEP = 3600*24 #1day/frame
    high_TIMESTEP = 3600*24 * 60
    733027.181479147
    0.15442205654160465
    """
