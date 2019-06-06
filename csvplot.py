import os
import wx
import wx.grid
import matplotlib
matplotlib.use('WXAgg')
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
# import events as evts
import functions as ftns
import plotfunctions as pf



class MainFrame(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title='CSVplot')
        self.setUI()
        self.Centre()

    def setUI(self):
        self.panel = wx.Panel(self)

        #create vertical box sizer
        self.mainbox = wx.BoxSizer(wx.VERTICAL)

        #create horizontal box1 and the things to go into it
        hbox_inputCSV = wx.BoxSizer(wx.HORIZONTAL)

        self.input_path_txtbx = wx.TextCtrl(self.panel, value="Enter path to CSV")
        load_csv_btn = wx.Button(self.panel, label='Browse')
        load_csv_btn.Bind(wx.EVT_BUTTON, self.load_csv_press)

        # add ( things your adding, proportion, wx.ALL = border all around, value of border size (px) )
        #hbox = LOAD CSV
        hbox_inputCSV.Add(self.input_path_txtbx, 1, wx.ALL, 5)
        hbox_inputCSV.Add(load_csv_btn, 0, wx.ALL, 5)


        #hbox = CHOOSE CSV FORMAT
        hbox_csvFormat = wx.BoxSizer(wx.HORIZONTAL)
        self.headers_txt = wx.StaticText(self.panel, label="Set headers:")
        self.set_headers_tb = wx.TextCtrl(self.panel, value="1", size=(25,25))
        csv_format_txt = wx.StaticText(self.panel, label="Choose CSV format:")
        self.csv_format = wx.ComboBox(self.panel, choices=["x,y,y,...", "x,y,x,y,..."])
        hbox_csvFormat.Add(self.headers_txt, 0, wx.ALL, 5)
        hbox_csvFormat.Add(self.set_headers_tb, 0, wx.ALL, 5)
        hbox_csvFormat.Add(csv_format_txt, 0, wx.ALL, 5)
        hbox_csvFormat.Add(self.csv_format, 0, wx.ALL, 5)

        vbox_CSV = wx.StaticBoxSizer(wx.VERTICAL, self.panel, label="CSV Format")
        vbox_CSV.Add(hbox_inputCSV, 0, wx.ALL | wx.ALIGN_RIGHT | wx.EXPAND, 5)
        vbox_CSV.Add(hbox_csvFormat, 0, wx.ALL, 5)

        self.mainbox.Add(vbox_CSV, 0, wx.ALL | wx.EXPAND, 5)

        #PRIMARY SETTINGS HERE

        #next hbox = TYPE OF PLOT
        hbox_PrimPlotType = wx.BoxSizer(wx.HORIZONTAL)
        prim_plot_typ_txt = wx.StaticText(self.panel, label="Preset Formats:")
        self.prim_plot_type = wx.ComboBox(self.panel, choices=["Common Presets",
                                                               "UV Titration with Linear Kb",
                                                               "UV Titration with Nonlinear Kb",
                                                               "CD Titration with Tm",
                                                               "Emission Titration with Kd"])
        hbox_PrimPlotType.Add(prim_plot_typ_txt, 0, wx.ALL | wx.ALIGN_LEFT, 5)
        hbox_PrimPlotType.Add(self.prim_plot_type, 0, wx.ALL | wx.ALIGN_LEFT, 5)
        self.prim_plot_type.Bind(wx.EVT_COMBOBOX, self.load_preset)

        #next hbox = TICK BOXES
        gbox_PrimParams = wx.GridSizer(5,2,5,5)
        self.bg_sub_chk = wx.CheckBox(self.panel, label="Background Subtract (first y series)")
        self.zero_correct_chk = wx.CheckBox(self.panel, label="Zero Correct (at highest x)")
        self.horiz_line_chk = wx.CheckBox(self.panel, label="Horizontal Line (y = 0)")
        self.vert_line_chk = wx.CheckBox(self.panel, label="Vertical Line (x = 0)")

        self.x_ax_limit_low = wx.TextCtrl(self.panel, value="Lower X limit")
        self.x_ax_limit_up = wx.TextCtrl(self.panel, value="Upper X limit")
        hbox_XLimits = wx.BoxSizer(wx.HORIZONTAL)
        hbox_XLimits.AddMany([(self.x_ax_limit_low, 1, wx.EXPAND, 0),
                             (self.x_ax_limit_up, 1, wx.EXPAND, 0)])

        self.y_ax_limit_low = wx.TextCtrl(self.panel, value="Lower Y limit")
        self.y_ax_limit_up = wx.TextCtrl(self.panel, value="Upper Y limit")
        hbox_YLimits = wx.BoxSizer(wx.HORIZONTAL)
        hbox_YLimits.AddMany([(self.y_ax_limit_low, 1, wx.EXPAND, 0),
                             (self.y_ax_limit_up, 1, wx.EXPAND, 0)])

        self.x_ax_label = wx.TextCtrl(self.panel, value="X Label")
        self.y_ax_label = wx.TextCtrl(self.panel, value="Y Label")

        gbox_PrimParams.AddMany([self.bg_sub_chk,
                        self.zero_correct_chk,
                        self.horiz_line_chk,
                        self.vert_line_chk,
                        (hbox_XLimits, 0, wx.EXPAND, 0),
                        (hbox_YLimits, 0, wx.EXPAND, 0),
                        (self.x_ax_label, 0, wx.EXPAND, 0),
                        (self.y_ax_label, 0, wx.EXPAND, 0)])

        #hbox = TITLE
        hbox_PrimTitle = wx.BoxSizer(wx.HORIZONTAL)
        self.title_txt = wx.TextCtrl(self.panel, value="Plot title")
        hbox_PrimTitle.Add(self.title_txt, 1, wx.EXPAND, 0)

        #hbox = COLOR GRADIENT
        hbox_Gradient = wx.BoxSizer(wx.HORIZONTAL)
        gradient_txt = wx.StaticText(self.panel, label="Select Colour Gradient:")
        self.gradient = wx.ComboBox(self.panel, choices=["Blue - Red"])
        hbox_Gradient.Add(gradient_txt, 0, wx.ALL, 5)
        hbox_Gradient.Add(self.gradient, 0, wx.ALL, 5)


        vbox_PrimParams = wx.StaticBoxSizer(wx.VERTICAL, self.panel, label="Primary Plot Settings")
        vbox_PrimParams.Add(hbox_PrimPlotType, 0, wx.ALL, 5)
        vbox_PrimParams.Add(gbox_PrimParams, 0, wx.ALL, 5)
        vbox_PrimParams.Add(hbox_PrimTitle, 0, wx.ALL | wx.EXPAND, 5)
        vbox_PrimParams.Add(hbox_Gradient, 0, wx.ALL, 5)
        self.mainbox.Add(vbox_PrimParams, 0, wx.ALL | wx.EXPAND, 5)

        #SECONDARY PLOT HERE

        #hbox = CONFIRM SECOND PLOT
        hbox_ConfSecPlot = wx.BoxSizer(wx.HORIZONTAL)
        self.confirm_sec_plot = wx.CheckBox(self.panel, label="Confirm Secondary Plot")
        self.update_grid = wx.Button(self.panel, label="Update X From Grid")
        self.update_grid.Bind(wx.EVT_BUTTON, self.update_grid_press)
        hbox_ConfSecPlot.Add(self.confirm_sec_plot, 1, wx.ALIGN_LEFT, 5)
        hbox_ConfSecPlot.Add(self.update_grid, 1, wx.ALIGN_RIGHT, 5)

        #hbox = TYPE OF PLOT
        self.sec_plot_type = wx.ComboBox(self.panel, choices=["Common Functions",
                                                              "Linear Binding Constant",
                                                              "Nonlinear Binding Constant (McGhee von Hippel)",
                                                              "CD Melt"])
        self.sec_plot_type.Bind(wx.EVT_COMBOBOX, self.SecPlotChoice)

        #hbox = FUNCTIONS
        hbox_SecParams = wx.BoxSizer(wx.HORIZONTAL)
        self.secplot_xlabel = wx.TextCtrl(self.panel, value="X Label")
        self.secplot_ylabel =  wx.TextCtrl(self.panel, value="Y Label")
        hbox_SecParams.AddMany([(self.secplot_xlabel, 1, wx.ALL | wx.EXPAND, 5),
                        (self.secplot_ylabel, 1, wx.ALL | wx.EXPAND, 5)])

        #hbox = X VALUE CHOICE
        hbox_SecXValue = wx.BoxSizer(wx.HORIZONTAL)
        specific_x_val_txt = wx.StaticText(self.panel, label="Position in X to call function on:")
        self.specific_x_val = wx.TextCtrl(self.panel, size=(50,25))
        r2_txt = wx.StaticText(self.panel, label="R^2")
        self.r2 = wx.TextCtrl(self.panel, size=(75,25))
        hbox_SecXValue.Add(specific_x_val_txt, 0, wx.ALL, 5)
        hbox_SecXValue.Add(self.specific_x_val, 0, wx.ALL, 5)
        hbox_SecXValue.Add(r2_txt, 0, wx.ALL, 5)
        hbox_SecXValue.Add(self.r2, 0, wx.ALL, 5)

        self.vbox_SecParams = wx.StaticBoxSizer(wx.VERTICAL, self.panel, label="Secondary Plot Settings")
        self.vbox_SecParams.Add(hbox_ConfSecPlot, 0, wx.ALL | wx.EXPAND, 5)
        self.vbox_SecParams.Add(self.sec_plot_type, 0, wx.ALL | wx.EXPAND, 5)
        self.vbox_SecParams.Add(hbox_SecParams, 0, wx.ALL | wx.EXPAND, 5)
        self.vbox_SecParams.Add(hbox_SecXValue, 0, wx.ALL, 5)

        self.vboxLinear = wx.BoxSizer(wx.HORIZONTAL)
        c_txt = wx.StaticText(self.panel, label="Concentration (x10$^6$ M):")
        self.c = wx.TextCtrl(self.panel, size=(75, 25), value="1")
        self.vboxLinear.AddMany([(c_txt, 0, wx.ALL, 5),
                                 (self.c, 0, wx.ALL, 5)])

        self.hboxLinear = wx.BoxSizer(wx.HORIZONTAL)
        slope_txt = wx.StaticText(self.panel, label="Slope:")
        self.slope_box = wx.TextCtrl(self.panel, style=wx.TE_READONLY, value="", size=(75, 25))
        intercept_txt = wx.StaticText(self.panel, label="Intercept:")
        self.intercept_box = wx.TextCtrl(self.panel, style=wx.TE_READONLY, value="", size=(75, 25))
        slope_intercept_txt = wx.StaticText(self.panel, label="Slope/Intercept:")
        self.slope_intercept_box = wx.TextCtrl(self.panel, style=wx.TE_READONLY, value="", size=(75, 25))

        self.hboxLinear.AddMany([(slope_txt, 0, wx.ALL, 5),
                                  (self.slope_box, 0, wx.ALL, 5),
                                  (intercept_txt, 0, wx.ALL, 5),
                                  (self.intercept_box, 0, wx.ALL, 5),
                                  (slope_intercept_txt, 0, wx.ALL, 5),
                                  (self.slope_intercept_box, 0, wx.ALL, 5)])


        self.hbox_Nonlinear = wx.BoxSizer(wx.HORIZONTAL)
        NLBindingConst_txt = wx.StaticText(self.panel, label="Kb (x10$^6$ M):")
        self.NLBindingConst = wx.TextCtrl(self.panel, style=wx.TE_READONLY, value="", size=(50, 25))
        BindingSize_txt = wx.StaticText(self.panel, label="Site Size (bps):")
        self.BindingSize = wx.TextCtrl(self.panel, style=wx.TE_READONLY, value="", size=(50, 25))
        self.hbox_Nonlinear.AddMany([(NLBindingConst_txt, 0, wx.ALL, 5),
                                     (self.NLBindingConst, 0, wx.ALL, 5),
                                     (BindingSize_txt, 0, wx.ALL, 5),
                                     (self.BindingSize, 0, wx.ALL, 5)])


        self.hbox_CDMelt = wx.BoxSizer(wx.HORIZONTAL)
        startX_txt = wx.StaticText(self.panel, label="First x:")
        self.startX = wx.TextCtrl(self.panel, size=(50, 25))
        endX_txt = wx.StaticText(self.panel, label="Final x:")
        self.endX = wx.TextCtrl(self.panel, size=(50, 25))
        increment_txt = wx.StaticText(self.panel, label="Increments:")
        self.increment = wx.TextCtrl(self.panel, size=(50, 25))
        meltT_txt = wx.StaticText(self.panel, label="Y=0.5, X=")
        self.meltT = wx.TextCtrl(self.panel, style=wx.TE_READONLY, size=(50, 25))
        self.hbox_CDMelt.AddMany([(startX_txt, 0, wx.ALL, 5),
                                  (self.startX, 0, wx.ALL, 5),
                                  (endX_txt, 0, wx.ALL, 5),
                                  (self.endX, 0, wx.ALL, 5),
                                  (increment_txt, 0, wx.ALL, 5),
                                  (self.increment, 0, wx.ALL, 5),
                                  (meltT_txt, 0, wx.ALL, 5),
                                  (self.meltT, 0, wx.ALL, 5)])

        self.vbox_SecParams.Add(self.hboxLinear, 0, wx.ALL, 5)
        self.vbox_SecParams.Add(self.hbox_Nonlinear, 0, wx.ALL, 5)
        self.vbox_SecParams.Add(self.hbox_CDMelt, 0, wx.ALL, 5)
        self.vbox_SecParams.Add(self.vboxLinear, 0, wx.ALL, 5)

        self.vbox_SecParams.Hide(self.hboxLinear)
        self.vbox_SecParams.Hide(self.hbox_Nonlinear)
        self.vbox_SecParams.Hide(self.hbox_CDMelt)
        self.vbox_SecParams.Hide(self.vboxLinear)

        self.mainbox.Add(self.vbox_SecParams, 0, wx.ALL | wx.EXPAND, 5)

        #ADD COLOUR AND EDITING OF SECOND PLOT

        #CONFIRM PLOT HERE
        vbox_ConfPlot = wx.StaticBoxSizer(wx.VERTICAL, self.panel, label="Confirm Plot")
        hbox_ConfirmPlot = wx.BoxSizer(wx.HORIZONTAL)
        self.savefig1 = wx.Button(self.panel, label="Save Figure 1")
        self.savefig1.Bind(wx.EVT_BUTTON, self.save_fig_1)
        self.savefig2 = wx.Button(self.panel, label="Save Figure 2")
        self.savefig2.Bind(wx.EVT_BUTTON, self.save_fig_2)
        plot_btn = wx.Button(self.panel, label="Plot")
        plot_btn.Bind(wx.EVT_BUTTON, self.plot_btn_press)
        hbox_ConfirmPlot.Add(self.savefig1, 0, wx.ALL, 5)
        hbox_ConfirmPlot.Add(self.savefig2, 0, wx.ALL, 5)
        hbox_ConfirmPlot.Add(plot_btn, 0, wx.ALL, 5)

        vbox_ConfPlot.Add(hbox_ConfirmPlot, 0, wx.ALIGN_RIGHT | wx.EXPAND, 5)

        self.mainbox.Add(vbox_ConfPlot, 0, wx.ALL | wx.EXPAND, 5)

        figbox = wx.BoxSizer(wx.VERTICAL)

        self.figure = Figure(figsize=(5, 6), dpi=100)
        self.axes1 = self.figure.add_subplot(211)
        self.axes2 = self.figure.add_subplot(212)
        self.figure.subplots_adjust(hspace=0.5, wspace=0.5)

        self.canvas = FigureCanvas(self, 0, self.figure)

        figbox.Add(self.canvas, 1, wx.CENTER | wx.EXPAND, 5)

        #CREATE GRID
        gridbox = wx.BoxSizer(wx.VERTICAL)
        self.grid = wx.grid.Grid(self.panel)
        self.grid.CreateGrid(35, 2)
        self.grid.Bind(wx.EVT_KEY_DOWN, self.OnKey)
        self.data4undo = [0, 0, '']
        gridbox.Add(self.grid)

        self.framebox = wx.BoxSizer(wx.HORIZONTAL)
        self.framebox.Add(gridbox)
        self.framebox.Add(self.mainbox)
        self.framebox.Add(figbox, 1, wx.EXPAND)


        self.panel.SetSizerAndFit(self.framebox)
        self.framebox.SetSizeHints(self)

        self.Show()
        self.Center()

    # ------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    # EVENTS

    def load_csv_press(self, event):
        input_path, csv_filename, csv_dir = ftns.load_csv(self)
        self.input_path_txtbx.SetLabel(input_path)
        output_file = csv_filename.replace(".csv", ".png")
        output_path = os.path.join(csv_dir, output_file)

    def plot_btn_press(self, event):
        # functions to call:

        # get headers and csv format then trim the data

        # format = self.csv_format

        self.axes1.clear()
        self.axes1.spines['right'].set_visible(False)
        self.axes1.spines['top'].set_visible(False)

        self.axes2.clear()
        self.axes2.spines['right'].set_visible(False)
        self.axes2.spines['top'].set_visible(False)

        data = ftns.opentext(self.input_path_txtbx.GetLabel(), int(self.set_headers_tb.GetValue()))
        if self.csv_format.GetCurrentSelection() == 1:
            isY = 1
            temp_data = []
            temp_data.append(data[0])
            while isY < len(data):
                if (isY % 2) == 0:  # removes all even numbered arrays (the x values in x,y,x,y,x,y,...)
                    pass
                else:
                    temp_data.append(data[isY])
                isY += 1
            data = temp_data
        else:
            pass

        self.x = np.array(data[0])
        self.y = np.array(data[1:])

        # reverse arrays in x is going large - small (fixes issues with finding closes value later
        if self.x[0] > self.x[-1]:
            self.x = self.x[::-1]
            tempY = []
            for i in self.y:
                tempY.append(i[::-1])
            self.y = np.array(tempY)
        # y = y[:-1]

        # get all parameters on the primary plot

        prim_format = self.prim_plot_type.GetCurrentSelection()
        bg_sub = self.bg_sub_chk.GetValue()
        zero_corr = self.zero_correct_chk.GetValue()
        hline = self.horiz_line_chk.GetValue()
        vline = self.vert_line_chk.GetValue()
        xlabel = self.x_ax_label.GetValue()
        ylabel = self.y_ax_label.GetValue()
        title = self.title_txt.GetValue()
        color = self.gradient.GetCurrentSelection()

        # plot primary plot

        # background subtract
        if bg_sub is True:
            bg = self.y[0]
            self.y = self.y[1:]
            tempY = []
            for i in self.y:
                tempY.append(i - bg)
            self.y = np.array(tempY)

        # zero correct
        if zero_corr is True:
            max_x = max(self.x)
            zero_pos = np.where(self.x == max_x)
            self.y = ftns.zero_correct(zero_pos, self.y)
        else:
            pass

        pf.plot_multiline(self.axes1, self.x, self.y, xlabel, ylabel, title, hline, vline, color,
                          self.x_ax_limit_low.GetValue(), self.x_ax_limit_up.GetValue(), self.y_ax_limit_low.GetValue(),
                          self.y_ax_limit_up.GetValue())

        # secondary plot

        confirm_sec = self.confirm_sec_plot.GetValue()

        # get parameters

        if confirm_sec is True:
            try:
                self.sec_type = self.sec_plot_type.GetCurrentSelection()  # select type of plot
                self.xvalue = float(self.specific_x_val.GetValue())  # specific x value
                xval = ftns.find_closest(self.x, self.xvalue, self)
                self.sec_y = np.array(ftns.get_newy(self.x, self.y, xval))  # get y values from the series at a specific x
                self.sec_x = np.array(ftns.get_newx(self))  # get x values from the increments
                pf.plotsec(self)
                ftns.send_to_grid(self)
            except ValueError:
                ftns.error_report(self, "Value missing in Secondary Plot Settings")
        else:
            pass
        self.figure.canvas.draw()

    def update_grid_press(self, event):
        # get x from grid
        num = 0
        lenX = len(self.sec_x)
        tempX = []
        while num < lenX:
            tempX.append(float(self.grid.GetCellValue(num, 0)))
            num += 1
        self.sec_x = np.array(tempX)
        pf.plotsec(self)
        self.figure.canvas.draw()

    def SecPlotChoice(self, event):
        self.vbox_SecParams.Hide(self.hboxLinear)
        self.vbox_SecParams.Hide(self.hbox_Nonlinear)
        self.vbox_SecParams.Hide(self.hbox_CDMelt)
        self.vbox_SecParams.Hide(self.vboxLinear)

        if self.sec_plot_type.GetCurrentSelection() == 0:  # none
            ftns.resize_sizer(self, self.vbox_SecParams)

        if self.sec_plot_type.GetCurrentSelection() == 1:  # linear
            self.vbox_SecParams.Show(self.hboxLinear)
            self.vbox_SecParams.Show(self.vboxLinear)
            ftns.resize_sizer(self, self.vbox_SecParams)

        elif self.sec_plot_type.GetCurrentSelection() == 2:  # nonlinear
            self.vbox_SecParams.Show(self.hbox_Nonlinear)
            self.vbox_SecParams.Show(self.vboxLinear)
            ftns.resize_sizer(self, self.vbox_SecParams)

        elif self.sec_plot_type.GetCurrentSelection() == 3:  # Tm/Kd
            self.vbox_SecParams.Show(self.hbox_CDMelt)
            ftns.resize_sizer(self, self.vbox_SecParams)

    def load_preset(self, event):
        if self.prim_plot_type.GetCurrentSelection() == 1:  # UV linear
            ftns.set_labels(self, "Wavelength (nm)", "Absorption (a.u.)", "UV Titration", 1, "[DNA] (x10$^6$ M)",
                            "[DNA]/($\epsilon_a$ - $\epsilon_f$)")
            self.SecPlotChoice(self)
        elif self.prim_plot_type.GetCurrentSelection() == 2:  # UV nonlinear
            ftns.set_labels(self, "Wavelength (nm)", "Absorption (a.u.)", "UV Titration", 2, "[DNA] (x10$^6$ M)",
                            "($\epsilon_a$ - $\epsilon_b$)/($\epsilon_f$ - $\epsilon_b$)")
            self.SecPlotChoice(self)
        elif self.prim_plot_type.GetCurrentSelection() == 3:  # cd melt
            ftns.set_labels(self, "Wavelength (nm)", "Ellipticity (mdeg)", "CD Melt", 3, "Temperature ($^\circ$C)",
                            "Normalised Ellipticity")
            self.startX.SetValue("5")
            self.endX.SetValue("95")
            self.increment.SetValue("5")
            self.SecPlotChoice(self)
        elif self.prim_plot_type.GetCurrentSelection() == 4:  # emission kd
            ftns.set_labels(self, "Wavelength (nm)", "Emission Intensity (a.u.)", "Emission Intensity Titration", 3,
                            "[DNA] x10$^6$ M",
                            "Normalised Emission Intensity")
            self.SecPlotChoice(self)
        return

    def save_fig_1(self, event):
        path = ftns.save_csv(self)
        extent = ftns.full_extent(self.axes1).transformed(self.figure.dpi_scale_trans.inverted())
        self.figure.savefig(path, bbox_inches=extent, dpi=600)

    def save_fig_2(self, event):
        path = ftns.save_csv(self)
        extent = ftns.full_extent(self.axes2).transformed(self.figure.dpi_scale_trans.inverted())
        self.figure.savefig(path, bbox_inches=extent, dpi=600)

    def OnKey(self, event):
        if event.ControlDown() and event.GetKeyCode() == 67:
            ftns.copy(self)
            # If Ctrl+V is pressed...
        if event.ControlDown() and event.GetKeyCode() == 86:
            ftns.paste(self, 'clip')
            # If Ctrl+Z is pressed...
        if event.ControlDown() and event.GetKeyCode() == 90:
            if self.data4undo[2] != '':
                ftns.paste(self, 'undo')
            # If del is pressed...
        if event.GetKeyCode() == 127:
            # Call delete method
            ftns.delete(self)
            # Skip other Key events
        if event.GetKeyCode():
            event.Skip()
            return

    # ------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    # MAIN


if __name__ == '__main__':
    app = wx.App()
    frame = MainFrame()
    app.MainLoop()