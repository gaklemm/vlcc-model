from scipy.optimize import curve_fit
from scipy.interpolate import interp1d
import numpy as np


class Curve(object):
    """
    Fuel consumption curve class containing various fitting methods.
    """

    def __init__(self, feature, target):
        """
        :param feature: input data
        :param target: target data
        """
        self.x = feature
        self.y = target

    def interpolate(self, x_new):
        """
        :param x_new: new observation (speed)
        :return: predicted target fuel consumption
        """
        # quadratic interpolation bounded by original data (ground truth)
        y_est = interp1d(self.x, self.y, kind='quadratic')
        return y_est(x_new)

    def quadratic_fit(self, x_new):
        """
        :param x_new: new observation (speed)
        :return: predicted target fuel consumption
        """
        # fit second-degree polynomial function
        y_est = np.poly1d(np.polyfit(self.x, self.y, 2))
        return y_est(x_new)

    def exponential_fit(self, x_new):
        """
        :param x_new: new observation (speed)
        :return: predicted target fuel consumption
        """
        # define exponential function
        def func(x, a, b, c):
            return a * np.exp(-b * x) + c
        # fit exponential function
        popt, _ = curve_fit(func, self.x, self.y, p0=(1, 1e-6, 1))
        return func(x_new, *popt)
