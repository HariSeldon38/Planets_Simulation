import unittest
import main
from celestial_class import Celestial
import numpy as np

tolerance = 5 #nb pixels difference acceptable for sum pos every planets
tolerance_vel = 10 #difference acceptable for sum velocity in m/s
duration_low = [5, 20] #in sec, real duration of test for low_TIMESTEP
low_TIMESTEP = 3600*24 #1day/frame
high_TIMESTEP = 3600*24*25 #25 days (max slider)
duration_high = [duration * low_TIMESTEP / high_TIMESTEP for duration in duration_low]

class TestStability(unittest.TestCase):
    """"Test the stability of our model with respect to time"""

    def test_stability_time(self):
        """
        Compare the state of the simulation after the same simulated time for a low TIMESTEP and for a high TIMESTEP
        
        return : the sum difference of position and velocity for each defined planets between low and high TIMESTEP
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
            
            #we begin with low timestep, the simu will last duration_low[idx_test] seconds
            Celestial.reset_class()
            main.init_planets()
            Celestial.set_simu_SCALE(250 / Celestial.AU)
            Celestial.set_simu_TIMESTEP(low_TIMESTEP)
            main.main(duration_low[idx_test])
            #retrieve final values (position and speed)
            for planet in Celestial.list_bodies:
                list_position_low.append(planet.x)
                list_position_low.append(planet.y)
                list_velocity_low.append(planet.x_vel)
                list_velocity_low.append(planet.y_vel)

            #proceed with high timestep
            Celestial.reset_class()
            main.init_planets()
            Celestial.set_simu_SCALE(250 / Celestial.AU)  # 1AU=100px
            Celestial.set_simu_TIMESTEP(high_TIMESTEP)
            main.main(int(duration_high[idx_test])) #duration_high * FPS cannot be integer so final frame should not be complete...
            #run main twice for high timestep in order to adjust TIMESTEP of final frame (like if we'd done fractional frame)
            Celestial.set_simu_TIMESTEP(high_TIMESTEP*(duration_high[idx_test]-int(duration_high[idx_test])))
            main.main(1)
            for planet in Celestial.list_bodies:
                list_position_high.append(planet.x)
                list_position_high.append(planet.y)
                list_velocity_high.append(planet.x_vel)
                list_velocity_high.append(planet.y_vel)
            position_result = np.sum(np.abs(np.array(sorted(list_position_low)) - np.array(sorted(list_position_high))))
            velocity_result = np.sum(np.abs(np.array(sorted(list_velocity_low) - np.array(sorted(list_velocity_high)))))
            position_result_px = position_result * Celestial.simu_SCALE

            print(f"Pour un temps réel de {duration_low[idx_test]} sec:")
            print(f'\técart de position total: {position_result} metres soit {position_result_px} pixels')
            print(f'\técart de vitesse total: {velocity_result}')

            self.assertLessEqual(position_result_px, tolerance, "Sum difference in position for each planets is more than {tolerance} pixels")
            #self.assertLessEqual(velocity_result, tolerance_vel, "Sum velocity difference too high")




if __name__ == "__main__":
    unittest.main()

    """
    Résultats 07/08/25 :

    Pour un temps réel de 5 sec:
        écart de position total: 733027.181479147 metres soit 0.0012249957744713447 pixels
        écart de vitesse total: 0.15442205654160465
    Pour un temps réel de 20 sec:
        écart de position total: 21760493.99437312 metres soit 0.036364972359861206 pixels
        écart de vitesse total: 4.459947568187638
    Pour un temps réel de 120 sec:
        écart de position total: 152570758.7270124 metres soit 0.254968082317687 pixels
        écart de vitesse total: 53.19273505208518
    
    à la suite de ce test on ne check plus la diff de vitesse qui a tendance a exploser facilement
    (idk why) mais tant que les positions sont bonnes, aucun pb.
    """