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
    y = np.exp(-k * (x - x0)) / (1 + np.exp(-k * (x - x0)))
    return y

def mcghee_vh(x, k, s):
    b = (1 + (k * 5) + ((k * x) / (2 * s)))
    y = (b - (b ** 2 - (2 * k ** 2 * 5 * x) / s) ** 0.5) / (2 * k * 5)
    return y

def fit_curve_sig(x, y):
    popt, pcov = curve_fit(sigmoid, x, y)  # fits data using sigmoid func and returns 2 values
    estimated_k, estimated_x0 = popt  # k and x0 are return in popt
    y_fit = sigmoid(x, estimated_k, estimated_x0)  # make y series of the fitted curve
    r_squared = get_r_squared(sigmoid, y, popt)
    return y_fit, estimated_x0, estimated_k, r_squared

def fit_curve_mcghee(x, y):
    popt, pcov = curve_fit(mcghee_vh, x, y)  # fits data using mcghee func and returns 2 values
    estimated_kb, estimated_s = popt  # kb and s are return in popt
    y_fit = mcghee_vh(x, estimated_kb, estimated_s)  # make y series of the fitted curve
    r_squared = get_r_squared(mcghee_vh, y, popt)
    return y_fit, estimated_kb, estimated_s, r_squared

def get_r_squared(f, y, popt):
    ss_res = np.dot((y - f(x, *popt)), (y - f(x, *popt)))
    ymean = np.mean(y)
    ss_tot = np.dot((y - ymean), (y - ymean))
    return 1 - ss_res / ss_tot

def plot_fittedcurve(x, y, half, y_fit, type, s, r2):
    plt.scatter(x, y)  # plot the x and y data
    x_pos = max(x) / 1.3
    if type == 4:
        plt.text(x_pos, 0.5,
                 str('K$_b$ = ' + str(round(half, 2)) + '\n s = ' + str(round(s, 2)) + '\n R$^2$ = ' + str(round(r2, 5))))  # add text for Tm (which is value of estimated_x0)
    elif type == 2:
        plt.text(x_pos, 0.5,
                 str('K$_D$ = ' + str(round(half, 2))))  # add text for Tm (which is value of estimated_x0)
    x_max = max(x)
    x_lim = x_max + (x_max * 0.1)
    plt.xlim(0, x_lim)
    plt.plot(x, y_fit, '--')  # plot fitted curve
    sns.despine()  # remove right and top axis


type = int(input("\n 1) CD titration \n 2) CD melt \n 3) Emission titration \n 4) Nonlinear Kb plot \n What are you plotting? (Enter number): "))

if type == 1: #CD titration
    infile = input('Name of CSV file: ')
    title = input('Graph title: ')
    data, names = opentext(infile, 2)
    xp_name = infile.replace('.csv', '')

    # plot multiline
    plt.figure(1)
    x = data[0]
    y = data[1:]
    plot_multiline(x, y, 'Wavelength [nm]', 'Ellipticity [mdeg]')
    plt.axhline(0, color='black', linewidth="1")  # add horiz line at y=0
    plt.title(title)
    filename = xp_name + '-CDSpectraFull.png'
    plt.savefig(filename, dpi=300)

elif type == 2: #CD melt
    # open csv file
    infile = input('Name of CSV file: ')
    title = input('Graph title: ')
    data, names = opentext(infile, 2)
    xp_name = infile.replace('.csv', '')


    # TODO extract melt plot from csv of melt (machine saves this)
    # START NEXT PLOT
    plt.figure(2)

    elip = np.where(x == peak)  # find which position in x = peak
    # x_elip = x[elip] #find the value of x at the position calcd from above

    plt.xlabel('Temperature [\u00b0C]')
    plt.ylabel('Normalised Ellipiticity at ' + str(peak) + ' nm [mdeg]')

    # set x values as every 5 between startT and finalT
    newx = []
    num = startT
    while num <= finalT:
        newx.append(num)
        num += 5  # add 5 to startT and append it until you hit finalT, this is the x axis

    # cut off last point in y, it errors for some reason, must be artifact of csv file
    y = y[:-1]

    # find each y at position of max y1 and make a new array of them
    newy = []  # this will be the y axis
    for i in y:
        newy.append(i[elip])

    # normalised 0 to 1
    normy = norm_zero_to_one(newy)

    # fit curve
    y_fit, melt = fit_curve_sig(newx, normy)

    # plot data
    plot_fittedcurve(newx, normy, melt, y_fit, type)
    plt.title(title)
    filename = xp_name + '-CDMeltPeak.png'
    plt.savefig(filename, dpi=300)
elif type == 3: #Emission titration
    # open csv file
    infile = input('Name of CSV file: ')
    data, names = opentext(infile, 1)

    # plot multiline
    plt.figure(1)
    x = data[0]
    y = data[1:]
    plot_multiline(x, y, 'Wavelength [nm]', 'Emission Intensity [a.u.]')
    plt.savefig('EmissionTitration.png', dpi=300)

    # NORMALISED DATA FIGURE
    plt.figure(2)

    peak = np.argmax(y[-1])  # find which position in first y series is the max
    x_peak = x[peak]  # find the value of x at the position calcd from above

    # find max in series with no DNA in
    noDNA = y[0]
    norm_value = noDNA[peak]

    # normalise y
    normy = []
    for z in y:
        normy.append(z / norm_value)

    # plot
    plot_multiline(x, normy, 'Wavelength [nm]', 'Normalised Emission Intensity')
    plt.savefig('NormalisedEmissionTitration.png', dpi=300)

    # INTENSITY AT ONE PEAK AND KD CALC
    plt.figure(3)

    peak = np.argmax(y[1])  # find which position in first y series is the max
    x_peak = x[peak]  # find the value of x at the position calcd from above

    newy = []  # this will be the y axis
    for i in y:
        newy.append(i[peak])

    normy = norm_zero_to_one(newy)

    y_fit, Kd = fit_curve_sig(names, normy)

    plot_fittedcurve(names, normy, Kd, y_fit, type)
    plt.savefig('Emission-Kd.png', dpi=300)
elif type == 4: #Nonlinear Kb plot
    # open csv file
    infile = input('Name of CSV file: ')
    title = input('Graph title: ')
    data, names = opentext(infile, 0)
    xp_name = infile.replace('.csv', '')

    plt.figure(1)
    plt.xlabel('[DNA] [x $10^{-6}$ M$^{-1}$]')
    plt.ylabel('($\epsilon_a$ - $\epsilon_f$) / ($\epsilon_b$ - $\epsilon_f$)')

    x = data[0]
    y = data[1]

    y_fit, Kb, s, r2 = fit_curve_mcghee(x, y)

    plt.title(title)
    plot_fittedcurve(x, y, Kb, y_fit, type, s, r2)
    plt.savefig('UV-Kb.png', dpi=300)
else:
    print("Incorrect input, please try again.")