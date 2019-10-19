from methods import *
from localization import Localization
import numpy as np
import pandas as pd

class Particle:

    ident = 0
    cell = None

    def __init__(self, lifetime, K_BLEACH, K_DARK, K_REC, LENGTH, HEIGHT, FRAMES, fraction, cell_origin, cell_angle, generate_movie=False):
        self.lifetime = lifetime
        self.K_BLEACH = K_BLEACH
        self.K_DARK = K_DARK
        self.K_REC = K_REC
        self.cell_origin = cell_origin

        self.init_bool = False

        # Generates the initial position of the particle within the cell
        while self.init_bool == False:
            self.init_x = np.random.uniform(0, LENGTH)
            self.init_y = np.random.uniform(0, HEIGHT)
            self.init_t = np.random.randint(0, FRAMES)

            self.init_x, self.init_y = rotate(cell_origin, [self.init_x, self.init_y], cell_angle)

            self.init_bool = Particle.cell.path.contains_point((self.init_x, self.init_y))

        self.localizations = [Localization(self.init_x + self.cell_origin[0], self.init_y + self.cell_origin[1], self.init_t, np.random.lognormal(np.log(3000), np.log(3000)*0.2, 1), 1, 0, generate_movie=generate_movie)]
        self.bright_localizations = [Localization(self.init_x + self.cell_origin[0], self.init_y + self.cell_origin[1], self.init_t, np.random.lognormal(np.log(500), np.log(500)*0.2, 1), 1, 0, generate_movie=generate_movie)]
        self.dark_localizations = []
        self.id = Particle.ident
        Particle.ident += 1

        # Generates trajectories, including blinking, recovery and bleaching
        while self.lifetime > 0:
            last_x = self.localizations[-1].x
            last_y = self.localizations[-1].y
            last_t = self.localizations[-1].t
            last_state = self.localizations[-1].state
            r = displacements(fraction[0], fraction[1])

            self.inside = False

        # Check whether generates localization is within the cell
            while self.inside == False:
                directions = direction(1)
                jump = polarToCartesian(r, directions)

                self.inside = Particle.cell.path.contains_point((last_x+jump[0][0] - self.cell_origin[0], last_y+jump[1][0] - self.cell_origin[1]))

            # If in the previous frame localization was in the "on" state...
            if last_state == 1:

                # Checks whether localization will go to the "off" state...
                blinking = blink(K_DARK)
                
                # If not...
                if blinking == 0:
                    new_loc = Localization(last_x+jump[0][0], last_y+jump[1][0], last_t+1, np.random.lognormal(np.log(3000), np.log(3000)*0.2, 1), 1, r, directions, generate_movie=generate_movie)

                    self.localizations.append(new_loc)
                    self.bright_localizations.append(new_loc)

                    self.lifetime -= 1

                # If yes...
                else:
                    new_loc = Localization(last_x+jump[0][0], last_y+jump[1][0], last_t+1, 0, 0)

                    self.localizations.append(new_loc)
                    self.dark_localizations.append(new_loc)
            
            # If in the previous frame localization was in the "of" state...
            else:

                # Checks whether localization will go to the "on" state...
                recov = recovery(K_REC)

                # If yes...
                if recov == 1:
                    new_loc = Localization(last_x+jump[0][0], last_y+jump[1][0], last_t+1, np.random.lognormal(np.log(3000), np.log(3000)*0.2, 1), 1, r, directions, generate_movie=generate_movie)

                    self.localizations.append(new_loc)
                    self.bright_localizations.append(new_loc)

                    self.lifetime -= 1
                
                # If not...
                else:
                    new_loc = Localization(last_x+jump[0][0], last_y+jump[1][0], last_t+1, 0, 0)

                    self.localizations.append(new_loc)
                    self.dark_localizations.append(new_loc) 

    def groundtruth_trajectory(self):
        # Generates a dictionary with groundtruth trajectories. Useful to compare with the tracking software result
        self.groundtruth = pd.DataFrame(columns=['x','y','t','id'])

        for b in self.bright_localizations:
            d = {'x': [np.round(b.x,1)], 'y': [np.round(b.y,1)], 't': [b.t], 'id': [self.id]}
            df = pd.DataFrame(data=d)
            self.groundtruth = self.groundtruth.append(df)


