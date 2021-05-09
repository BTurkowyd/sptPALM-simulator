from concurrent.futures import process
import numpy as np
from cell_multiprocess import *
from methods import *
from camera_setup import *
import tifffile
import concurrent.futures
from multiprocessing import cpu_count, Lock, Process
import itertools

CPU_COUNT = cpu_count()
global_lock = Lock()


if __name__ == '__main__':
    cells = []

    with concurrent.futures.ProcessPoolExecutor() as executor:
        results = [executor.submit(generate_cells, i) for i in range(no_of_cells)]

        count = 1
        for f in concurrent.futures.as_completed(results):
            cells.append(f.result())
            print("Cell {} created".format(count))
            count += 1

    x = []
    y = []
    t = []
    ident = []
    intensity = []
    displacements = []

    localizations = []

    trajectory_id = 1
    for i, c in enumerate(cells):
        for part in c.trajectories:
            for l in part.bright_localizations:
                if not (l.t % np.round(FRAMERATE/TAU)):
                    x.append(np.round(l.x, 1))
                    y.append(np.round(l.y, 1))
                    t.append(l.t)
                    ident.append(trajectory_id)
                    intensity.append(np.round(l.intensity, 1))
                    localizations.append(l)
            trajectory_id += 1
        print("Cell {} processed".format(i+1))

    min_x = np.min(x)
    min_y = np.min(y)

    x = x - min_x + PIXEL_SIZE*10
    y = y - min_y + PIXEL_SIZE*10

    # if generate_movie:
    #     for l in localizations:
    #         l.PSF[0] = l.PSF[0] - min_x + PIXEL_SIZE*10
    #         l.PSF[1] = l.PSF[1] - min_y + PIXEL_SIZE*10


    max_x = np.max(x)
    max_y = np.max(y)

    rapidstorm_array = np.column_stack((x,y,t,intensity))
    rapidstorm_array = rapidstorm_array[rapidstorm_array[:,2].argsort()]

    groundtruth_array = np.column_stack((x,y,t,ident))
    groundtruth_array = groundtruth_array[groundtruth_array[:,2].argsort()]

    header = '# <localizations insequence="true" repetitions="variable"><field identifier="Position-0-0" syntax="floating point with . for decimals and optional scientific e-notation" semantic="position in sample space in X" unit="nanometer" min="{}" max="{} nm" /><field identifier="Position-1-0" syntax="floating point with . for decimals and optional scientific e-notation" semantic="position in sample space in Y" unit="nanometer" min="{} m" max="{} nm" /><field identifier="ImageNumber-0-0" syntax="integer" semantic="frame number" unit="frame" min="0 fr" /><field identifier="Amplitude-0-0" syntax="floating point with . for decimals and optional scientific e-notation" semantic="emission strength" unit="A/D count" /></localizations>'.format(min_x, min_y, max_x, max_y)

    processes_loc_file = []
    for i in range(CPU_COUNT):
        p = Process(target=write_to_loc_file, args=[header, rapidstorm_array])
        processes_loc_file.append(p)
        p.start()
    [process.join() for process in processes_loc_file]

    processes_groundtruth = []
    for i in range(CPU_COUNT):
        p = Process(target=write_to_groundtruth, args=[groundtruth_array])
        processes_groundtruth.append(p)
        p.start()
    [process.join() for process in processes_groundtruth]

    if generate_movie:
        print("line 88")
        NO_OF_PIXELS_Y = int(np.ceil(max_x/PIXEL_SIZE)) + 20
        NO_OF_PIXELS_X = int(np.ceil(max_y/PIXEL_SIZE)) + 20
        # movie_array = np.zeros((np.max(t)+1, NO_OF_PIXELS_X, NO_OF_PIXELS_Y), dtype=np.int16)
        print("line 92")
        no_frames = FRAMES+1
        movie_array = np.zeros((int(no_frames), NO_OF_PIXELS_X, NO_OF_PIXELS_Y), dtype=np.int16)
        noise = np.random.poisson(lam=BASE_LEVEL_AD_COUNTS*ELECTRON_PER_AD_COUNT, size=(int(no_frames), NO_OF_PIXELS_X, NO_OF_PIXELS_Y))

        print("line 97")
        for i in range(int(no_frames)):
        # if not (i % np.round(FRAMERATE/TAU)):
            if not i%20:
                print("Frame " + str(i))

            frame_x = []
            frame_y = []

            for l in localizations:
                if l.t/int(FRAMERATE/TAU) == i:
                    l.PSF[0] = l.PSF[0] - min_x + PIXEL_SIZE*10
                    l.PSF[1] = l.PSF[1] - min_y + PIXEL_SIZE*10
                    frame_x.append(l.PSF[0])
                    frame_y.append(l.PSF[1])

            frame_x = [item for sublist in frame_x for item in sublist]
            frame_y = [item for sublist in frame_y for item in sublist]

            hist = np.histogram2d(frame_y, frame_x, bins=[NO_OF_PIXELS_X, NO_OF_PIXELS_Y], range=[[0,NO_OF_PIXELS_X*PIXEL_SIZE],[0,NO_OF_PIXELS_Y*PIXEL_SIZE]])

            movie_array[i] = hist[0]*(QE*EM_GAIN/ELECTRON_PER_AD_COUNT) + noise[i]

        # movie_array = movie_array[np.arange(0, np.max(t)+1, int(FRAMERATE/TAU))]
        tifffile.imsave('test.tiff', movie_array)

