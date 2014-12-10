# -*- coding: utf-8 -*-
"""
Created on Thu Nov 20 12:45:23 2014

@author: legitz3
"""

#ACGui is basically just SH102, but the main loop is 
#reformatted as a class function definition, since
#it will be called remotely in the app.exec() of 
#a separate (GUI) application- so now its totally just
#a library

#Serial Handshake 102 is very similar to 101 with
#the following exception: a ReqString is formatted
#and sent to Arduino any time a measurement series
#is requested, and is required for any Arduino
#response other than the original 'r' for entering loop


#a summary of the protocol is below:

''' First we specify and attempt to open the default Arduino serial port 
in Linux (/dev/ttyACM0). Windows should be a COM number, probably COM1
 We do this using the PySerial library, denoted serial. 
 We do this by calling connFunc().
 If the first try in connFunc() throws an error, we wait a few secs and try again.
connFunc() recursively calls connFunc() recursively, up to max tolerance depth #
 connFunc() always returns either a valid pySerial .Serial object, or a -1 for error 
 
 
 
 the Arduino that this program talks with operates in THREE different
 modes.
 
 As soon as it receives power, the Arduino registers a serial connection and 
 enters the local routine sendPing()
 sendPing() is a counting loop in which Arduino writes a string of 'a' concatenated
 with the count one time per second (default)
 
 if the Serial.available() buffer registers a message
  before the connection exceeds max wait count, Arduino sends a 'r' to computer
  to acknowledge receiving its first message and succesfully entering loop()

  
  
  Every python signal also provokes a transmission from Arduino. Arduino sends  
  a comma-parsing result , and if it accepts the python signal as a DATAREQUEST,
  the string 'b', to signal it has entered transmission mode, 
  
  or else 'l' and the default terminator 'x' to end the transaction. 
  
  in transmission mode, it runs an iterative comma-parsing loop, and returns iteration number,
  current string, nextcomma status, and shaved string for next iter loop, each with a reasonable header.
  
  
  
  Once Python has successfully created the serial.Serial object, it waits for the
  "a" + "<int>" from Arduino. If it receives any message its fwds it to stdout, and
  responds by sending
  the byte 'p' to establish first contact.
  
  The p should provoke the 'r' character from Arduino, followed by 'l', t0-t4, and an 'x'.
  Python hangs 20 ms, then checks for a response from Arduino. If it receives none, it will
  retry to garner a response up to a max tolerance specified by the user.
  For each try, it will parse up to (default) 60 bytes from arduino, searching for an 'r' ("charin"
  ) to indicate that Arduino is no longer in Ping mode.
  
  After it exits this 'p' loop (whether it has gotten an 'r' successfully or not), it enters the
  ReadSomeVals() loop, and
  scrolls through the strings it is getting from Arduino
   (with maximum # measurement reads, and max read time specd by user)
   until it gets a 'x' terminator or times out.
 
  Finally Python tries to trigger a measurement series, using the default  'b10,s,1E0r,g'
  which is relayed to stdout
 
  Then calls ReadSomeVals() again (hopefully getting a measurement). then it closes the
  serial.Serial (connection) object.
  
  Each time that ReadSomeVals is called, python enters Single Measurement (datapoint)
  cycle associated with a counter. acquisition of each datapoint continues until
  line terminator '\n' is received. Then python parses numbers and +-*.E, converts to float
  and prints this value to stdout along with a datapoint summary (time, counter etc)
  
  As long as all loop conditions still hold and Arduino hasn't killed the function
  with 'x', ReadSomeVals() just continues taking data.
  

'''
#wait for any message on the specified serial port.
#
#Upon receipt, reply by writing a 'p' back to the serial port,
#and forward the message to stdout and/or console.




from time import sleep
import serial
import time
import datetime as dt
import Queue
import thread
import threading
#small func to recursively handle any failed port connection
#attempts
#- returns connection identifier is successful, -1 if fail

#whole library reimplemented as a class so that its
#methods are externally callable

