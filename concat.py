import datetime
import os
import sys

class bfdata:
    def __init__(self,dt1,dt2,ffT,ffP):

        self.ffT = ffT
        self.ffP = ffP
        outfile = open(ffT,"r")
        varline = outfile.readline()
        self.variablesT = varline[1:].split(", ")
        self.nnT = 0
        for i,l in enumerate(outfile):
            self.nnT = i+1
        outfile.close()
        print('Temperature points: ',self.nnT)

        outfile = open(ffP,"r")
        varline = outfile.readline()
        self.variablesP = varline[1:].split(", ")
        self.nnP = 0
        for i,l in enumerate(outfile):
            self.nnP = i+1
        outfile.close()
        print('Pressure points: ',self.nnP)

        self.dt1 = dt1
        self.dt2 = dt2

    def getrealstart(self): #Gets the datetime for the first point in the file
        with open(self.ffT) as fp:
            fp.readline()
            mystr = fp.readline()
            mystr = mystr.split(", ")[0]
            ts = int(mystr)
            mydt = datetime.datetime.fromtimestamp(ts)
        return mydt

    def getTvars(self):
        with open(self.ffT,'r') as myfile:
            varline = myfile.readline()
            varline = varline.strip().strip('#')
            varline = varline.split(', ')
            return varline
    def getPvars(self):
        with open(self.ffP,'r') as myfile:
            varline = myfile.readline()
            varline = varline.strip().strip('#')
            varline = varline.split(', ')
            return varline
    def getAllvars(self):
        varline = self.getTvars() + self.getPvars()
        print(varline)
        return varline
    def getFileCol(self,variable):
        
        try:
            idx = self.getTvars().index(variable)
            return (self.ffT,idx+1) #add 1 for Gnuplot index conventions
        except:
            try:
                idx = self.getPvars().index(variable)
                return (self.ffP,idx+1) #add 1 for Gnuplot index conventions
            except:
                print('Variable not found')
        

def joinfiles(datetime1,datetime2,location = "",type="BF"):
    if(datetime1 > datetime2): #Check that datetime1 is earlier than datetime2 and correct if necessary
        datetime1, datetime2 = datetime2, datetime1

    #Create folder for joined logs if it doesn't exist
    #Will be a subfolder of the main script location (I hope...)
    logfoldername = 'joinedlogs'
    logfoldername = os.path.abspath(logfoldername) #convert to absolute path
    #Create the datafile
    if not os.path.exists(logfoldername):  #Checks concatenated log folder existance and creates it if it doesn't exist
        os.makedirs(logfoldername)

    if type == "BF":
        mydata = BFjoinfiles(datetime1,datetime2,location,logfoldername)
    return mydata


def BFjoinfiles(datetime1,datetime2,location,logfoldername):
    
    filenameT = os.path.join(logfoldername, 'BF' + datetime1.strftime("%y%m%d_") + datetime2.strftime("%y%m%d") + '.T.log')
    filenameP = os.path.join(logfoldername, 'BF' + datetime1.strftime("%y%m%d_") + datetime2.strftime("%y%m%d") + '.P.log')

    #Check if logs are already concatenated and read variable line
    if os.path.isfile(filenameT) or os.path.isfile(filenameP):
        print("Files for dates " + datetime1.strftime("%y-%m-%d") + ' to ' + datetime2.strftime("%y-%m-%d") + ' already exist')
        mydata = bfdata(datetime1,datetime2,filenameT,filenameP)
        return mydata
    print("Starting complete logfile generation for dates " + datetime1.strftime("%y-%m-%d") + ' to ' + datetime2.strftime("%y-%m-%d") + '...')


    td = datetime2.date()-datetime1.date()
    td = td.days
    date_list = [datetime1.date() + datetime.timedelta(days=x) for x in range(0, td+1)]

    rt = ['R', 'T']
    units = ['Ohm', 'K']
    chs = [1,2,5,6]
    fnames = [('CH%1d %s' % (x,y)) for x in chs for y in rt]
    titlelineT = 'Time (s), ' + ', '.join([('CH%1d %s (%s)' % (x,y,z)) for x in chs for y,z in zip(rt,units)])
    titlelineP = 'Time Maxigauge (s), ' + ', '.join(['Pressure CH%d (mbar)' % x for x in range(1,7)])
    
    outfile = open(filenameT,'w')
    outfile.write("#" + titlelineT + '\n')
    for mydate in date_list:
        dirname = mydate.strftime("%y-%m-%d")
        flist = []
        try:
            for fn in fnames:
                flist.append(open(location + '/' + dirname+'/'+fn + ' ' + dirname + '.log','r'))
        except FileNotFoundError as err:
            print('Could not open T in date ' + dirname + ': {0}'.format(err))
            continue
        for lines in zip(*flist):
            line = lines[0].strip()
            line = line.split(',')
            line = line[0] + ' ' + line[1]
            mydatetime = datetime.datetime.strptime(line,'%d-%m-%y %H:%M:%S')
            outfile.write(mydatetime.strftime('%s'))
            for line in lines:
                line = line.split(',')
                x = float(line[2])
                outfile.write(', %.5e' % x)

            outfile.write('\n')
        for f in flist:
            f.close()
    outfile.close()

    outfile = open(filenameP,'w')
    outfile.write("#" + titlelineP + '\n')
    for mydate in date_list:
        dirname = mydate.strftime("%y-%m-%d")
        try:
            fileP = open(location + '/' + dirname+'/'+ 'Maxigauge' + ' ' + dirname + '.log','r')
        except FileNotFoundError as err:
            print('Could not open P in date ' + dirname + ': {0}'.format(err))
            continue
        for line in fileP:
            line = line.strip()
            line = line.split(',')
            mydatetime = datetime.datetime.strptime(line[0] + ' ' + line[1],'%d-%m-%y %H:%M:%S')
            outfile.write(mydatetime.strftime('%s'))
            dataline = [float(x) for x in line[5::6] ]
            for x in dataline:
                outfile.write(', %.2e' % x)
            outfile.write('\n')
        fileP.close()
    outfile.close()

    mydata = bfdata(datetime1,datetime2,filenameT,filenameP)

    return mydata
