import matplotlib
matplotlib.use('TKAgg')
import matplotlib.pyplot as plt
matplotlib.rcParams.update({'font.size': 12})
import numpy as np
import seaborn as sns
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
    y = 1 / (1 + np.exp(-k * (x - x0)))
    return y

def mcghee_vh(x, k, s):
    b = (1 + (k * 5) + ((k * x) / (2 * s)))
    y = (b - (b ** 2 - (2 * (k ** 2) * 5 * x) / s)  ** 0.5) / (2 * k * 5)
    return y

def fit_curve_sig(x, y):
    popt, pcov = curve_fit(sigmoid, x, y)  # fits data using sigmoid func and returns 2 values
    est_k, est_x0 = popt  # k and x0 are return in popt
    y_fit = sigmoid(x, est_k, est_x0)  # make y series of the fitted curve
    r_squared = get_r_squared(sigmoid, y, popt, x)
    return y_fit, est_x0, r_squared

def fit_curve_mcghee(x, y):
    popt, pcov = curve_fit(mcghee_vh, x, y)  # fits data using mcghee func and returns 2 values
    est_kb, est_s = popt  # kb and s are return in popt
    y_fit = mcghee_vh(x, est_kb, est_s)  # make y series of the fitted curve
    r_squared = get_r_squared(mcghee_vh, y, popt, x)
    return y_fit, est_kb, est_s, r_squared

def get_r_squared(f, y, popt, x):
    ss_res = np.dot((y - f(x, *popt)), (y - f(x, *popt)))
    ymean = np.mean(y)
    ss_tot = np.dot((y - ymean), (y - ymean))
    return 1 - ss_res / ss_tot

def plot_fittedcurve(x, y, half, y_fit, type, s, r2, err):
    plt.scatter(x, y)  # plot the x and y data
    if type == 3: #if UV kB
        #add text containing calculated values
        x_pos = max(x) / 1.8
        plt.text(x_pos, 0.5,
                 str('K$_b$ = ' + str(round(half, 2)) + ' \u00b1 ' + str(round(err, 2)) + ' x 10$^{6}$ M$^{-1}$' + '\n s = ' + str(round(s, 2)) + ' base pairs' + '\n R$^2$ = ' + str(round(r2, 5))))
    elif type == 2: #if CD melt
        x_pos = max(x) / 1.3
        plt.text(x_pos, 0.5,
                 str('T$_m$ = ' + str(round(half, 2)) + ' \u00b1' + str(round(err, 2)) + '\n R$^2$ = ' + str(round(r2, 5))))  # add text for Tm (which is value of estimated_x0)
    plt.plot(x, y_fit, '--')  # plot fitted curve
    sns.despine()  # remove right and top axis

def zero_correct(zero_pos, y):
    zeroed_y = []
    for series in y:
        minus_value = series[zero_pos] #finds value at the zero position, i.e. 320nm or 700nm, etc.
        zeroed_series = []
        for i in series:
            newi = i - minus_value
            zeroed_series.append(newi)
        zeroed_y.append(zeroed_series)
    return zeroed_y

def cd_titr(infile, xp_name):
    data, names = opentext(infile, 2)
    # plot multiline
    plt.figure(1)
    x = data[0]
    y = data[1:]
    y = y[:-1]

    #zero correct y
    max_x = max(x)
    zero_pos = np.where(x == max_x)
    zeroed_y = zero_correct(zero_pos, y)

    plot_multiline(x, zeroed_y, 'Wavelength [nm]', 'Ellipticity [mdeg]')
    plt.axhline(0, color='black', linewidth="1")  # add horiz line at y=0
    plt.title(title)
    filename = xp_name + '-CDTitration.png'
    plt.savefig(filename, dpi=300)
    return x, zeroed_y

