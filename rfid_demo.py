 #-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      dhpollock
#
# Created:     09/06/2014
# Copyright:   (c) dhpollock 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import serial;
import time;
from multiprocessing import Process, Queue
import threading
import random

class RFIDUnit:


    def __init__(self, comPort, antennaNum):
        self.ser = serial.Serial()
        self.tags = []
        self.tags = [0] * antennaNum
        self.comPort = comPort
        try:
##            self.ser = serial.Serial(int(comPort))  # open first serial port
            self.ser.baudrate = 115200
            self.ser.port = comPort
            if(self.ser.isOpen()):
                self.ser.close()
            self.ser.open()
            self.ser.flushInput()
            self.ser.flushOutput()

            if(self.ping() != 0):
                print("Bad Serial. Connect try reconnect")
                #self.reconnect()

        except serial.SerialException, e:
            print("Error:Serial Error-> ")
            print(e)
            print(comPort)

        if(self.ser.isOpen()):
            print("Connected to Port %s!" % comPort)
        else:
            print("Not Connected")

    def reconnect(self):
        if(self.ping() != 0):
            try:
                self.ser.flushInput()
                self.ser.flushOutput()
                self.ser.flush
                self.ser.close()
                time.sleep(.25)
                self.ser.port = self.comPort
                self.ser.baudrate = 115200
                self.ser.open()
                self.ser.flushInput()
                self.ser.flushOutput()
                if(self.ping() != 0):
                    self.reconnect()
            except serial.SerialException, e:
                print(e)
        else:
            self.reset()

    def ping(self):
        self.ser.write("\x30".encode("utf-8"))
        s = (self.ser.read(self.ser.inWaiting()))
        time.sleep(.05)
        while(len(s) > 0):
            time.sleep(.01)
            s = (self.ser.read(self.ser.inWaiting()))

        ping = "\x30\x31\x30\x38\x30\x30\x30\x33\x30\x34\x46\x46\x30\x30\x30\x30"
        self.ser.flushInput()
        self.ser.flushOutput()
        s = (self.ser.read(self.ser.inWaiting()))
        try:
            self.ser.write(ping.encode("utf-8"))      # write a string
        except serial.SerialException, e:
            print("Error: Could not send ping:")
            print(e)
        time.sleep(.05)
        s = (self.ser.read(self.ser.inWaiting()))

##        print(s)

        if(len(s) < 3):
            return 1

        loc1 = s.find("DLP-RFID")
        loc2 = s.find("TRF7960 EVM")

        if(loc1 == -1 and loc2 == -1):
            return 1

        self.ser.flushInput()
        self.ser.flushOutput()

        return 0

    def beep(self):
        beep = "\x30\x31\x30\x39\x30\x30\x30\x33\x30\x34\x37\x37\x46\x30\x30\x30\x30\x30"
        self.ser.flushInput()
        self.ser.flushOutput()
        try:
            self.ser.write(beep.encode("utf-8"))      # write a string
        except serial.SerialException, e:
            print("Error: Could not send beep:")
            print(e)
        time.sleep(.05)
        s = (self.ser.read(self.ser.inWaiting()))
##        print(s)
##        print(":".join("{:02x}".format(ord(c)) for c in s))

##        time.sleep(.05)
##        self.ser.close()


    def failBeep(self):
        failbeep = "\x30\x31\x30\x39\x30\x30\x30\x33\x30\x34\x37\x39\x46\x30\x30\x30\x30\x30"
        self.ser.flushInput()
        self.ser.flushOutput()

        self.ser.write(failbeep.encode("utf-8"))      # write a string
        time.sleep(.05)
        s = (self.ser.read(self.ser.inWaiting()))
##        print(":".join("{:02x}".format(ord(c)) for c in s))

##        time.sleep(.05)
##        self.ser.close()

    def readAllThreaded(self, q):
        threading.Thread(target = self.readAll, args = (q,)).start()

    def readAll(self, q):
##        self.readTagID(1)
        for i in range(len(self.tags)):
            self.tags[i] = self.readTagID(i)

##        return self.tags
        q.put(self.tags)



    def readTagID(self, tagIndex):

        self.SendRegwrtreq(0)
        self.SendAgcToggle()
        self.SendAmPmToggle()


