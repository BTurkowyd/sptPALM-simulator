# Camera settings
PIXEL_SIZE = 129
ELECTRON_PER_AD_COUNT = 5.48
QE = 0.9
BASE_LEVEL_AD_COUNTS = 138
EM_GAIN = 300

# Movie settings
TAU = 0.0001
FRAMERATE = 0.01
FRAMES = 3000
LOC_PREC = 1

# Fluorophore settings
PSF_SIGMA = 200
PSF_SIGMA_STD = 50
PHOTONS_PER_EVENT = 200
K_BLEACH = 0.001
K_DARK = 0.00001
K_REC = 0.999

# Cell settings
LENGTH = 4000
HEIGHT = 1000
no_of_trajectories = 100
no_of_cells = 100

# Dynamics (µm²/s)
fractions = [0,4]

# Biological rates (s⁻¹)
K_SM = 100
K_MS = 100

# State transistions
trans_matrix = {
    'static': {'static': 1-(K_SM*TAU), 'mobile': K_SM*TAU},
    'mobile': {'static': K_MS*TAU, 'mobile': 1-(K_MS*TAU)}
}

emission_matrix = {
    'static': {'static': 1, 'mobile': 0},
    'mobile': {'static': 0, 'mobile': 1}
}

# Save to tiff
generate_movie = False