# Camera settings
PIXEL_SIZE = 129
ELECTRON_PER_AD_COUNT = 5.48
QE = 0.9
BASE_LEVEL_AD_COUNTS = 138
EM_GAIN = 300
AD_factor = int(QE*EM_GAIN/ELECTRON_PER_AD_COUNT)
dark_pixel = BASE_LEVEL_AD_COUNTS*ELECTRON_PER_AD_COUNT

# Movie settings
TAU = 0.013
FRAMES = 500

# Fluorophore settings
PSF_SIGMA = 200
PSF_SIGMA_STD = 50
PHOTONS_PER_EVENT = 300
K_BLEACH = 0.07
K_DARK = 0.3
K_REC = 0.4

# Cell settings
LENGTH = 4000
HEIGHT = 800
no_of_trajectories = 10
no_of_cells = 10

# Dynamics ([mean, std])
fractions = [[50,25], [360,150]]

# Save to tiff
generate_movie = True