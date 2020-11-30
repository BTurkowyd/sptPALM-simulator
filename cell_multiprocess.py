from cell import CellShape
from camera_setup import *
import numpy as np
from multiprocessing import cpu_count, Lock, Process

CPU_COUNT = cpu_count()
global_lock = Lock()


length = np.random.lognormal(np.log(LENGTH), np.log(LENGTH)*0.03, no_of_cells)
height = np.random.normal(HEIGHT, HEIGHT*0.1, no_of_cells)
angle = np.random.uniform(0, np.pi, no_of_cells)
origin_x, origin_y = np.random.uniform(10000, 20000, no_of_cells), np.random.uniform(10000, 20000, no_of_cells)

def generate_cells(i):
    cell = CellShape(length[i], height[i], origin=[origin_x[i], origin_y[i]], angle=angle[i], generate_movie=generate_movie, transition_matrix=trans_matrix, emission_matrix=emission_matrix)
    cell.generate_particles(K_BLEACH, K_DARK, K_REC, FRAMES, fractions, no_of_trajectories)
    return cell


def to_list(cell):
    x = []
    y = []
    t = []
    ident = []
    intensity = []
    localizations = []
    for part in cell.trajectories:
        for l in part.bright_localizations:
            x.append(np.round(l.x, 1))
            y.append(np.round(l.y, 1))
            t.append(l.t)
            ident.append(part.id)
            intensity.append(np.round(l.intensity, 1))
            localizations.append(l)
    return [x, y, t, ident, intensity, localizations]

def write_to_loc_file(header, data):
    with global_lock:
        with open("localizations.txt", "w") as file:
            file.write(header + "\n")
            for r in data:
                file.write("%.1f, %.1f, %.0f, %.0f\n" % (r[0], r[1], int(r[2]), r[3]))

def write_to_groundtruth(data):
    with global_lock:
        with open("groundtruth.csv", "w") as file:
            file.write("x,y,t,id\n")
            for r in data:
                file.write("%.1f,%.1f,%.0f,%.0f\n" % (r[0], r[1], int(r[2]), r[3]))