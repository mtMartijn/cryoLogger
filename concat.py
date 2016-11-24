import datetime
import os
import sys
import os.path

class bfdata:
    def __init__(self,dt1,dt2,ffT,ffP):

        self.ffT = os.path.normpath(ffT)
        self.ffP = os.path.normpath(ffP)
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
        


class tritondata:
    def __init__(self,dt1,dt2,ff):

        self.ff = os.path.normpath(ff)
        outfile = open(ff,"r")
        varline = outfile.readline()
        self.variables = varline[1:].split(", ")
        self.nn = 0
        for i,l in enumerate(outfile):
            self.nn = i+1
        outfile.close()
        print('Number of points: ',self.nn)
        self.dt1 = dt1
        self.dt2 = dt2

    def getrealstart(self): #Gets the datetime for the first point in the file
        with open(self.ff) as fp:
            fp.readline()
            mystr = fp.readline()
            mystr = mystr.split(", ")[0]
            ts = int(mystr)
            mydt = datetime.datetime.fromtimestamp(ts)
        return mydt

    def getvars(self):
        with open(self.ff,'r') as myfile:
            varline = myfile.readline()
            varline = varline.strip().strip('#')
            varline = varline.split(', ')
            return varline
    def getFileCol(self,variable):
        try:
            idx = self.getvars().index(variable)
            return (self.ff,idx+1) #add 1 for Gnuplot index conventions
        except:
            print('Variable not found')
            
    def getAllvars(self):
        return self.getvars()
        

def joinfiles(datetime1,datetime2,location = "",type="Triton",force=0):
    if(datetime1 > datetime2): #Check that datetime1 is earlier than datetime2 and correct if necessary
        datetime1, datetime2 = datetime2, datetime1

    #Create folder for joined logs if it doesn't exist
    #Will be a subfolder of the main script location (I hope...)
    logfoldername = location + '/joinedlogs'
    logfoldername = os.path.abspath(logfoldername) #convert to absolute path
    location = os.path.normpath(location)
    #Create the datafile
    if not os.path.exists(logfoldername):  #Checks concatenated log folder existance and creates it if it doesn't exist
        os.makedirs(logfoldername)

    if type == "BF":
        mydata = BFjoinfiles(datetime1,datetime2,location,logfoldername,force)
    elif type == "Triton":
        mydata = Tritonjoinfiles(datetime1,datetime2,location,logfoldername,force)
    return mydata


def Tritonjoinfiles(datetime1,datetime2,location,logfoldername,force):
    filename = os.path.join(logfoldername, 'Triton' + datetime1.strftime("%y%m%d_") + datetime2.strftime("%y%m%d") + '.T.log')
    if force==0: #if force is set to 0, check if logs are already concatenated and read variable line
        if os.path.isfile(filename):
            print("Files for dates " + datetime1.strftime("%y-%m-%d") + ' to ' + datetime2.strftime("%y-%m-%d") + ' already exist')
            mydata = tritondata(datetime1,datetime2,filename)
            return mydata
      
    print("Starting complete logfile generation for dates " + datetime1.strftime("%y-%m-%d") + ' to ' + datetime2.strftime("%y-%m-%d") + '...')


    td = datetime2.date()-datetime1.date()
    td = td.days
    date_list = [datetime1.date() + datetime.timedelta(days=x) for x in range(0, td+1)]

    outfile = open(filename,'w')
    for ii,mydate in enumerate(date_list):
        dirname = mydate.strftime("%Y-%m-%d")
        try:
            ff = open(os.path.normpath(location + '/' + dirname+'/log_' + dirname + '.dat'),'r')
        except FileNotFoundError as err:
            print('Could not open log for date ' + dirname + ': {0}'.format(err))
            continue
        if ii==0:
            varline = ff.readline()
            outfile.write(varline + '\n')
            vars = varline.strip('\n').strip('# ')
            vars = vars.split(', ')
            print(vars)
        for line in ff:
            outfile.write(line)
        ff.close()
    outfile.close()

    mydata = tritondata(datetime1,datetime2,filename)

    return mydata
    pass
    
    
def BFjoinfiles(datetime1,datetime2,location,logfoldername,force):
    
    filenameT = os.path.join(logfoldername, 'BF' + datetime1.strftime("%y%m%d_") + datetime2.strftime("%y%m%d") + '.T.log')
    filenameP = os.path.join(logfoldername, 'BF' + datetime1.strftime("%y%m%d_") + datetime2.strftime("%y%m%d") + '.P.log')

    #Check if logs are already concatenated and read variable line
    if force==0:
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
                flist.append(open(os.path.normpath(location + '/' + dirname+'/'+fn + ' ' + dirname + '.log'),'r'))
        except FileNotFoundError as err:
            print('Could not open T in date ' + dirname + ': {0}'.format(err))
            continue
        for lines in zip(*flist):
            line = lines[0].strip()
            line = line.split(',')
            line = line[0] + ' ' + line[1]
            mydatetime = datetime.datetime.strptime(line,'%d-%m-%y %H:%M:%S')
            t = mydatetime.replace(tzinfo=datetime.timezone.utc).timestamp() #To correct for the fact that we are not in UTC time zone
            # Could produce strange results when DST is applied (an hour of repeated or missing time stamps).
            outfile.write(str(t))
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
            fileP = open(os.path.normpath(location + '/' + dirname+'/'+ 'Maxigauge' + ' ' + dirname + '.log'),'r')
        except FileNotFoundError as err:
            print('Could not open P in date ' + dirname + ': {0}'.format(err))
            continue
        for line in fileP:
            line = line.strip()
            line = line.split(',')
            mydatetime = datetime.datetime.strptime(line[0] + ' ' + line[1],'%d-%m-%y %H:%M:%S')
            t = mydatetime.replace(tzinfo=datetime.timezone.utc).timestamp() #To correct for the fact that we are not in UTC time zone
            # Could produce strange results when DST is applied (an hour of repeated or missing time stamps).
            outfile.write(str(t))
            dataline = [float(x) for x in line[5::6] ]
            for x in dataline:
                outfile.write(', %.2e' % x)
            outfile.write('\n')
        fileP.close()
    outfile.close()

    mydata = bfdata(datetime1,datetime2,filenameT,filenameP)

    return mydata
