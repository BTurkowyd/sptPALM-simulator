from cell import CellShape
from camera_setup import *
import numpy as np

length = np.random.lognormal(np.log(LENGTH), np.log(LENGTH)*0.03, no_of_cells)
height = np.random.normal(HEIGHT, HEIGHT*0.1, no_of_cells)
angle = np.random.uniform(0, np.pi, no_of_cells)
origin_x, origin_y = np.random.uniform(10000, 20000, no_of_cells), np.random.uniform(10000, 20000, no_of_cells)

def generate_cells(i):
    cell = CellShape(length[i], height[i], origin=[origin_x[i], origin_y[i]], angle=angle[i], generate_movie=generate_movie, transition_matrix=trans_matrix, emission_matrix=emission_matrix)
    cell.generate_particles(K_BLEACH, K_DARK, K_REC, FRAMES, fractions, no_of_trajectories)
    return cell