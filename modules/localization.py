from input_parameters import FRAMERATE, TAU
import numpy as np

class Localization:
    def __init__(self, x, y, t, i, state, displacement=0, orientation=0, PSF_FWHM=200, generate_movie=False):
        self.x = x
        self.y = y
        self.t = t
        self.intensity = i
        self.state = state
        self.displacement = displacement
        self.orientation = orientation
        self.frame = self.t // (FRAMERATE/TAU)

        # [self.displacement_x, self.displacement_y] = polarToCartesian(self.displacement, self.orientation)

        self.PSF_FWHM_X = int(PSF_FWHM)
        self.PSF_FWHM_Y = int(PSF_FWHM)

        if generate_movie:
            self.PSF = self.gauss2d(self.intensity, self.x, self.y, self.PSF_FWHM_X, self.PSF_FWHM_Y, self.orientation)

    def gauss2d(self, intensity, center_x, center_y, PSF_FWHM_X=200, PSF_FWHM_Y=200, orientation = 0):
        mean = [center_x, center_y]
        covariance =[[PSF_FWHM_X**2, 0],[0, PSF_FWHM_Y**2]]
        x,y = np.random.multivariate_normal(mean, covariance, int(intensity)).T

        # for i in range(len(x)):
        #     x[i], y[i] = rotate(mean, [x[i],y[i]], orientation)
        return [x,y]