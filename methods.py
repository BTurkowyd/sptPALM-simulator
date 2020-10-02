import numpy as np
from camera_setup import LOC_PREC, TAU

def direction(n):
    return np.random.uniform(0, np.pi*2, n)

def lifetime(rate, size):
    return np.random.geometric(rate, size)

def dToJD(D, loc_prec=LOC_PREC, dt=TAU):
    y = 2*np.sqrt(D*10**6*dt + loc_prec**2)
    return y

def displacements(diffusion, lifetime=1):
    rayleigh_sigma = dToJD(diffusion)
    y = np.random.rayleigh(rayleigh_sigma, lifetime)
    return y

def polarToCartesian(displacement, direction):
    x = displacement*np.cos(direction)
    y = displacement*np.sin(direction)
    return([x,y])

def blink(prob, trial=1):
    return np.random.binomial(trial, prob)

def recovery(prob, trial=1):
    return np.random.binomial(trial, prob)

def rotate(origin, point, angle):
    ox, oy = origin
    px, py = point

    qx = ox + np.cos(angle) * (px - ox) - np.sin(angle) * (py - oy)
    qy = oy + np.sin(angle) * (px - ox) + np.cos(angle) * (py - oy)
    return qx, qy

def gauss2d(intensity, center_x, center_y, PSF_FWHM_X=200, PSF_FWHM_Y=200, orientation = 0):
    mean = [center_x, center_y]
    covariance =[[PSF_FWHM_X**2, 0],[0, PSF_FWHM_Y**2]]
    x,y = np.random.multivariate_normal(mean, covariance, int(intensity)).T

    # for i in range(len(x)):
    #     x[i], y[i] = rotate(mean, [x[i],y[i]], orientation)
    return [x,y]