class ACObject():
    def __init__(self, refnum):
        self.initObj(refnum)
    def initObj(self, refnum):
        print 'ACObject initialized'
        self.refnum=refnum
        self.connStatus='r'
        self.acqStatus='r'
        self.connobject=[]
        
    def connFunc(self, connPort, AppWindow='none', recurs=0, recurmax=20, connected=False):
        print 'connFunc initiated'
        self.killConnStatus=False
        self.AppWindow=AppWindow
    
        #We run the connFunc for Arduino port, which repeats until
        #a valid serial connection is obtained, or attempt times out
        serconn=-1    
        breakloop=False
        while ((recurs < recurmax) and (breakloop==False)):
            #try:
            serconn=serial.Serial(connPort, 115200, timeout=30)
            breakloop=True
            self.connPrintTime=dt.datetime.now()
            self.connStartTime=time.time()
            self.AppWindow.connPrintTime=self.connPrintTime
            self.AppWindow.connStartTime=self.connStartTime
            self.connStatus='o'
            self.AppWindow.connStatuses[self.AppWindow.nowtab]='o'
            self.AppWindow.abstractcolorbutton.click()
            #except:
#                print 'port not found at time ' + str(dt.datetime.now())    
#                sleep(1)
#                recurs=recurs+1
#                serconn=-1
    
    
        #anything besides a valid connection object returns -1
        # so entering this loop means serconn should be 
        #valid pySerial object
        if serconn != -1:
            print 'connFunc returned object !=-1: '
            print (serconn)
            print type(serconn)
            self.connobject=serconn
            #change porticon o to yellow
            self.connStatus='y'
            self.AppWindow.connStatuses[self.AppWindow.nowtab]='y'
            self.AppWindow.abstractcolorbutton.click()
            
    # this is the end of the 'raw' connection handling
    #now, we proceed to first contact initiation w Arduino        

            while not connected:
                    #serInbox=serconn.readline()  
                    #what are the subtleties  of this particular call?
                if serconn.inWaiting()>0:     
                    connected=True
                else:
                    sleep(0.1)
                    
        #this loop should only enter if we have heard anything from Arduino.
        #in short, we try to send a 'p', and read up to first 'x'-term
        #with ReadSomeVals()
            if connected:
                print ('serconn.inWaiting !=Empty. Connected to Arduino')
                #firstMsg=str(serconn.readline())    
                firstMsg=serconn.read(int(serconn.inWaiting()))
                print 'msg type'
                print type(firstMsg)
                print "length="+str(len(firstMsg))
                for cnum, cha in enumerate(firstMsg):
                    print str(cnum)+': ' + cha
                print 'over'
                
                print 'firstMsg'
                print (firstMsg)
                print str(firstMsg)
                print repr(firstMsg)
        
                blankstring=[]
                charin = ''
                charstart='r'
                maxtries=5;
                tries=0;
                started=False
                while (started==False and tries <=maxtries):
                    print "sending 'p' to Arduino: try #"
                    print str(tries+1)
                    serconn.write('p')
                    sleep(0.02)
                    sreads=0
                    nonreads=0
                    newlineMarker=0
                    while (sreads <= 20 and charin !=charstart and started==False):

                        if serconn.inWaiting()<1:
                            nonreads+=1                            
                            if nonreads%1000==0:
                                print 'nonread'
                                print nonreads
                            sleep(.001)
                        else:
                            print 'sr='+str(sreads)
                            charin = serconn.read()
                            sreads+=1
                            blankstring += str(charin)           
                            if sreads%8==0:
                                print 'sreads = ' + str(sreads)
                                print blankstring
                                print '++++++++'
                                sleep(0.001)
                            if charin=='\n':
                                lineString=blankstring[newlineMarker:sreads]
                                self.sendLine( lineString, AppWindow, datamode=False, clock=time.time()-self.connStartTime)
                            if charin == charstart:
                                print 'charstart found! at ' + str(sreads)
                                self.connStatus='g'
                                self.AppWindow.connStatuses[self.AppWindow.nowtab]='g'
                                self.AppWindow.abstractcolorbutton.click()
                                self.sendLine(charin, AppWindow, datamode=False, clock=time.time()-self.connStartTime)
                                started = True
                #send some output each time inner while loop terminates    
                    print 'final blankstring'
                    print blankstring
                    print 'final sreads'
                    print sreads
                    print '+++++'
                    tries+=1
            
                self.maxVals=300
                self.maxtime = 50
                #if we have a successful charstart match, we need to parse the 
                # Arduino non-data to our 'p' counterpings
                if started:
                    self.ReadSomeVals(self.maxVals, self.maxtime, serconn)
                    sleep(.1)
    
    #inner fail (session killed)
            else:
                print 'session killed. exiting connFunc() loop.'
    
    #outer fail (no port connection)
        else:
            print 'port connection failed. try a different dev file or be more patient'
                
                
                
    def ReadSomeVals(self, maxVals, maxtime, serconn, readTerm='x', badmax=40, reptime=0.001):
        print 'Entering ReadSomeVals loop'
        #how many measurement receipts have complete?    
        MeasCount=0
        #how many microseconds have elapsed?
        eltime=0
        #how many errors have been thrown?
        bads=0
        #how many non-availables have been returned
        empties=0
        #start the clock
        t0=time.time()
        #has Arduino sent a measurement termination Byte?
        readTermed=False
        self.datamode=False
        acqYellowed=False
        acqGreened=False
        #loops conditions:
        #MeasCount is number of line returns \n
        #eltime is just timer since RSV() got called
        #bads are attempted reads where connection.read() throws an error (usually due to no data available
        #-- is there a builtin function that checks automatically eg "peek")
        #readTermed is the loop killing response to receipt of an 'x' from Arduino
        while ((MeasCount < maxVals) and (eltime < maxtime) and (bads<badmax) \
         and readTermed==False):
           # ########if serconn.inWaiting()>0:
          #We set our status to Currently Acquiring Measurement Entry 
            readingEntry=True
            #We start each Single Measurement Acquisition (data point) from scratch
            thisEntry="" 
            #used to ensure only a single abstractcolorbutton.click() is called to update
            # Acquisition status            

            #two ways to kill each MeasCount while loop, \n sets readingEntry to false and 'x' nukes
            while (readingEntry==True and readTermed == False):                  
               #get a Byte
                if serconn.inWaiting():

                    try:
                        nextMsg=serconn.read()
                        strnextMsg=str(nextMsg)
                   #record Byte receipt time     
                        nowtime = time.time()
                   #calc elapsed time in sec
                        eltime = (nowtime - t0)
                    #supplant our datapoint character array
                        thisEntry+=strnextMsg
                    # if we receive the 'x' death signal, change our status to lame duck
                        if strnextMsg==readTerm:
                            print( 'read termed by Arduino with signal ' + readTerm)
                            readTermed = True
                            acqYellowed=False
                            acqGreened=False
                            #if we are in an acquisition, then that acquisition is now done
                            if self.AppWindow.acqStatuses[-1] != 'r':
                                print 'final acquisition NParray'
                                print self.AppWindow.NParraylist[-1]
                                print 'calling AcqKill'
                                self.AppWindow.AIDisconnectButton.click()
                                #self.AppWindow.acqStatuses[-1]='b'
                                #self.AppWindow.abstractcolorbutton.click()
                    #if we receive the End Single Measurement status (\n) print the 
                    #full datapoint transcript, and strip to numerical form.
                        if strnextMsg=='\n':
                            print ( str(MeasCount) + ':  ' + thisEntry + '@' + str(eltime))
                            #datapoint = ""                    
                            #for dnum, dchar in enumerate(thisEntry):
                              #  if (dchar.isdigit()) or dchar== ('+' or'-' or '.' or '*' or 'E'):
                             #       datapoint +=dchar
                            #datapoint=float(datapoint)                    
                            #print datapoint
                            print '--------------'
                        #here, we always want to look for a datamode flag, to pass to sendLine
                            #this decision tree will need updating
                            #if MeasCount==0:
                            if not acqYellowed:
                               if thisEntry[0]=='b':
                                   acqYellowed=True
                                   self.AppWindow.acqStatuses[-1]='y'
                                   self.AppWindow.abstractcolorbutton.click()
                                   #self.datamode=True
                            if acqGreened:
                                #Arduino line header byte for datapoint
                                if thisEntry[0]=='z':
                                    self.datamode=True
                            if not acqGreened:
                                #print 'not acqGreened'
                                #Arduino bytecode for commence datastream
                                if thisEntry[0]=='y':
                                    print 'y found! acqGreened->True'
                                    self.AppWindow.acqStatuses[-1]='g'
                                    self.AppWindow.abstractcolorbutton.click()
                                    acqGreened=True
                                #else:
                                    #print thisEntry[0]+ "!='y'"
                            #print 'rsv sendline info: '
                            #print 'acqGreened: ' + str(acqGreened)
                            #print 'thisEntry[0]='+thisEntry[0]
                            #print 'rsv-datamode: ' + str(self.datamode)
                            if self.datamode:
                                self.sendLine(thisEntry, self.AppWindow, datamode=True, clock=time.time()-self.DataStartTime)
                            else:
                                self.sendLine(thisEntry, self.AppWindow, datamode=False, clock=time.time()-self.connStartTime)                            
                            
                            thisEntry=""
                            readingEntry = False  
                            self.datamode=False
                            MeasCount +=1
                        sleep(0.001)
                #except should be obsolete, given else loop below
                    except:
                        print 'ReadSomeVals: no data available to read from serconn'
                        bads+=1            
                        print ("bads= " + str(bads))
                        readingEntry=False
                        sleep(reptime)
                else:   
                    empties+=1
                    if empties%1000 == 0:
                        print 'empties: ' + str(empties)
                    readingEntry=False
                    sleep(reptime)                        
    
    ###at the Very end of ReadSomeVals, we would like Arduino to resend the original
    #  ReqString it received from Python to initiate the loop. 
    #This will be printed to stdout for debugging / design&construction 
    
    
    def sendLine( self, thisline, AppWindow, datamode=False, clock='manual', msgCount=''):
        #error handling        
        if AppWindow=='none':
            print 'no Window specified to send data line to'
            print "dataline was: "
            print thisline
            if datamode:
                print 'd'
                
            else:
                print 'l'
        #end error handling
        else:
            
            if datamode:
                formdline=str(clock)+ ';' + str(thisline).lstrip('z')
                #remember, this whole function is part of a distinct
                #thread
                #AppWindow.ModeList.append('d')
                AppWindow.dqlock.acquire()
                AppWindow.dqueue.put(formdline)
                AppWindow.dqlock.release()
            else:
                formdline=str(clock)+ '\t' + str(thisline)
                #AppWindow.ModeList.append('l')
                #formdline=str(msgCount)+'\t'+str(clock)+ '\t' + str(thisline)
                
                AppWindow.lqlock.acquire()
                AppWindow.lqueue.put(formdline)
                AppWindow.lqlock.release()
                
            AppWindow.LineList.append(thisline)
            #probs comment out soon
            print 'sent line to AppWindow'
            print thisline
            print ('datamode? ' + str(datamode))
            
                
               ########################### 
                
    #begin main executable here
    #reimplemented as a callable method for ACGui
    #is qtApp necessary as an arg here, or can we just
    #get the self.AppWindow property??
    def reqAcqData(self, reqString, qtApp):            
        print 'ACGuiLib.reqAcq data called, sending reqString to Arduino'

        self.connobject.write(reqString)
        self.DataStartTime=time.time()
        self.ReadSomeVals(self.maxVals, self.maxtime, self.connobject)
        
    
    
    #initial connection stuff has all been moved to connFunc
    #for implementation as a callable library from ComAppWindow
    
    #this function now runs the actual data acquisition, ie
    #accepts a 'sendString' as input, and alters ComAppWindow 
    #state variables until it gets a 'x'
               
        #however, the "connected" var refers to whether or not
        # we have received some kind of signal from Arduino
        #--- which is not necessarily the same thing as 
        #accessing the proper serial port    
    
                #print 'commence python write firstMsg'
                #serconn.write(str(firstMsg))
                #print 'complete python write firstMsg'
                
                #need to add reqString constructor here
                #burst/cont+burstsize, sendClock, timeCoef E timeSig, 'g' for GO
            
            
    #good code        
    #        reqString = 'b10,s,1E0r,g'
    #            print 'commence python write reqString' + reqString
    #            serconn.write(reqString)
    #            ReadSomeVals(maxVals, maxtime, serconn)
    #            serconn.close()
 

   
#        else:
#            print (' while not connected loop terminated without valid connection')
#    
#    #this is if serial connection never gets established
#    else:
#        print 'recursive connection attempts failed'     



            
            