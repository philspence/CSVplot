import argparse
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from functions import *

parser = argparse.ArgumentParser()
parser.add_argument('-i', dest='filename', metavar ='Input filename', help='enter csv filename', required=True)
args = parser.parse_args()

#open csv file
infile = args.filename
data, names = opentext(infile, 1)

#plot multiline
plt.figure(1)
x = data[0]
y = data[1:]
plot_multiline(x, y, 'Wavelength [nm]', 'Emission Intensity [a.u.]')
plt.savefig('EmissionTitration.png', dpi=300)

#NORMALISED DATA FIGURE
plt.figure(2)

peak = np.argmax(y[-1]) #find which position in first y series is the max
x_peak = x[peak] #find the value of x at the position calcd from above

#find max in series with no DNA in
noDNA = y[0]
norm_value = noDNA[peak]

#normalise y
normy = []
for z in y:
    normy.append(z/norm_value)

#plot
plot_multiline(x, normy, 'Wavelength [nm]', 'Normalised Emission Intensity')
plt.savefig('NormalisedEmissionTitration.png', dpi=300)

#INTENSITY AT ONE PEAK AND KD CALC
plt.figure(3)

peak = np.argmax(y[1]) #find which position in first y series is the max
x_peak = x[peak] #find the value of x at the position calcd from above

newy = [] #this will be the y axis
for i in y:
    newy.append(i[peak])

normy = norm_zero_to_one(newy)

y_fit, Kd = fit_curve(names, normy)

plot_fittedcurve(names, normy, Kd, y_fit)
plt.savefig('Emission-Kd.png', dpi=300)


