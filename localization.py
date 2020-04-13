from methods import *

class Localization:
    def __init__(self, x, y, t, i, state, displacement=0, orientation=0, PSF_FWHM=200, generate_movie=False):
        self.x = x
        self.y = y
        self.t = t
        self.intensity = i
        self.state = state
        self.displacement = displacement
        self.orientation = orientation

        # [self.displacement_x, self.displacement_y] = polarToCartesian(self.displacement, self.orientation)

        self.PSF_FWHM_X = int(PSF_FWHM)
        self.PSF_FWHM_Y = int(PSF_FWHM)

        if generate_movie:
            self.PSF = gauss2d(self.intensity, self.x, self.y, self.PSF_FWHM_X, self.PSF_FWHM_Y, self.orientation)