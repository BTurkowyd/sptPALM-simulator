import numpy as np
import pandas as pd
from particle import Particle
from cell import CellShape
from methods import *
import matplotlib.pyplot as plt
from random import shuffle
import tifffile

K_BLEACH = 0.07
K_DARK = 0.3
K_REC = 0.4
TAU = 0.013
FRAMES = 2000
LENGTH = 4000
HEIGHT = 800
fractions = [[50,80], [200,150], [350,250]]
no_of_trajectories = [10, 0, 20]

generate_movie = False

PIXEL_SIZE = 129
ARRAY_DIMS = 400

no_of_cells = 20

length = np.random.lognormal(np.log(LENGTH), np.log(LENGTH)*0.03, no_of_cells)
height = np.random.normal(HEIGHT, HEIGHT*0.1, no_of_cells)
angle = np.random.uniform(0, np.pi, no_of_cells)
origin_x, origin_y = np.random.uniform(10**2, PIXEL_SIZE*ARRAY_DIMS/4, no_of_cells), np.random.uniform(10**4, PIXEL_SIZE*ARRAY_DIMS/4, no_of_cells)

shuffle(length)
shuffle(height)
shuffle(angle)
shuffle(origin_x)
shuffle(origin_y)

cells = []

for i in range(no_of_cells):
    cell = CellShape(length[i], height[i], origin=[origin_x[i], origin_y[i]], angle=angle[i], generate_movie=generate_movie)
    cell.generate_particles(K_BLEACH, K_DARK, K_REC, FRAMES, fractions, no_of_trajectories)

    cells.append(cell)

x = []
y = []
t = []
intensity = []
displacements = []

localizations = []

for c in cells:
    for i in c.trajs:
        for part in i:
            for l in part.bright_localizations:
                x.append(np.round(l.x, 1))
                y.append(np.round(l.y, 1))
                t.append(l.t)
                intensity.append(np.round(l.intensity, 1))
                localizations.append(l)

rapidstorm_array = np.column_stack((x,y,t,intensity))

rapidstorm_array = rapidstorm_array[rapidstorm_array[:,2].argsort()]

min_x = min_y = 0

if np.max(x) > np.max(y):
    max_x = max_y = np.max(x) + PIXEL_SIZE*10
else:
    max_x = max_y = np.max(y) + PIXEL_SIZE*10

trajs = []

header = '# <localizations insequence="true" repetitions="variable"><field identifier="Position-0-0" syntax="floating point with . for decimals and optional scientific e-notation" semantic="position in sample space in X" unit="nanometer" min="{}" max="{} nm" /><field identifier="Position-1-0" syntax="floating point with . for decimals and optional scientific e-notation" semantic="position in sample space in Y" unit="nanometer" min="{} m" max="{} nm" /><field identifier="ImageNumber-0-0" syntax="integer" semantic="frame number" unit="frame" min="0 fr" /><field identifier="Amplitude-0-0" syntax="floating point with . for decimals and optional scientific e-notation" semantic="emission strength" unit="A/D count" /></localizations>'.format(min_x, min_y, max_x, max_y)


with open("localizations.txt", "w") as file:
    file.write(header + "\n")
    for r in rapidstorm_array:
        file.write("{} {} {} {}\n".format(r[0], r[1], int(r[2]), r[3]))


if generate_movie:
    NO_OF_PIXELS = int(np.ceil(max_x/PIXEL_SIZE))
    movie_array = np.zeros((np.max(t)+1, NO_OF_PIXELS, NO_OF_PIXELS), dtype=np.int16)
    noise = np.random.randint(400, 600, (np.max(t)+1, NO_OF_PIXELS, NO_OF_PIXELS), dtype=np.int16)

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

        hist = np.histogram2d(frame_x, frame_y, bins=NO_OF_PIXELS, range=[[0,NO_OF_PIXELS*PIXEL_SIZE],[0,NO_OF_PIXELS*PIXEL_SIZE]])

        movie_array[i] = hist[0] + noise[i]

    tifffile.imsave('test.tiff', movie_array)

df = pd.DataFrame(columns=['x','y','t','id'])

for c in cells:
    for t in c.trajs:
        for p in t:
            p.groundtruth_trajectory()
            df = df.append(p.groundtruth)

df.to_csv("groundtruth.csv", index=False)