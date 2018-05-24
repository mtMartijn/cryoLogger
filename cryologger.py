#test.py
import tkinter as tk  # for python 3
import pygubu
from datetime import datetime
import Gnuplot
import time
import concat
import sys
from pygubu.builder import ttkstdwidgets
import configparser
from tkinter import filedialog

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
            'plot': self.plot,
            'gnucommand': self.gnucommand,
            'today_start': self.today_start,
            'today_end': self.today_end,
            'browse_folder': self.browse_folder
        }

        builder.connect_callbacks(callbacks)

        self.startdate = self.builder.get_object('startdate')
        self.enddate = self.builder.get_object('enddate')
        self.loglocation = self.builder.get_object('loglocation')
        self.plotbutton = self.builder.get_object('plotbutton')
        self.browsebutton = self.builder.get_object('browsebutton')
        self.gnurunbutton = self.builder.get_object('gnurunbutton')
        self.listaxis1 = self.builder.get_object('listaxis1')
        self.listaxis2 = self.builder.get_object('listaxis2')
        self.everyentry = self.builder.get_object('everyentry')
        self.gnucommandentry = self.builder.get_object('gnucommandentry')
        self.gnuform = self.builder.get_object('gnuplotformentry')
        self.forcelog = self.builder.get_variable('forcelog')
        self.logtype = self.builder.get_variable('logtype')
        self.usetoday_start = self.builder.get_object('usetoday_start')
        self.usetoday_end = self.builder.get_object('usetoday_end')
        self.usetoday_start_bool = self.builder.get_variable('today_start_bool')
        self.usetoday_end_bool = self.builder.get_variable('today_end_bool')

               
        config = configparser.ConfigParser()
        config.sections()
        config.read('cryologger.ini')
        self.loglocation.delete(0,tk.END)
        self.loglocation.insert(0,config['DEFAULT']['loglocation'])
        self.startdate.delete(0,tk.END)
        self.startdate.insert(0,config['DEFAULT']['startdate'])
        self.enddate.delete(0,tk.END)
        self.enddate.insert(0,config['DEFAULT']['enddate'])
        self.logtype.set(config['DEFAULT']['logtype'])
        self.forcelog.set(int(config['DEFAULT']['forcelog']))
        
        self.g = Gnuplot.Gnuplot(debug=1)
        self.g('set terminal qt')
        self.g('set xdata time')
        self.g('set timefmt "%s"')
        self.g('set format x "%d/%m/%y\\n%H:%M:%S"')

    def today_start(self):
        self.startdate.delete(0,tk.END)
        today = datetime.today()
        self.startdate.insert(0,today.strftime('%d-%m-%y'))
        if self.usetoday_start_bool.get():
            self.startdate.config(state='readonly')
        else:
            self.startdate.config(state='normal')

    def today_end(self):
        self.enddate.delete(0,tk.END)
        today = datetime.today()
        self.enddate.insert(0,today.strftime('%d-%m-%y'))
        if self.usetoday_end_bool.get():
            self.enddate.config(state='readonly')
        else:
            self.enddate.config(state='normal')

    def joinlogs(self):
        try:
            date1 = datetime.strptime(self.startdate.get(), '%d-%m-%Y')
        except ValueError:
            date1 = datetime.strptime(self.startdate.get(), '%d-%m-%y')
        try:
            date2 = datetime.strptime(self.enddate.get(), '%d-%m-%Y')
        except ValueError:
            date2 = datetime.strptime(self.enddate.get(), '%d-%m-%y')
        self.mylog = concat.joinfiles(date1,date2,self.loglocation.get(),type=self.logtype.get(),force=self.forcelog.get())
        self.plotbutton.config(state="normal")
        self.gnurunbutton.config(state="normal")
        myvars = self.mylog.getAllvars()
        self.listaxis1.delete(0, tk.END)
        self.listaxis2.delete(0, tk.END)
        for ss in myvars:
            self.listaxis1.insert(tk.END, ss)
            self.listaxis2.insert(tk.END, ss)

    def browse_folder(self):
        filename = filedialog.askdirectory()
        #folder_path.set(filename)
        self.loglocation.delete(0,tk.END)
        self.loglocation.insert(0,filename)
        return


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
        self.g('set ytics nomirror')
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
    def gnucommand(self):
        mycomm = str(self.gnucommandentry.get('1.0','end'))
        comlist = mycomm.split('\n')
        for com in comlist:
            self.g(com)
        return
if __name__ == '__main__':
    root = tk.Tk()
    root.wm_title("Cryologger")
    app = Application(root)
    root.mainloop()

