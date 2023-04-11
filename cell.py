import numpy as np
import matplotlib.path as mpltPath
from methods import *
from particle import Particle

class CellShape:
    ident = 1
    def __init__(self, length, height, origin = [0,0], angle = 0, generate_movie = False, transition_matrix = {}, emission_matrix = {}):
        # In general initializer generates a shape of the cell
        self.length = length
        self.height = height
        self.origin = [origin[0]+length/2, origin[1]+height/2]
        self.angle = angle
        # self.id = CellShape.ident
        self.transition_matrix = transition_matrix
        self.emission_matrix = emission_matrix
        CellShape.ident += 1
        CellShape.generate_movie = generate_movie

        self.rect_length = self.length - self.height

        self.circle_center1 = {'x': [self.height/2], 'y': [self.height/2]}
        self.circle_center2 = {'x': [self.height/2+self.rect_length], 'y': [self.height/2]}

        self.rectangle_side1 = {'x': [], 'y': []}
        self.rectangle_side2 = {'x': [], 'y': []}

        for i in np.linspace(self.height/2, self.height/2+self.rect_length, 201):
            self.rectangle_side1['x'].append(i+ np.random.normal())
            self.rectangle_side1['y'].append(0 + np.random.normal())

        for i in np.linspace(self.height/2+self.rect_length, self.height/2, 201):
            self.rectangle_side2['x'].append(i + np.random.normal())
            self.rectangle_side2['y'].append(self.height + np.random.normal())

        self.rotations1 = np.linspace(np.pi/2, 3*np.pi/2, 200)
        self.rotations2 = np.linspace(3*np.pi/2, 5*np.pi/2, 200)

        self.circle1 = {'x': [], 'y': []}
        self.circle2 = {'x': [], 'y': []}

        for r1, r2 in zip(self.rotations1, self.rotations2):
            point1 = np.array(polarToCartesian(self.height/2, r1))
            point2 = np.array(polarToCartesian(self.height/2, r2))

            self.circle1['x'].append(self.circle_center1['x'] + point1[0] + np.random.normal())
            self.circle1['y'].append(self.circle_center1['y'] + point1[1] + np.random.normal())
            self.circle2['x'].append(self.circle_center2['x'] + point2[0] + np.random.normal())
            self.circle2['y'].append(self.circle_center2['y'] + point2[1] + np.random.normal())

        self.shape = {'x': self.circle1['x'] + self.rectangle_side1['x'] + self.circle2['x'] + self.rectangle_side2['x'], 'y' : self.circle1['y'] + self.rectangle_side1['y'] + self.circle2['y'] + self.rectangle_side2['y']}

        for i in range(len(self.shape['x'])):
            # Rotate the cell
            self.shape['x'][i], self.shape['y'][i] = rotate([self.shape['x'][i], self.shape['y'][i]], self.angle)

            self.shape['x'][i] += self.origin[0]
            self.shape['y'][i] += self.origin[1] 

        # Creating a matplotlib Path object. It allows to chack later whether generated localization is within the cell.
        self.polygon = [(x, y) for x, y in zip(self.shape['x'], self.shape['y'])]
        self.path = mpltPath.Path(self.polygon)

        # print("Cell {} created".format(self.id))

    def generate_particles(self, K_BLEACH, K_DARK, K_REC, FRAMES, fractions, no_of_trajectories):
        # Generates particles inside the cell

        Particle.cell = self

        self.trajectories = [Particle(i, K_BLEACH, K_DARK, K_REC, self.length, self.height, FRAMES, fractions, self.origin, self.angle, CellShape.generate_movie, self.transition_matrix, self.emission_matrix) for i in lifetime(K_BLEACH, no_of_trajectories)]