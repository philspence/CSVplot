import os
import numpy as np
import functions as ftns
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from matplotlib.transforms import Bbox

def opentext(input, h):
    rawdata = np.genfromtxt(input, delimiter=',')
    predata = rawdata[h:]
    data = np.transpose(predata)  # transpose the data so first item in each row is now a row, etc.
    return data

def zero_correct(zero_pos, y):
    zeroed_y = []
    for series in y:
        minus_value = series[zero_pos] #finds value at the zero position, i.e. 320nm or 700nm, etc.
        zeroed_series = []
        for i in series:
            newi = float(i - minus_value)
            zeroed_series.append(newi)
        zeroed_y.append(zeroed_series)
    return np.array(zeroed_y)

def get_newy(x, y, xvalue):
    y = y[:-1]
    peak_value = np.where(x == xvalue)
    peak_value = int(peak_value[0])
    newy = []
    for i in y:
        newy.append(i[peak_value])
    return newy

def zero_to_one(y):
    # find min and max of y to normalise with
    y_max = max(y)
    y_min = min(y)
    # normalise from 0 to 1
    normy = []  # new normalised y axis
    for i in y:
        norm = (i - y_min) / (y_max - y_min)
        normy.append(float(norm))
    return normy

def find_closest(x, val, self):
    try:
        num = 0
        for i in x:
            if (i - val) < (i - x[num]):
                closest = x[num]
            num += 1
        return closest
    except Exception:
        error_report(self, "Position in X to monitor is outside of X range")
        return

def full_extent(ax, pad=0.0):
    # For text objects, we need to draw the figure first, otherwise the extents
    # are undefined.
    ax.figure.canvas.draw()
    items = ax.get_xticklabels() + ax.get_yticklabels()
    items += [ax, ax.title, ax.xaxis.label, ax.yaxis.label]
    items += [ax, ax.title]
    bbox = Bbox.union([item.get_window_extent() for item in items])

    return bbox.expanded(1.0 + pad, 1.0 + pad)

def plot_multiline(axes, x, y, xaxis, yaxis, title, hline, vline, color, xmin, xmax, ymin, ymax):
    #colours
    colrs = plt.cm.brg(np.linspace(0, 0.5, len(y)))

    try:
        axes.set_xlim(float(xmin), float(xmax))
        axes.set_ylim(float(ymin), float(ymax))
    except Exception:
        pass

    num = 0
    for i in y:  # for each row in the y array
        axes.plot(x, i, color=colrs[num], linewidth="0.7")  # plot each y series with the first color in the color array
        num += 1  # go to next color
    # set axes labels
    axes.set_xlabel(xaxis)
    axes.set_ylabel(yaxis)
    axes.set_title(title)
    #add lines
    if hline == True:
        axes.axhline(0, color='black', linewidth="1")  # add horiz line at y=0
    if vline == True:
        axes.axvline(0, color='black', linewidth="1")  # add horiz line at x=0
    return axes

def fit_curve(self, x, y, xx, func):
    popt, pcov = curve_fit(func, x, y)  # fits data using func and returns 2 values
    if func == sigmoid:
        popt, pcov = curve_fit(func, x, y, method="trf")
        self.est_k, self.est_x0 = popt  # k and x0 are return in popt
        y_fit = sigmoid(xx, self.est_k, self.est_x0)  # make y series of the fitted curve
    if func == linear:
        self.slope, self.intercept = popt
        y_fit = linear(xx, self.slope, self.intercept)
    if func == mcghee_vh:
        self.kb, self.site_size = popt
        y_fit = mcghee_vh(xx, self.kb, self.site_size)
    r_squared = get_r_squared(func, y, popt, x)
    return y_fit, r_squared, popt

def sigmoid(x, k, x0):
    return (1 / (1 + np.exp(-k * (x - x0))))

def linear(x, m, c):
    return (m * x + c)

def mcghee_vh(x, k, s):
    global c
    b = (1 + (k * c) + ((k * x) / (2 * s)))
    return (b - (b ** 2 - (2 * (k ** 2) * c * x) / s) ** 0.5) / (2 * k * c)

