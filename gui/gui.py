import os
import datetime
from tkinter import *
from tkinter.filedialog import askdirectory

class fridgeLogger(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent, background='white')
        
        #Set member variables:
        self.parent = parent
        self.dirPath = StringVar()
        self.dirPath.set(os.getcwd())
        self.startDate = StringVar()
        self.startDate.set('21/12/12')
        self.endDate = StringVar()
        self.endDate.set(datetime.datetime.now().strftime('%d/%m/%y'))
        self.daysAgo = StringVar()
        self.daysAgo.set('3')
        self.maxPts = StringVar()
        self.maxPts.set('1000000')

        #Boolean variable to determine to use start date-end date or 'days ago'
        self.dateRange = BooleanVar(False)
        self.limitPts = BooleanVar(False)
        self.dirPathEntry = []
        self.startDateEntry = []
        self.endDateEntry = []
        self.daysAgoEntry = []
        self.maxPtsEntry = []
        self.absoluteDateCheck = []
        self.relativeDateCheck = []
        self.numPlots = 0

        self.initUI()

    def initUI(self):
        self.parent.title('fridgeLogger')
        self.pack(fill=BOTH)

        frame1 = Frame(self)
        frame1.pack(side=TOP, fill=BOTH)

        #Text box to insert directory path:
        lbl1 = Label(frame1, text='Path:', width=6)
        lbl1.pack(side=LEFT)
        self.dirPathEntry = Entry(frame1, width=40, textvariable=self.dirPath)
        self.dirPathEntry.pack(side=LEFT, expand=True, fill=X)
        btn = Button(frame1, width=2, text='...', command=lambda: self.setDirectory())
        btn.pack(side=LEFT)

        frame2 = Frame(self)
        frame2.pack(side=TOP, fill=BOTH)

        #Fill in start date and end date of log files:
        self.absoluteDateCheck = Checkbutton(frame2, text='Start date:')
        self.absoluteDateCheck.pack(side=LEFT)
        self.absoluteDateCheck.config(command=lambda: self.toggleDateRange())
        self.startDateEntry = Entry(frame2, width=10, textvariable=self.startDate, state=DISABLED)
        self.startDateEntry.pack(side=LEFT, expand=True)
        lbl2 = Label(frame2, text='End date:', width=7)
        lbl2.pack(side=LEFT)
        self.endDateEntry = Entry(frame2, width=10, textvariable=self.endDate, state=DISABLED)
        self.endDateEntry.pack(side=LEFT, expand=True)
        lbl3 = Label(frame2, text='dd/mm/yy', width=8)
        lbl3.pack(side=LEFT)

        frame3 = Frame(self)
        frame3.pack(side=TOP, fill=BOTH)

        #Fill in how many days ago
        self.relativeDateCheck = Checkbutton(frame3, text='Days ago:')
        self.relativeDateCheck.pack(side=LEFT)
        self.relativeDateCheck.select()
        self.relativeDateCheck.config(command=lambda: self.toggleDateRange())

        self.daysAgoEntry = Entry(frame3, width=5, textvariable=self.daysAgo)
        self.daysAgoEntry.pack(side=LEFT, expand=True)

        #Fill in maximum sample points
        chk3 = Checkbutton(frame3, text='Max points:')
        chk3.pack(side=LEFT)
        chk3.config(command=lambda: self.toggleMaxPts())

        self.maxPtsEntry = Entry(frame3, width=10, textvariable=self.maxPts, state=DISABLED)
        self.maxPtsEntry.pack(side=LEFT, expand=True)

        frame4 = Frame(self)
        frame4.pack(side=TOP, fill=BOTH)

        btn2 = Button(frame4, text='Add plotting window', command=lambda: self.addPlot())
        btn2.pack(side=LEFT)
    
    def addPlot(self):
        frame = Frame(self)
        frame.pack(side=TOP, fill=BOTH)

        lbl1 = Label(frame, text='Y-axis (left)')
        lbl1.pack(side=LEFT)

    def setDirectory(self):
        name = askdirectory()
        self.dirPath.set(name)

    def toggleDateRange(self):
        self.dateRange = not self.dateRange
        if self.dateRange == True:
            self.startDateEntry.config(state=DISABLED)
            self.endDateEntry.config(state=DISABLED)
            self.absoluteDateCheck.deselect()
            self.daysAgoEntry.config(state=NORMAL)
            self.relativeDateCheck.select()
        else:
            self.startDateEntry.config(state=NORMAL)
            self.endDateEntry.config(state=NORMAL)
            self.absoluteDateCheck.select()
            self.daysAgoEntry.config(state=DISABLED)
            self.relativeDateCheck.deselect()

    def toggleMaxPts(self):
        self.limitPts = not self.limitPts
        if self.limitPts == False:
            self.maxPtsEntry.config(state=NORMAL)
        else:
            self.maxPtsEntry.config(state=DISABLED)

if __name__ == '__main__':
    root = Tk()
    app = fridgeLogger(root)
    root.mainloop()

