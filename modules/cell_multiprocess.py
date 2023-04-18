from modules.cell import CellShape
from input_parameters import *
import numpy as np
from multiprocessing import cpu_count, Lock

CPU_COUNT = cpu_count()
global_lock = Lock()

length = np.random.lognormal(np.log(LENGTH), np.log(LENGTH)*0.03, no_of_cells)
height = np.random.normal(HEIGHT, HEIGHT*0.1, no_of_cells)
angle = np.random.uniform(0, np.pi, no_of_cells)
origin_x, origin_y = np.random.uniform(10000, 50000, no_of_cells), np.random.uniform(10000, 50000, no_of_cells)

def generate_cells(i):
    cell = CellShape(length[i], height[i], origin=[origin_x[i], origin_y[i]], angle=angle[i], generate_movie=generate_movie, transition_matrix=trans_matrix, emission_matrix=emission_matrix)
    cell.generate_particles(K_BLEACH, K_DARK, K_REC, FRAMES, fractions, no_of_trajectories)
    return cell

def write_to_loc_file(header, data):
    with global_lock:
        with open("localizations_K_SM_{}__K_MS_{}.txt".format(str(K_SM), str(K_MS)), "w") as file:
            file.write(header + "\n")
            for r in data:
                file.write("%.1f, %.1f, %.0f, %.0f\n" % (r[0], r[1], int(r[2]), r[3]))

def write_to_groundtruth(data):
    with global_lock:
        with open("groundtruth_K_SM_{}__K_MS_{}.csv".format(str(K_SM), str(K_MS)), "w") as file:
            file.write("x,y,t,id\n")
            for r in data:
                file.write("%.1f,%.1f,%.0f,%.0f\n" % (r[0], r[1], int(r[2]), r[3]))