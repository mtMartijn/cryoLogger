#test.py
import tkinter as tk  # for python 3
import pygubu
from datetime import datetime
import Gnuplot
import time
import concat
import sys

'''
        self.g('set terminal qt')

'''

class Application:
    def __init__(self, master):

        #1: Create a builder
        self.builder = builder = pygubu.Builder()

        #2: Load an ui file
        builder.add_from_file('cryologger.ui')

        #3: Create the widget using a master as parent
        self.mainwindow = builder.get_object('mainwindow', master)

        callbacks = {
            'joinlogs': self.joinlogs,
            'isdate': self.isdate,
            'plot': self.plot
        }

        builder.connect_callbacks(callbacks)

        self.startdate = self.builder.get_object('startdate')
        self.enddate = self.builder.get_object('enddate')
        self.loglocation = self.builder.get_object('loglocation')
        self.plotbutton = self.builder.get_object('plotbutton')
        self.listaxis1 = self.builder.get_object('listaxis1')
        self.listaxis2 = self.builder.get_object('listaxis2')
        self.everyentry = self.builder.get_object('everyentry')
        self.gnuform = self.builder.get_object('gnuplotformentry')

        self.g = Gnuplot.Gnuplot(debug=1)
        self.g('set terminal qt')
        self.g('set xdata time')
        self.g('set timefmt "%s"')
        self.g('set format x "%m/%d/%y\\n%H:%M:%S"')

    def joinlogs(self):
        date1 = datetime.strptime(self.startdate.get(), '%d-%m-%Y')
        date2 = datetime.strptime(self.enddate.get(), '%d-%m-%Y')
        self.mylog = concat.joinfiles(date1,date2,self.loglocation.get())
        self.plotbutton.config(state="normal")
        myvars = self.mylog.getAllvars()
        for ss in myvars:
            self.listaxis1.insert(tk.END, ss)
            self.listaxis2.insert(tk.END, ss)


    def plot(self):
        vars1 = [self.listaxis1.get(idx) for idx in self.listaxis1.curselection()]
        vars2 = [self.listaxis2.get(idx) for idx in self.listaxis2.curselection()]
        print(vars1,vars2)

        axis1cols = []
        axis2cols = []
        for myvar in vars1:
            axis1cols.append(self.mylog.getFileCol(myvar))
        for myvar in vars2:
            axis2cols.append(self.mylog.getFileCol(myvar))

        first = True
        myform = self.gnuform.get()
        every = int(self.everyentry.get())
        self.g("set autoscale y")
        self.g("set autoscale y2")
        self.g("set xlabel 'Time'")
        try:
            s = vars1[0]
            axistitle = s[s.find("(")+1:s.find(")")]
            self.g('set ylabel "%s"' % axistitle)
        except:
            pass
        try:
            s = vars2[0]
            axistitle = s[s.find("(")+1:s.find(")")]
            self.g('set y2label "%s"' % axistitle)
        except:
            pass
        self.g("set y2tics")
        for (myfile,col),title in zip(axis1cols,vars1):
            if first:
                self.g("plot '%s' every %d u 1:%d w %s axes x1y1 title '%s'" % (myfile,every,col,myform,title))
                first = False
            else:
                self.g("replot '%s' every %d u 1:%d w %s axes x1y1 title '%s'" % (myfile,every,col,myform,title))
        for (myfile,col),title in zip(axis2cols,vars2):
            if first:
                self.g("plot '%s' every %d u 1:%d w %s axes x1y2 title '%s'" % (myfile,every,col,myform,title))
                first = False
            else:
                self.g("replot '%s' every %d u 1:%d w %s axes x1y2 title '%s'" % (myfile,every,col,myform,title))
#        if not first:
#            self.g("replot")

        
                    

#        self.g('set xrange [-2:2]')
#        self.g("plot '%s' every 10 u 1:2 w lp" % self.mylog.ffT)
        pass

    def isdate(self):
#        print(type(entry))
        print(self.startdate.get())
        return True

if __name__ == '__main__':
    root = tk.Tk()
    root.wm_title("Cryologger")
    app = Application(root)
    root.mainloop()