def plot_fittedcurve(axes, x, y, xx, y_fit, xaxis, yaxis):
    axes.plot(x, y, 's', xx, y_fit, '-')
    axes.set_xlabel(xaxis)
    axes.set_ylabel(yaxis)

def get_r_squared(f, y, popt, x):
    ss_res = np.dot((y - f(x, *popt)), (y - f(x, *popt)))
    ymean = np.mean(y)
    ss_tot = np.dot((y - ymean), (y - ymean))
    return 1 - ss_res / ss_tot

def plotsec(self):
    global c
    c = float(self.c.GetValue())
    self.axes2.clear()

    xval = ftns.find_closest(self.x, self.xvalue, self)
    self.sec_y = np.array(ftns.get_newy(self.x, self.y, xval))  # get y values from the series at a specific x

    if self.sec_type == 0:
        return

    if self.sec_type == 1: #linear binding model

        ex_coeffY = []
        for i in self.sec_y:
            ex_coeffY.append(i / c)
        first_y = ex_coeffY[0]
        lenY = len(ex_coeffY)
        num = 0
        tempY = []
        while num < lenY:
            if (ex_coeffY[num] - first_y) == 0:
                tempY.append(0)
            else:
                tempY.append(self.sec_x[num] / (ex_coeffY[num] - first_y))
            num += 1
        self.sec_y = np.array(tempY)
        xx = np.linspace(min(self.sec_x), max(self.sec_x), 100)
        y_fit, r_squared, popt = fit_curve(self, self.sec_x, self.sec_y, xx, linear)
        plot_fittedcurve(self.axes2, self.sec_x, self.sec_y, xx, y_fit, self.secplot_xlabel.GetValue(), self.secplot_ylabel.GetValue())
        self.slope, self.intercept = popt
        self.slope_box.SetValue(str(self.slope))
        self.intercept_box.SetValue(str(self.intercept))
        self.slope_intercept_box.SetValue(str(self.slope/self.intercept))
        self.r2.SetValue(str(r_squared)[:7])

    if self.sec_type == 2: #nonlinear binding model
        ex_coeffY = []
        for i in self.sec_y:
            ex_coeffY.append(i / c)
        exF = ex_coeffY[0]
        exB = ex_coeffY[-1]
        tempY = []
        for i in ex_coeffY:
            tempY.append((i - exF) / (exB - exF))
        self.sec_y = np.array(tempY)
        self.axes2.plot(self.sec_x, self.sec_y, 'o')
        xx = np.linspace(min(self.sec_x), max(self.sec_x), 100)
        y_fit, r_squared, popt = fit_curve(self, self.sec_x, self.sec_y, xx, mcghee_vh)
        plot_fittedcurve(self.axes2, self.sec_x, self.sec_y, xx, y_fit, self.secplot_xlabel.GetValue(), self.secplot_ylabel.GetValue())
        kb, sitesize = popt
        self.NLBindingConst.SetValue(str(kb))
        self.BindingSize.SetValue(str(sitesize))
        self.r2.SetValue(str(r_squared)[:7])

    if self.sec_type == 3: #melting curve
        self.sec_y = np.array(ftns.zero_to_one(self.sec_y))
        xx = np.linspace(min(self.sec_x), max(self.sec_x), 100)
        y_fit, r_squared, popt = fit_curve(self, self.sec_x, self.sec_y, xx, sigmoid)
        plot_fittedcurve(self.axes2, self.sec_x, self.sec_y, xx, y_fit, self.secplot_xlabel.GetValue(), self.secplot_ylabel.GetValue())
        est_k, est_x0 = popt
        self.meltT.SetValue(str(est_x0))
        self.r2.SetValue(str(r_squared)[:7])

# def emission_decay(x, alpha1, alpha2, tau1, tau2, tau3):
#     x * ((1 - alpha1 - alpha2) e^(-t / tau1) + alpha1 * e^(-t / tau2) + alpha2 * e^(-t / tau3))