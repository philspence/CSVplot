import wx
import numpy as np
import matplotlib
# matplotlib.use('WXAgg')
from matplotlib.transforms import Bbox

def load_csv():
    wildcard = "CSV Files (*.csv)|*.csv"
    dialog = wx.FileDialog(None, "Open CSV", wildcard=wildcard, style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)

    if dialog.ShowModal() == wx.ID_CANCEL:
        return
    path = dialog.GetPath()
    csv_filename = dialog.GetFilename()
    csv_dir = dialog.GetDirectory()
    return path, csv_filename, csv_dir

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

def get_newx(self):
    if self.startX.IsEmpty() is False and self.endX.IsEmpty() is False and self.increment.IsEmpty() is False and self.sec_plot_type.GetCurrentSelection() == 3:
        startX = float(self.startX.GetValue())
        endX = float(self.endX.GetValue())
        increment = int(self.increment.GetValue())
        inc = int((endX - startX) / increment) + 1
        self.sec_x = np.linspace(startX, endX, inc)
    else:
        self.sec_x = np.linspace(0, (len(self.sec_y) - 1), len(self.sec_y))
    return self.sec_x

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

def send_to_grid(self):
    num = 0
    lenX = len(self.sec_x)
    self.grid.ClearGrid()
    while num < lenX:
        self.grid.SetCellValue(num, 0, str(self.sec_x[num]))
        self.grid.SetCellValue(num, 1, str(self.sec_y[num])[:4])
        num += 1
    self.grid.ForceRefresh()

def resize_sizer(self, sizer):
    sizer.Layout()
    self.mainbox.Layout()
    self.framebox.Layout()
    self.panel.SetSizerAndFit(self.framebox)
    self.framebox.SetSizeHints(self)

def set_labels(self, xlabel, ylabel, title, type, secxlabel, secylabel):
    self.x_ax_label.SetValue(xlabel)
    self.y_ax_label.SetValue(ylabel)
    self.title_txt.SetValue(title)
    self.sec_plot_type.SetSelection(type)
    self.secplot_xlabel.SetValue(secxlabel)
    self.secplot_ylabel.SetValue(secylabel)

def full_extent(ax, pad=0.0):
    # For text objects, we need to draw the figure first, otherwise the extents
    # are undefined.
    ax.figure.canvas.draw()
    items = ax.get_xticklabels() + ax.get_yticklabels()
    items += [ax, ax.title, ax.xaxis.label, ax.yaxis.label]
    items += [ax, ax.title]
    bbox = Bbox.union([item.get_window_extent() for item in items])

    return bbox.expanded(1.0 + pad, 1.0 + pad)

def save_csv(self):
    wildcard = "CSV Files (*.png)|*.png"
    dialog = wx.FileDialog(self, "Save PNG", wildcard=wildcard, style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)

    if dialog.ShowModal() == wx.ID_CANCEL:
        return
    path = dialog.GetPath()
    return path

def error_report(self, msg):
    error = wx.MessageDialog(self, msg, style=wx.OK, caption="Error")
    error.ShowModal()

def copy(self):
    # Number of rows and cols
    topleft = self.grid.GetSelectionBlockTopLeft()
    if list(topleft) == []:
        topleft = []
    else:
        topleft = list(topleft[0])
    bottomright = self.grid.GetSelectionBlockBottomRight()
    if list(bottomright) == []:
        bottomright = []
    else:
        bottomright = list(bottomright[0])
    if list(self.grid.GetSelectionBlockTopLeft()) == []:
        rows = 1
        cols = 1
        iscell = True
    else:
        rows = bottomright[0] - topleft[0] + 1
        cols = bottomright[1] - topleft[1] + 1
        iscell = False
    # data variable contain text that must be set in the clipboard
    data = ''
    # For each cell in selected range append the cell value in the data variable
    # Tabs '    ' for cols and '\r' for rows
    for r in range(rows):
        for c in range(cols):
            if iscell:
                data += str(self.grid.GetCellValue(self.grid.GetGridCursorRow() + r, self.grid.GetGridCursorCol() + c))
            else:
                data += str(self.grid.GetCellValue(topleft[0] + r, topleft[1] + c))
            if c < cols - 1:
                data += '    '
        data += '\n'
    # Create text data object
    clipboard = wx.TextDataObject()
    # Set data object value
    clipboard.SetText(data)
    # Put the data in the clipboard
    if wx.TheClipboard.Open():
        wx.TheClipboard.SetData(clipboard)
        wx.TheClipboard.Close()
    else:
        wx.MessageBox("Can't open the clipboard", "Error")

def paste(self, stage):
    topleft = list(self.grid.GetSelectionBlockTopLeft())
    if stage == 'clip':
        clipboard = wx.TextDataObject()
        if wx.TheClipboard.Open():
            wx.TheClipboard.GetData(clipboard)
            wx.TheClipboard.Close()
        else:
            wx.MessageBox("Can't open the clipboard", "Error")
        data = clipboard.GetText()
        if topleft == []:
            rowstart = self.grid.GetGridCursorRow()
            colstart = self.grid.GetGridCursorCol()
        else:
            rowstart = topleft[0][0]
            colstart = topleft[0][1]
    elif stage == 'undo':
        data = self.data4undo[2]
        rowstart = self.data4undo[0]
        colstart = self.data4undo[1]
    else:
        wx.MessageBox("Paste method " + stage + " does not exist", "Error")
    text4undo = ''
    # Convert text in a array of lines
    for y, r in enumerate(data.splitlines()):
        # Convert c in a array of text separated by tab
        for x, c in enumerate(r.split('    ')):
            if y + rowstart < self.grid.NumberRows and x + colstart < self.grid.NumberCols:
                text4undo += str(self.grid.GetCellValue(rowstart + y, colstart + x)) + '    '
                self.grid.SetCellValue(rowstart + y, colstart + x, c)
        text4undo = text4undo[:-1] + '\n'
    if stage == 'clip':
        self.data4undo = [rowstart, colstart, text4undo]
    else:
        self.data4undo = [0, 0, '']

def delete(self):
    # print "Delete method"
    # Number of rows and cols
    topleft = list(self.grid.GetSelectionBlockTopLeft())
    bottomright = list(self.grid.GetSelectionBlockBottomRight())
    if topleft == []:
        rows = 1
        cols = 1
    else:
        rows = bottomright[0][0] - topleft[0][0] + 1
        cols = bottomright[0][1] - topleft[0][1] + 1
    # Clear cells contents
    for r in range(rows):
        for c in range(cols):
            if topleft == []:
                self.grid.SetCellValue(self.grid.GetGridCursorRow() + r, self.grid.GetGridCursorCol() + c, '')
            else:
                self.grid.SetCellValue(topleft[0][0] + r, topleft[0][1] + c, '')