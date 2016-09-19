import datetime
import os
import sys

class bfdata:
    def __init__(self,dt1,dt2,ff,nn,vvars=None):
        self.dt1 = dt1
        self.dt2 = dt2
        self.ff = os.path.abspath(ff)
        self.nn = nn
        if vvars == None:
            self.vvars = tuple()
        else:
            self.vvars = tuple(vvars)
    def getrealstart(self): #Gets the datetime for the first point in the file
        with open(self.ff) as fp:
            fp.readline()
            mystr = fp.readline()
            mystr = mystr.split(", ")[0]
            ts = int(mystr)
            mydt = datetime.datetime.fromtimestamp(ts)
        return mydt
    def getstart(self): #Gets the datetime user specified start
        return self.dt1
    def getend(self): #Gets the datetime user specified end
        return self.dt2
    def Npoints(self): #Gets number of datapoints
        return self.nn
    def filename(self):
        return self.ff #Return filename

def joinfiles(datetime1,datetime2,location = ""):
    if(datetime1 > datetime2): #Check that datetime1 is earlier than datetime2 and correct if necessary
        datetime1, datetime2 = datetime2, datetime1

    #Create folder for joined logs if it doesn't exist
    #Will be a subfolder of the main script location (I hope...)
    logfoldername = 'joinedlogs'
    logfoldername = os.path.abspath(logfoldername) #convert to absolute path
    #Create the datafile
    if not os.path.exists(logfoldername):  #Checks file existance and stops if it already exists
        os.makedirs(logfoldername)
    #base path and filename
    filename = os.path.join(logfoldername, 'BF' + datetime1.strftime("%y%m%d_") + datetime2.strftime("%y%m%d") + '.log')

    #Check if logs are already concatenated and read variable line
    if os.path.isfile(filename):
        print("Files for dates " + datetime1.strftime("%y-%m-%d") + ' to ' + datetime2.strftime("%y-%m-%d") + ' already exist')
        outfile = open(filename,"r")
        varline = outfile.readline()
        for i,l in enumerate(outfile):
            pass
        nn = i+1
        outfile.close()
        variables = varline[1:].split(", ")
        mydata = bfdata(datetime1,datetime2,filename,nn,variables)
        return mydata
    print("Starting complete logfile generation for dates " + datetime1.strftime("%y-%m-%d") + ' to ' + datetime2.strftime("%y-%m-%d") + '...')


    td = datetime2.date()-datetime1.date()
    td = td.days
    date_list = [datetime1.date() + datetime.timedelta(days=x) for x in range(0, td+1)]

    rt = ['R', 'T']
    units = ['Ohm', 'K']
    chs = [1,2,5,6]
    fnames = [('CH%1d %s' % (x,y)) for x in chs for y in rt]
    titleline = 'Time (s), ' + ', '.join([('CH%1d %s (%s)' % (x,y,z)) for x in chs for y,z in zip(rt,units)])
    titlelineMaxi = 'Time Maxigauge (s), ' + ', '.join(['Pressure CH%d (mbar)' % x for x in range(1,7)])
    variables = (titleline + ', ' + titlelineMaxi).split(", ")
    print(variables)
    
    outfile = open(filename,'w')
    outfile.write("#" + titleline + ', ' + titlelineMaxi + '\n')
    nn = 0 #counter for number of points
    for mydate in date_list:
        dirname = mydate.strftime("%y-%m-%d")
        flist = []
        try:
            for fn in fnames:
                flist.append(open(location + '/' + dirname+'/'+fn + ' ' + dirname + '.log','r'))
            flist.append(open(location + '/' + dirname+'/'+ 'Maxigauge' + ' ' + dirname + '.log','r'))
        except FileNotFoundError as err:
            print('Could not open date ' + dirname + ': {0}'.format(err))
        for lines in zip(*flist):
            nn += 1
            line = lines[0].strip()
            line = line.split(',')
            line = line[0] + ' ' + line[1]
            mydatetime = datetime.datetime.strptime(line,'%d-%m-%y %H:%M:%S')
            outfile.write(mydatetime.strftime('%s'))
            for line in lines[:-1]:
                line = line.split(',')
                x = float(line[2])
                outfile.write(', %.5e' % x)

            line = lines[-1].strip()
            line = line.split(',') #maxigauge file
            mydatetime = datetime.datetime.strptime(line[0] + ' ' + line[1],'%d-%m-%y %H:%M:%S')
            outfile.write(', ' + mydatetime.strftime('%s'))
            dataline = [float(x) for x in line[5::6] ]
            for x in dataline:
                outfile.write(', %.2e' % x)
            outfile.write('\n')
        for f in flist:
            f.close()

    print("Total data points:",nn)
    mydata = bfdata(datetime1,datetime2,filename,nn,variables)
    outfile.close()
    return mydata



