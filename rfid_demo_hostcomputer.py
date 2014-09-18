
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

import serial


def main():
	serOutput = serial.Serial()
	try:
		serOutput = serial.Serial("/dev/cu.PL2303-00001014", baudrate=115200, timeout=3.0)
		if(serOutput.isOpen()):
			serOutput.close()
		serOutput.open()
		serOutput.flushInput()
		serOutput.flushOutput()
	except:
		print("unable to connect to main serial port, oops")

	while(True):
		if(serOutput.inWaiting() > 2):
			line = serOutput.readline()
			mylist = line.split(' ')
			print(mylist)


if __name__ == '__main__':

    main()