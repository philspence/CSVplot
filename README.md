# CSVplot

CSVplot is a GUI, written in python, to plot multiline graphs using matplotlib and perform various secondary functions.

![image of CSV plot](https://i.imgur.com/I9gbOJP.png)

Load CSV files in either x,y,y,... or x,y,x,y,... format, plot the multiline titrations and then load common presets:

* Calculate ligand binding constants using linear or nonlinear models
* Calculate binding constants from emission intensity titrations
* Calculate melting temperatures from CD or UV titrations

Options to save the figures as PNGs and edit the axis labels/range are available.

Prerequisites:
* matplotlib
* numpy
* wxpython
* scipy
