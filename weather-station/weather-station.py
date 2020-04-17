#!/usr/bin/python2
#
# WeatherPiArduino V2 Test File
# Version 2.0 May 9, 2016
#
# SwitchDoc Labs
# www.switchdoc.com
#
#

# imports

import sys
import time
from datetime import datetime
import random

import config

import subprocess
import RPi.GPIO as GPIO

sys.path.append('RTC_SDL_DS3231')
sys.path.append('Adafruit_Python_BMP')
sys.path.append('Adafruit_Python_GPIO')
sys.path.append('SDL_Pi_WeatherRack')
sys.path.append('SDL_Pi_FRAM')
sys.path.append('Adafruit_ADS1x15')
sys.path.append('RaspberryPi-AS3935/RPi_AS3935')

import SDL_DS3231
import Adafruit_BMP.BMP280 as BMP280
import SDL_Pi_WeatherRack as SDL_Pi_WeatherRack

import SDL_Pi_FRAM
from RPi_AS3935 import RPi_AS3935

################
# Device Present State Variables
###############

config.AS3935_Present = False
config.DS3231_Present = False
config.BMP280_Present = False
config.FRAM_Present = False
config.HTU21DF_Present = False
config.AM2315_Present = False
config.ADS1015_Present = False
config.ADS1115_Present = False


def returnStatusLine(device, state):

	returnString = device
	if (state == True):
		returnString = returnString + ":   \t\tPresent"
	else:
		returnString = returnString + ":   \t\tNot Present"
	return returnString


###############df

#WeatherRack Weather Sensors
#
# GPIO Numbering Mode GPIO.BCM
#

anemometerPin = 26
rainPin = 21

# constants

SDL_MODE_INTERNAL_AD = 0
SDL_MODE_I2C_ADS1015 = 1    # internally, the library checks for ADS1115 or ADS1015 if found

#sample mode means return immediately.  THe wind speed is averaged at sampleTime or when you ask, whichever is longer
SDL_MODE_SAMPLE = 0
#Delay mode means to wait for sampleTime and the average after that time.
SDL_MODE_DELAY = 1

weatherStation = SDL_Pi_WeatherRack.SDL_Pi_WeatherRack(anemometerPin, rainPin, 0,0, SDL_MODE_I2C_ADS1015)

weatherStation.setWindMode(SDL_MODE_SAMPLE, 5.0)
#weatherStation.setWindMode(SDL_MODE_DELAY, 5.0)


################

# DS3231/AT24C32 Setup
filename = time.strftime("%Y-%m-%d%H:%M:%SRTCTest") + ".txt"
starttime = datetime.utcnow()

ds3231 = SDL_DS3231.SDL_DS3231(1, 0x68)


try:

	#comment out the next line after the clock has been initialized
	ds3231.write_now()
	# print "DS3231=\t\t%s" % ds3231.read_datetime()
	config.DS3231_Present = True
except IOError as e:
	#    print "I/O error({0}): {1}".format(e.errno, e.strerror)
	config.DS3231_Present = False


################

# BMP280 Setup

try:
	bmp280 = BMP280.BMP280()
	config.BMP280_Present = True

except IOError as e:

	#    print "I/O error({0}): {1}".format(e.errno, e.strerror)
	config.BMP280_Present = False

################

# HTU21DF Detection
try:
	HTU21DFOut = subprocess.check_output(["htu21dflib/htu21dflib","-l"])
	config.HTU21DF_Present = True
except:
	config.HTU21DF_Present = False


################

# ad3935 Set up Lightning Detector

as3935 = RPi_AS3935(address=0x03, bus=1)

try:

	as3935.set_indoors(True)
	config.AS3935_Present = True

except IOError as e:

    #    print "I/O error({0}): {1}".format(e.errno, e.strerror)
    config.AS3935_Present = False


if (config.AS3935_Present == True):
	as3935.set_noise_floor(0)
	as3935.calibrate(tun_cap=0x0F)

as3935LastInterrupt = 0
as3935LightningCount = 0
as3935LastDistance = 0
as3935LastStatus = ""

