import numpy as np
import pandas as pd
from particle import Particle
from cell import CellShape
from methods import *
from camera_setup import *
import matplotlib.pyplot as plt
from random import shuffle
import tifffile


trans_matrix = {
    'static': {'static': 1.0, 'mobile': 0.0},
    'mobile': {'static': 1.0, 'mobile': 0.0}
}

emission_matrix = {
    'static': {'static': 1, 'mobile': 0},
    'mobile': {'static': 0, 'mobile': 1}
}

length = np.random.lognormal(np.log(LENGTH), np.log(LENGTH)*0.03, no_of_cells)
height = np.random.normal(HEIGHT, HEIGHT*0.1, no_of_cells)
angle = np.random.uniform(0, np.pi, no_of_cells)
origin_x, origin_y = np.random.uniform(0, 10000, no_of_cells), np.random.uniform(0, 10000, no_of_cells)

shuffle(length)
shuffle(height)
shuffle(angle)
shuffle(origin_x)
shuffle(origin_y)

cells = []

for i in range(no_of_cells):
    cell = CellShape(length[i], height[i], origin=[origin_x[i], origin_y[i]], angle=angle[i], generate_movie=generate_movie, transition_matrix=trans_matrix, emission_matrix=emission_matrix)
    cell.generate_particles(K_BLEACH, K_DARK, K_REC, FRAMES, fractions, no_of_trajectories)

    cells.append(cell)

x = []
y = []
t = []
intensity = []
displacements = []

localizations = []

for c in cells:
    for part in c.trajectories:
            for l in part.bright_localizations:
                x.append(np.round(l.x, 1))
                y.append(np.round(l.y, 1))
                t.append(l.t)
                intensity.append(np.round(l.intensity, 1))
                localizations.append(l)


min_x = np.min(x)
min_y = np.min(y)

x = x - min_x + PIXEL_SIZE*10
y = y - min_y + PIXEL_SIZE*10

for l in localizations:
    l.PSF[0] = l.PSF[0] - min_x + PIXEL_SIZE*10
    l.PSF[1] = l.PSF[1] - min_y + PIXEL_SIZE*10


max_x = np.max(x)
max_y = np.max(y)

# if max_x > max_y:
#     max_y = max_x
# else:
#     max_x = max_y

rapidstorm_array = np.column_stack((x,y,t,intensity))

rapidstorm_array = rapidstorm_array[rapidstorm_array[:,2].argsort()]



trajs = []

header = '# <localizations insequence="true" repetitions="variable"><field identifier="Position-0-0" syntax="floating point with . for decimals and optional scientific e-notation" semantic="position in sample space in X" unit="nanometer" min="{}" max="{} nm" /><field identifier="Position-1-0" syntax="floating point with . for decimals and optional scientific e-notation" semantic="position in sample space in Y" unit="nanometer" min="{} m" max="{} nm" /><field identifier="ImageNumber-0-0" syntax="integer" semantic="frame number" unit="frame" min="0 fr" /><field identifier="Amplitude-0-0" syntax="floating point with . for decimals and optional scientific e-notation" semantic="emission strength" unit="A/D count" /></localizations>'.format(min_x, min_y, max_x, max_y)


with open("localizations.txt", "w") as file:
    file.write(header + "\n")
    for r in rapidstorm_array:
        file.write("{} {} {} {}\n".format(r[0], r[1], int(r[2]), r[3]))


if generate_movie:
    NO_OF_PIXELS_X = int(np.ceil(max_x/PIXEL_SIZE)) + 20
    NO_OF_PIXELS_Y = int(np.ceil(max_y/PIXEL_SIZE)) + 20
    movie_array = np.zeros((np.max(t)+1, NO_OF_PIXELS_X, NO_OF_PIXELS_Y), dtype=np.int16)
    noise = np.random.poisson(lam=dark_pixel, size=(np.max(t)+1, NO_OF_PIXELS_X, NO_OF_PIXELS_Y))

    for i in range(np.max(t)+1):
        if not i%20:
            print("Frame " + str(i))

        frame_x = []
        frame_y = []

        for l in localizations:
            if l.t == i:
                frame_x.append(l.PSF[0])
                frame_y.append(l.PSF[1])

        frame_x = [item for sublist in frame_x for item in sublist]
        frame_y = [item for sublist in frame_y for item in sublist]

        hist = np.histogram2d(frame_y, frame_x, bins=[NO_OF_PIXELS_X, NO_OF_PIXELS_Y], range=[[0,NO_OF_PIXELS_X*PIXEL_SIZE],[0,NO_OF_PIXELS_Y*PIXEL_SIZE]])

        movie_array[i] = hist[0] + noise[i]

    tifffile.imsave('test.tiff', movie_array)

# df = pd.DataFrame(columns=['x','y','t','id'])

# for c in cells:
#     for t in c.trajectories:
#         for p in t:
#             p.groundtruth_trajectory()
#             df = df.append(p.groundtruth)

# df.to_csv("groundtruth.csv", index=False)