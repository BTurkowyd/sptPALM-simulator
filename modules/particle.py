from input_parameters import *
from modules.localization import Localization
from modules.markovchain import MarkovChain
import numpy as np
import pandas as pd

class Particle:

    ident = 0
    cell = None

    def __init__(self, lifetime, K_BLEACH, K_DARK, K_REC, LENGTH, HEIGHT, FRAMES, fraction, cell_origin, cell_angle, generate_movie=False, transition_matrix = {}, emission_matrix = {}):
        self.lifetime = lifetime
        self.K_BLEACH = K_BLEACH
        self.K_DARK = K_DARK
        self.K_REC = K_REC
        self.cell_origin = cell_origin
        self.transition_matrix = transition_matrix
        self.emission_matrix = emission_matrix

        self.markov_chain = MarkovChain(self.transition_matrix, self.emission_matrix)

        if np.random.rand() < 0.5:
            self.initial_mobility = 'mobile'
        else:
            self.initial_mobility = 'static'

        self.current_mobility = self.initial_mobility

        self.init_bool = False

        # Generates the initial position of the particle within the cell
        while self.init_bool == False:
            self.init_x = np.random.uniform(0, LENGTH)
            self.init_y = np.random.uniform(0, HEIGHT)
            self.init_t = np.random.randint(0, int(FRAMES*(FRAMERATE/TAU)))

            self.init_x, self.init_y = self.rotate([self.init_x, self.init_y], cell_angle)

            self.init_x += cell_origin[0]
            self.init_y += cell_origin[1]


            self.init_bool = Particle.cell.path.contains_point((self.init_x, self.init_y))

        self.localizations = [Localization(self.init_x + self.cell_origin[0], self.init_y + self.cell_origin[1], self.init_t, self.drawPhotonsEmitted(PHOTONS_ABSORBED, QY), 1, 0, generate_movie=generate_movie)]

        self.bright_localizations = [Localization(self.init_x + self.cell_origin[0], self.init_y + self.cell_origin[1], self.init_t, self.drawPhotonsEmitted(PHOTONS_ABSORBED, QY), 1, 0, generate_movie=generate_movie)]

        self.dark_localizations = []
        self.id = Particle.ident
        Particle.ident += 1

        # Generates trajectories, including blinking, recovery and bleaching
        while self.lifetime > 0:
            # last_x = self.localizations[-1].x
            # last_y = self.localizations[-1].y
            # last_t = self.localizations[-1].t
            # last_state = self.localizations[-1].state
            try:
                last_x = new_loc.x
                last_t = new_loc.t
                last_y = new_loc.y
                last_state = new_loc.state
            except UnboundLocalError:
                last_x = self.localizations[-1].x
                last_y = self.localizations[-1].y
                last_t = self.localizations[-1].t
                last_state = self.localizations[-1].state

            if self.current_mobility == 'static':
                r = self.displacements(fraction[0])
            else:
                r = self.displacements(fraction[1])

            self.inside = False

            trial = 0

        # Check whether generates localization is within the cell
            while self.inside == False and trial < 300:
                directions = self.direction(1)
                jump = self.polarToCartesian(r, directions)

                # Apply loc precision error
                directions_LP = self.direction(1)
                jump_LP = self.polarToCartesian(np.random.normal(0, LOC_PREC), directions_LP)
                jump[0][0] += jump_LP[0][0]
                jump[1][0] += jump_LP[1][0]

                self.inside = Particle.cell.path.contains_point((last_x+jump[0][0] - self.cell_origin[0], last_y+jump[1][0] - self.cell_origin[1]))

                trial += 1

            if trial == 300:
                print('The trajectory was killed!')

            # If in the previous frame localization was in the "on" state...
            if last_state == 1:

                # Checks whether localization will go to the "off" state...
                blinking = self.blink(K_DARK)
                
                # If not...
                if blinking == 0:
                    new_loc = Localization(last_x+jump[0][0], last_y+jump[1][0], last_t+1, self.drawPhotonsEmitted(PHOTONS_ABSORBED, QY), 1, r, directions, generate_movie=generate_movie, PSF_FWHM=np.random.normal(PSF_SIGMA, PSF_SIGMA_STD, 1)[0])

                    if not (new_loc.t % np.round(FRAMERATE/TAU)):
                        self.localizations.append(new_loc)
                    self.bright_localizations.append(new_loc)

                    self.lifetime -= 1

                # If yes...
                else:
                    new_loc = Localization(last_x+jump[0][0], last_y+jump[1][0], last_t+1, 0, 0)

                    if not (new_loc.t % np.round(FRAMERATE/TAU)):
                        self.localizations.append(new_loc)
                    self.dark_localizations.append(new_loc)

                self.current_mobility = self.markov_chain.next_state(self.current_mobility)[0]
            
            # If in the previous frame localization was in the "of" state...
            else:

                # Checks whether localization will go to the "on" state...
                recov = self.recovery(K_REC)

                # If yes...
                if recov == 1:
                    new_loc = Localization(last_x+jump[0][0], last_y+jump[1][0], last_t+1, self.drawPhotonsEmitted(PHOTONS_ABSORBED, QY), 1, r, directions, generate_movie=generate_movie, PSF_FWHM=np.random.normal(PSF_SIGMA, PSF_SIGMA_STD, 1)[0])

                    if not (new_loc.t % np.round(FRAMERATE/TAU)):
                        self.localizations.append(new_loc)
                    self.bright_localizations.append(new_loc)

                    self.lifetime -= 1
                
                # If not...
                else:
                    new_loc = Localization(last_x+jump[0][0], last_y+jump[1][0], last_t+1, 0, 0)

                    if not (new_loc.t % np.round(FRAMERATE/TAU)):
                        self.localizations.append(new_loc)
                    self.dark_localizations.append(new_loc)

                self.current_mobility = self.markov_chain.next_state(self.current_mobility)[0]

        self.groundtruth_trajectory()

    def direction(self, n):
        return np.random.uniform(0, np.pi*2, n)
    
    def dToJD(self, D, loc_prec=LOC_PREC, dt=TAU):
        y = 2*np.sqrt(D*10**6*dt + loc_prec**2)
        return y

    def displacements(self, diffusion, lifetime=1):
        rayleigh_sigma = self.dToJD(diffusion)
        y = np.random.rayleigh(rayleigh_sigma, lifetime)
        return y
    
    def polarToCartesian(self, displacement, direction):
        x = displacement*np.cos(direction)
        y = displacement*np.sin(direction)
        return([x,y])

    def blink(self, prob, trial=1):
        return np.random.binomial(trial, prob)

    def recovery(self, prob, trial=1):
        return np.random.binomial(trial, prob)
    
    def rotate(self, point, angle):
        px, py = point
        qx = np.cos(angle) * px - np.sin(angle) * py
        qy = np.sin(angle) * px + np.cos(angle) * py
        return qx, qy

    def groundtruth_trajectory(self):
        # Generates a dictionary with groundtruth trajectories. Useful to compare with the tracking software result
        self.groundtruth = pd.DataFrame(columns=['x','y','t','frame','id'])

        for b in self.bright_localizations:
            d = {'x': [np.round(b.x,1)], 'y': [np.round(b.y,1)], 't': [b.t], 'frame': [b.frame], 'id': [self.id]}
            df = pd.DataFrame(data=d)
            self.groundtruth = self.groundtruth.append(df)

    def drawPhotonsAbsorbed(self, mean, std = 400):
        y = np.random.normal(mean, std, 1)
        if y > 0:
            return np.int(y)
        else: return 1

    def drawPhotonsEmitted(self, mean, QY):
        photons_absorbed = self.drawPhotonsAbsorbed(mean)
        y = np.random.binomial(photons_absorbed, QY)
        return np.int(y) 