def handle_as3935_interrupt(channel):
    time.sleep(0.003)
    global as3935, as3935LastInterrupt, as3935LastDistance, as3935LastStatus
    reason = as3935.get_interrupt()
    as3935LastInterrupt = reason
    if reason == 0x01:
	as3935LastStatus = "Noise Floor too low. Adjusting"
        as3935.raise_noise_floor()
    elif reason == 0x04:
	as3935LastStatus = "Disturber detected - masking"
        as3935.set_mask_disturber(True)
    elif reason == 0x08:
        now = datetime.now().strftime('%H:%M:%S - %Y/%m/%d')
        distance = as3935.get_distance()
	as3935LastDistance = distance
	as3935LastStatus = "Lightning Detected "  + str(distance) + "km away. (%s)" % now



as3935pin = 25

if (config.AS3935_Present == True):
	GPIO.setup(as3935pin, GPIO.IN)
	GPIO.add_event_detect(as3935pin, GPIO.RISING, callback=handle_as3935_interrupt)

###############

# Set up FRAM

fram = SDL_Pi_FRAM.SDL_Pi_FRAM(addr = 0x50)
# FRAM Detection
try:
	fram.read8(0)
	config.FRAM_Present = True
except:
	config.FRAM_Present = False

###############

# Detect AM2315
try:
	from tentacle_pi.AM2315 import AM2315
	try:
		am2315 = AM2315(0x5c,"/dev/i2c-1")
		temperature, humidity, crc_check = am2315.sense()
		# print "AM2315 =", temperature
		config.AM2315_Present = True
	except:
		config.AM2315_Present = False
except:
	config.AM2315_Present = False
	# print "------> See Readme to install tentacle_pi"

# Tests all I2C devices on WeatherPiArduino

# Main Program

#print ""
#print "WeatherPiArduino Demo / Test Version 1.0 - SwitchDoc Labs"
#print ""
#print ""
#print "Program Started at:"+ time.strftime("%Y-%m-%d %H:%M:%S")
#print ""

totalRain = 0

#print "----------------------"
#print returnStatusLine("DS3231",config.DS3231_Present)
#print returnStatusLine("BMP280",config.BMP280_Present)
#print returnStatusLine("FRAM",config.FRAM_Present)
#print returnStatusLine("HTU21DF",config.HTU21DF_Present)
#print returnStatusLine("AM2315",config.AM2315_Present)
#print returnStatusLine("ADS1015",config.ADS1015_Present)
#print returnStatusLine("ADS1115",config.ADS1115_Present)
#print returnStatusLine("AS3935",config.AS3935_Present)
#print "----------------------"

currentWindSpeed = weatherStation.current_wind_speed()/1.852
currentWindGust = weatherStation.get_wind_gust()/1.852

data = '{"wind_velocity":' + str(currentWindSpeed)
data = data + ',"wind_gust":' + str(currentWindGust)

if (config.ADS1015_Present or config.ADS1115_Present):
    windDirection = weatherStation.current_wind_direction()
    windDirectionVoltage = weatherStation.current_wind_direction_voltage()
    data = data + ',"wind_direction":' + str(windDirection)
else:
	data = data + ',"wind_direction":null'

if (config.BMP280_Present):
    temperature_bmp280 = format(bmp280.read_temperature())
    pressure = format(bmp280.read_pressure()/1000)
    altitude = format(bmp280.read_pressure()/1000)
    sealevel_pressure = format(bmp280.read_pressure()/1000)
    data = data + ',"pressure":' + str(pressure)
else:
	data = data + ',"pressure":null'

totalRain = totalRain + weatherStation.get_current_rain_total()
data = data + ',"rain":' + str(totalRain)

if (config.AM2315_Present):
    temperature, humidity, crc_check = am2315.sense()
    data = data + ',"temperature":' + str(temperature) 
    data = data + ',"humidity":' + str(humidity)
else:
	data = data + ',"temperature":null,"humidity":null'

if (config.HTU21DF_Present):
	HTU21DFOut = subprocess.check_output(["htu21dflib/htu21dflib","-l"])
	splitstring = HTU21DFOut.split()
	temperature_htu = float(splitstring[0])
	humidity_htu = float(splitstring[1])

if (config.FRAM_Present):
	for x in range(0,3):
		value = random.randint(0,255)
	fram.write8(x, value)

data = data + '}'

print data
