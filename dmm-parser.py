#!/usr/bin/env python
#
# -*- coding: utf-8 -*-
#
# @description
# Parses data from a Mastech MS8226
# and MS8226T digital multimeter (DMM)
# Documentation taken from http://rahmyzdhyfbr.tripod.com/
#
# To Do:
#  - Better documentation on the DMM's format
#
# @author: JLH
# @date: Aug 2013

import serial
import glob
import sys
from datetime import datetime
from bitarray import bitarray

# Get any serial port from /dev/
# works in Linux and Mac, should be modified
# for Windows use
def get_serial_port_name():
	names = glob.glob('/dev/tty.usb*') + glob.glob('/dev/ttyUSB*')
	if len(names) == 0:
		print 'No serial port found!'
		sys.exit(1)
	elif len(names) > 1:
		print "%d serial ports found: " % len(names),
		for name in names:
			print name,
		print
	return names[0]

# Gets a name for the serial port (if not specified)
# and creates the serial port
def get_serial_port(name=None):
	if name is None:
		name = get_serial_port_name()
		print "Automatically selecting %s as serial port" % name
	s = serial.Serial(name,
					  baudrate     = 2400,
					  bytesize     = serial.EIGHTBITS,
					  parity       = serial.PARITY_NONE,
					  stopbits     = serial.STOPBITS_ONE,
					  timeout      = 0.23)
	return s

def safe_open(serial_port):
	if serial_port is None:
		return
	if not serial_port.isOpen():
		serial_port.open()

def print_hex(line):
	print "Line (l=%d):" % len(line),
	print ["%02X " % ord(c) for c in line]

def num2binstr(num):
	return ''.join(num & (1 << i) and '1' or '0' for i in range(7,-1,-1))[::-1]

num_dict = {0: ' ', 0x68: 'L', 0x7D: 0, 0x05: 1,0x5B: 2,0x1F: 3,0x27: 4,0x3E: 5,0x7E: 6,0x15: 7,0x7F: 8,0x3F: 9}
# Core function, processes the serial line and converts it to a number
def parse_data(line):
	try:
		if len(line) == 0:
			return
		if len(line) != 14:
			print "Bad line (l=%d)" % len(line)
			return	
		arr = [ord(c) for c in line]
		arr_str = ''.join([num2binstr(n) for n in arr])
		ba = bitarray(arr_str, endian='little')
		ms_dict = {}
		for i in range(0, len(ba), 8):
			pos = ba[i+4:i+8]
			value = ba[i:i+4]
			ms_dict[ord(pos.tobytes())] = value
		first_ba  = ms_dict[3][0:4] + ms_dict[2][0:3]
		second_ba = ms_dict[5][0:4] + ms_dict[4][0:3]
		third_ba  = ms_dict[7][0:4] + ms_dict[6][0:3]
		fourth_ba = ms_dict[9][0:4] + ms_dict[8][0:3]

		# Build the number string
		num_str = ""
		# Check negative sign
		if ms_dict[2][3]:
			num_str = num_str + '-'
		num_str = num_str + str(num_dict[ord(first_ba.tobytes())])
		if ms_dict[4][3] == True:
			num_str = num_str + "."
		num_str = num_str + str(num_dict[ord(second_ba.tobytes())])
		if ms_dict[6][3] == True:
			num_str = num_str + "."
		num_str = num_str + str(num_dict[ord(third_ba.tobytes())])
		if ms_dict[8][3] == True:
			num_str = num_str + "."
		num_str = num_str + str(num_dict[ord(fourth_ba.tobytes())])

		# Build the unit string
		unit_str = ""
		voltage = False
		if ms_dict[10][2]:
			unit_str = unit_str + 'n'
		elif ms_dict[10][1]:
			unit_str = unit_str + 'k'
		elif ms_dict[10][3]:
			unit_str = unit_str + 'u'
		elif ms_dict[11][3]:
			unit_str = unit_str + 'm'
		elif ms_dict[11][1]:
			unit_str = unit_str + 'M'
		if ms_dict[13][2]:
			unit_str = unit_str + 'V'
			voltage = True
		elif ms_dict[13][3]:
			unit_str = unit_str + 'A'
		elif ms_dict[12][2]:
			unit_str = unit_str + 'Ohm'
		elif ms_dict[12][3]:
			unit_str = unit_str + 'F'
		elif ms_dict[14][2]:
			unit_str = unit_str + 'Celcius'
		elif ms_dict[13][1]:
			unit_str = unit_str + 'Hz'
		if voltage:
			if ms_dict[1][2]:
				unit_str = unit_str + ' DC'
			elif ms_dict[1][3]:
				unit_str = unit_str + ' AC'

		# check for the HOLD and REL flags
		if ms_dict[12][0]:
			unit_str = unit_str + ' (HOLD)'
		if ms_dict[12][1]:
			unit_str = unit_str + ' (REL)'

		now = datetime.now()
		timestamp = "[%02d:%02d:%04.1f]" % (now.hour, now.minute, now.second + now.microsecond / 1e6)
		# Print timestamp, number and units
		print timestamp, num_str, unit_str
		# Flush the output so that we can see it in a log
		sys.stdout.flush()
	except Exception, e:
		print "Couldn't parse line"
		print str(e)

def run(serial_port = None, name = None):
	if serial_port == None:
		serial_port = get_serial_port(name=name)
	safe_open(serial_port)
	while True:
		parse_data(serial_port.read(14))

print "Starting Mastech MS8226 DMM parser"
if len(sys.argv) > 1:
    run(name=sys.argv[1])
else:
    run()
serial_port.close()
print "Exiting"