##        readTag = "\x30\x31\x30\x39\x30\x30\x30\x33\x30\x34\x32\x32\x46\x30\x30\x30\x30\x30"
        readData = "\x30\x31\x30\x42\x30\x30\x30\x33\x30\x34\x31\x34\x32\x34\x30\x31\x30\x30\x30\x30\x30\x30"

        self.activateRelay(tagIndex)
        self.ser.flushInput()
        self.ser.flushOutput()

        self.ser.write(readData.encode("utf-8"))
        time.sleep(.05)
        s = ""
        # end =False
        # self.ser.timeout = 1
        # print("reading:  ")
        # while(self.ser.inWaiting() > 0):
        #     self.temp = ""
        #     if(self.ser.inWaiting() > 0):
        #         try:
        #             self.temp = self.ser.read(self.ser.inWaiting())
        #         except serial.SerialTimeoutException, e:
        #             end = True
        #             print s
        #             break
            
        #     s += self.temp

        #     if "]" in s:
        #         print("found a ]")
        #         end = True
        #         break

        #     time.sleep(2)
        #     print("looping")


        # print(s)
        # print("end")
        # self.ser.timeout = 1
        s =self.ser.read(self.ser.inWaiting())
        print(s)
##        print(s)
        split = s.split('\r\n')

        id = ""
        idStart = False
        error = False
        if(len(split) >= 3  and split[2] != ''):
            if(split[2][0] == "8" and split[2][1] == "0" and split[2][2] == "T"):
                for i in range(len(split[2])):
                    if(split[2][i] == "]"):
                        idStart = False

                    if(idStart):
                        id = id + split[2][i]
                    if(split[2][i] == "["):
                        idStart = True
                tag=id.split(',')
                if(len(tag[0]) < 15 and tag[1] != '40'):
                    error = True
            else:
                error = True
        else:
            error = True


##        if(error):
##            return "ReadError"
        self.ser.flushInput()
        self.ser.flushOutput()
        if(error):
            self.reconnect()
            time.sleep(.05)
            self.reset()
            time.sleep(.05)
            return self.readTagID(tagIndex)
        else:
            return id

    def activateRelay(self,num):
        msg1 = "\x30\x31\x30\x39\x30\x30\x30\x33\x30\x34"

        if(num ==0):
            msg2 = "\x32\x32\x46\x30"
        elif(num==1):
            msg2 = "\x32\x33\x46\x30"
        elif(num == 2):
            msg2 = "\x32\x34\x46\x30"
        elif(num == 3):
            msg2 = "\x32\x35\x46\x30"
        elif(num == 4):
            msg2 = "\x32\x36\x46\x30"
        elif(num == 5):
            msg2 = "\x32\x37\x46\x30"
        elif(num == 6):
            msg2 = "\x32\x38\x46\x30"
        elif(num == 7):
            msg2 = "\x32\x39\x46\x30"

        msg3 = "\x30\x30\x30\x30"

        finalMsg = msg1+msg2+msg3

        self.ser.flushInput()
        self.ser.flushOutput()
        self.ser.write(finalMsg.encode("utf-8"))

        time.sleep(.05)
        s =self.ser.read(self.ser.inWaiting())

    def reset(self):
        msg = "\x30\x31\x30\x41\x30\x30\x30\x33\x30\x34\x31\x30\x30\x30\x30\x31\x30\x30\x30\x30"
        self.ser.write(msg.encode("utf-8"))
        time.sleep(.05)
        self.ser.read(self.ser.inWaiting())


    def SendRegwrtreq(self,mode):
        msg1 = "\x30\x31\x30\x43\x30\x30\x30\x33\x30\x34\x31\x30\x30\x30\x32\x31\x30\x31\x30"

        if(mode ==0):
            msg2 = "\x30"
        elif(mode==1):
            msg2 = "\x32"

        msg3 = "\x30\x30\x30\x30"

        finalMsg = msg1+msg2+msg3

        self.ser.write(finalMsg.encode("utf-8"))
        time.sleep(.05)
        self.ser.read(self.ser.inWaiting())


    def SendAgcToggle(self):
        msg = "\x30\x31\x30\x39\x30\x30\x30\x33\x30\x34\x46\x30\x30\x30\x30\x30\x30\x30"
        self.ser.write(msg.encode("utf-8"))
        time.sleep(.05)
        self.ser.read(self.ser.inWaiting())


    def SendAmPmToggle(self):
        msg = "\x30\x31\x30\x39\x30\x30\x30\x33\x30\x34\x46\x31\x46\x46\x30\x30\x30\x30"
        self.ser.write(msg.encode("utf-8"))
        time.sleep(.05)
        self.ser.read(self.ser.inWaiting())


    def close(self):
        try:
            self.ser.close()
        except serial.SerialException, e:
            print("Did not close:")
            print(e)


