import numpy as np
from camera_setup import LOC_PREC

def direction(n):
    return np.random.uniform(0, np.pi*2, n)

def lifetime(rate, size):
    return np.random.geometric(rate, size)

def displacements(mean, sigma, lifetime=1):
    y = np.random.normal(mean, sigma, lifetime) + np.random.normal(0, LOC_PREC)
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