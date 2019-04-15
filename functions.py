import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

def opentext(input, d):
    h = d - 1
    rawdata = np.genfromtxt(input, delimiter=',')
    prenames = rawdata[h]
    names = prenames[d:]
    predata = rawdata[d:]
    data = np.transpose(predata)  # transpose the data so first item in each row is now a row, etc.
    return data, names

def plot_multiline(x, y, xaxis, yaxis):
    numy = len(y)
    colrs = plt.cm.brg(np.linspace(0, 0.5, numy))
    num = 0
    for i in y:  # for each row in the y array
        plt.plot(x, i, color=colrs[num])  # plot each y series with the first color in the color array
        num += 1  # go to next color
    # set axes labels
    plt.xlabel(xaxis)
    plt.ylabel(yaxis)
    sns.despine()  # remove right and top axisß

def norm_zero_to_one(y):
    # find min and max of y to normalise with
    y_max = max(y)
    y_min = min(y)
    # normalise from 0 to 1
    normy = []  # new normalised y axis
    for i in y:
        norm = (i - y_min) / (y_max - y_min)
        normy.append(float(norm))
    return normy

def sigmoid(x, k, x0):
    y = np.exp(-k * (x - x0)) / (1 + np.exp(-k * (x - x0)))
    return y

def fit_curve(x, y):
    popt, pcov = curve_fit(sigmoid, x, y)  # fits data using sigmoid func and returns 2 values
    estimated_k, estimated_x0 = popt  # k and x0 are return in popt
    y_fit = sigmoid(x, estimated_k, estimated_x0)  # make y series of the fitted curve
    return y_fit, estimated_x0

def plot_fittedcurve(x, y, half, y_fit):
    plt.scatter(x, y)  # plot the x and y data
    x_pos = max(x) / 1.3
    plt.text(x_pos, 0.5, '$y_{0.5}$ = ' + str(round(half, 2)))  # add text for Tm (which is value of estimated_x0)
    plt.plot(x, y_fit, '--')  # plot fitted curve
    sns.despine()  # remove right and top axis