class TangibleBoard:



    def __init__(self, unitOneComPort, unitTwoComPort, unitThreeComPort):

        self.blockTableFile =  'blockTableData.csv'

        self.unitOne = -1
        self.unitTwo = -1
        self.unitThree = -1

        self.blockTable = {}

        self.units = []

        self.loadBlockTable(self.blockTableFile, self.blockTable)

        self.tag1 = Queue()
        self.tag2 = Queue()
        self.tag3 = Queue()

        self.myQueues = []

        if(unitOneComPort != -1):
            self.unitOne = RFIDUnit(unitOneComPort,4)
            self.units.append(self.unitOne)
            self.myQueues.append(self.tag1)
        if(unitTwoComPort != -1):
            self.unitTwo = RFIDUnit(unitTwoComPort,4)
            self.units.append(self.unitTwo)
            self.myQueues.append(self.tag2)
        if(unitThreeComPort != -1):
            self.unitThree = RFIDUnit(unitThreeComPort)
            self.units.append(self.unitThree)
            self.myQueues.append(self.tag3)


    def boardBeep(self):
        for unit in self.units:
            unit.beep()
            time.sleep(.5)

    def readTags(self,num):
        i = 0
        while(i<num):
##            self.unitOne.readAll(self.tag1)
##            self.unitTwo.readAll(self.tag2)

            for i in range(len(self.units)):
                self.units[i].readAllThreaded(self.myQueues[i])

            
            tempTags = []
            for queue in self.myQueues:
                tempTags += queue.get()
            print(tempTags)
            print("\n")
            i = i+1



    def close(self):
        for unit in self.units:
            unit.close()

    def reconnect(self):
        for unit in self.units:
            unit.reconnect()


    def addBlock(self):
        tag = self.unitOne.readTagID(0)
        if(len(tag) < 16):
            print("Error: Write slot empty, unable to add block to table")
            return
        else:
            tag = tag[:16]
            print("Select Type of Block to Add:")
            print("-- hop")
            print("-- chirp")
            print("-- eat")
            print("-- left")
            print("-- right")
            print("-- spin")
            print("-- hatch")
            print("-- if")
            print("-- else")
            print("-- end if else")
            print("-- repeat")
            print("-- end repeat")
            selection = raw_input("Type Selection for Block %s" % tag)
            if(selection == 'hop' or selection == 'chirp' or selection == 'eat' or selection == 'left' or selection == 'right' or selection == 'spin' or selection == 'hatch' or selection == 'if' or selection == 'else' or selection == 'end if else' or selection == 'repeat' or selection == 'end repeat'):
                self.blockTable[tag] = selection
                self.writeBlockTable()
            else:
                print("Error: Invalid Block Type Selection")

    def readBlocks(self,num):
        i = 0
        while(i<num):
            for i in range(len(self.units)):
                self.units[i].readAllThreaded(self.myQueues[i])

            tags = []
            for queue in self.myQueues:
                tags += queue.get()

            blocks =[]
            j = 0
            for tag in tags:
                if(len(tag) > 15):
                    tagTemp = tag[:16]
                    if(self.blockTable.has_key(tagTemp)):
                        blocks.append(str(self.blockTable[tagTemp]))
                    else:
                        blocks.append("noType")
                else:
                    blocks.append("empty")
                j = j+1

            print(blocks)
            i = i+1



    def writeBlockTable(self):
        with open(self.blockTableFile, "w") as myFile:
            for (key,value) in self.blockTable.items():
                    myFile.write('%s,%s\n' %(key,value))
            myFile.close()

    def loadBlockTable(self, myFileName, myTable):
        myFile = open(myFileName, 'r')

        entries = myFile.read().splitlines()
        myFile.close()

        for line in entries:
            entry = line.split(',')
            myTable[entry[0]] = entry[1]

def main():

    myBoard = None;
    while(True):
        command = raw_input("Command: ")

        if(command == 'connect'):
            myBoard = TangibleBoard("/dev/tty.usbserial-12345678", "/dev/tty.usbserial-4",-1)

        elif(command == 'reconnect'):
            try:
                myBoard.reconnect()
            except:
                print("Error, try connecting to board first")

        elif(command == 'beep'):
            try:
                myBoard.boardBeep()
            except:
                print("Error, try connecting to board first")
        elif(command == 'read'):
            try:
                myBoard.readTags(1)
            except:
                print("Error, try connecting to board first")
        elif(command == 'read50'):
            try:
                myBoard.readTags(50)
            except:
                print("Error, try connecting to board first")

        elif(command == 'add block'):
            try:
                myBoard.addBlock()
            except:
                print("Error, try connecting to board first")
        elif(command == 'read blocks'):
            try:
                myBoard.readBlocks(1)
            except:
                print("Error, try connecting to board first")


        elif(command == 'exit'):
            try:
                myBoard.close()
                break
            except:
                print("Error, try connecting to board first")
                break




if __name__ == '__main__':

    main()