def cd_melt(infile, xp_name):
    data, names = opentext(infile, 2)

    x, y = cd_titr(infile, xp_name)

    # START NEXT PLOT
    peak = int(input('Which peak do you want to monitor? '))

    plt.figure(2)

    elip = np.where(x == peak)  # find which position in x = peak
    # x_elip = x[elip] #find the value of x at the position calcd from above

    plt.xlabel('Temperature [\u00b0C]')
    plt.ylabel('Normalised Ellipiticity at ' + str(peak) + ' nm [mdeg]')

    # set x values as every 5 between startT and finalT
    startT = int(input('Start temperature: '))
    finalT = int(input('Final temperature: '))
    newx = []
    num = startT
    while num <= finalT:
        newx.append(num)
        num += 5  # add 5 to startT and append it until you hit finalT, this is the x axis

    # find each y at position of max y1 and make a new array of them
    newy = []  # this will be the y axis
    for i in y:
        newy.append(i[elip])

    # normalised 0 to 1
    normy = norm_zero_to_one(newy)

    # fit curve
    y_fit, melt, r_squared = fit_curve_sig(newx, normy)
    err = Kb * (1 - r2)

    # plot data
    plot_fittedcurve(newx, normy, melt, y_fit, type, 0, r_squared, err)
    plt.title(title)
    filename = xp_name + '-CDMeltPeak.png'
    plt.savefig(filename, dpi=300)

def nl_kb(infile, xp_name):
    data, names = opentext(infile, 0)
    plt.figure(1)
    plt.xlabel('[DNA] [x $10^{-6}$ M]')
    plt.ylabel('($\epsilon_a$ - $\epsilon_f$) / ($\epsilon_b$ - $\epsilon_f$)')

    x = data[0]
    y = data[1]

    y_fit, Kb, s, r2 = fit_curve_mcghee(x, y)
    err = Kb * (1 - r2)

    print('Kb = ' + str(Kb) + '\n s = ' + str(s) + '\n r2 = ' + str(r2) + '\n Error: \u00b1' + str(err))

    plt.title(xp_name)
    plot_fittedcurve(x, y, Kb, y_fit, type, s, r2, err)
    plt.savefig(str('Kbs/' + xp_name + '-UV-Kb.png'), dpi=300)

def uv_titr(infile, xp_name):
    data, names = opentext(infile, 2)
    # plot multiline
    plt.figure(1)
    x = data[0]
    y = data[1:]
    y = y[:-1]

    # zero correct y
    max_x = max(x)
    zero_pos = np.where(x == max_x)
    zeroed_y = zero_correct(zero_pos, y)

    plot_multiline(x, zeroed_y, 'Wavelength [nm]', 'Aborbance [a.u.]')
    plt.title(title)

    x_min = float(input('X axis start: '))
    x_max = float(input('X axis end: '))
    plt.xlim(x_min, x_max)

    y_min = float(input('Y axis start: '))
    y_max = float(input('Y axis end: '))
    plt.ylim(y_min, y_max)

    filename = 'UV-titrations/' + xp_name + '-UVTitration.png'
    plt.savefig(filename, dpi=300)
    return x, zeroed_y

type = int(input("\n 1) CD titration \n 2) CD melt \n 3) Nonlinear Kb plot \n 4) UV titration \n What are you plotting? (Enter number): "))


if type == 1: #CD titration
    pre_infile = input('Name of CSV file: ')
    infile = 'CD-titrations/' + pre_infile
    xp_name = pre_infile.replace('.csv', '')
    title = xp_name
    cd_titr(infile, xp_name)

elif type == 2: #CD melt
    pre_infile = input('Name of CSV file: ')
    infile = 'CD-melts/' + pre_infile
    xp_name = pre_infile.replace('.csv', '')
    title = xp_name
    cd_melt(infile, xp_name)

elif type == 3: #Nonlinear Kb plot
    pre_infile = input('Name of CSV file: ')
    infile = 'Kbs/' + pre_infile
    xp_name = pre_infile.replace('.csv', '')
    title = xp_name
    nl_kb(infile, xp_name)
elif type == 4: #UV titration
    pre_infile = input('Name of CSV file: ')
    infile = 'UV-titrations/' + pre_infile
    xp_name = pre_infile.replace('.csv', '')
    title = xp_name
    uv_titr(infile, xp_name)
else:
    print("Incorrect input, please try again.")