'''
        Record movements.
		USAGE: python mov_rec.py n_of_movement
'''
import smbus			#import SMBus module of I2C
import time         
import collections
import numpy as np
import csv
import sys


#some MPU6050 Registers and their Address
PWR_MGMT_1   = 0x6B
SMPLRT_DIV   = 0x19
CONFIG       = 0x1A
GYRO_CONFIG  = 0x1B
INT_ENABLE   = 0x38
ACCEL_XOUT_H = 0x3B
ACCEL_YOUT_H = 0x3D
ACCEL_ZOUT_H = 0x3F
GYRO_XOUT_H  = 0x43
GYRO_YOUT_H  = 0x45
GYRO_ZOUT_H  = 0x47


def MPU_Init():
	#write to sample rate register
	bus.write_byte_data(Device_Address, SMPLRT_DIV, 7)
	
	#Write to power management register
	bus.write_byte_data(Device_Address, PWR_MGMT_1, 1)
	
	#Write to Configuration register
	bus.write_byte_data(Device_Address, CONFIG, 0)
	
	#Write to Gyro configuration register
	bus.write_byte_data(Device_Address, GYRO_CONFIG, 24)
	
	#Write to interrupt enable register
	bus.write_byte_data(Device_Address, INT_ENABLE, 1)

def read_raw_data(addr):
	#Accelero and Gyro value are 16-bit
        high = bus.read_byte_data(Device_Address, addr)
        low = bus.read_byte_data(Device_Address, addr+1)
    
        #concatenate higher and lower value
        value = ((high << 8) | low)
        
        #to get signed value from mpu6050
        if(value > 32768):
                value = value - 65536
        return value


bus = smbus.SMBus(1) 	# or bus = smbus.SMBus(0) for older version boards
Device_Address = 0x68   # MPU6050 device address

MPU_Init()

print (" Reading Data of Gyroscope and Accelerometer")

LenFifo = 20
Athr = 0.04
AxFifo = collections.deque(LenFifo*[0], LenFifo)
AyFifo = collections.deque(LenFifo*[0], LenFifo)
AzFifo = collections.deque(LenFifo*[0], LenFifo)
GxFifo = collections.deque(LenFifo*[0], LenFifo)
GyFifo = collections.deque(LenFifo*[0], LenFifo)
GzFifo = collections.deque(LenFifo*[0], LenFifo)

csvfile = open('movements.csv', 'ab')
writer = csv.writer(csvfile)

movement_class = sys.argv[1] 
if not(movement_class):
	movement_class = 'UNK'

while True:
	#Read Accelerometer raw value
	acc_x = read_raw_data(ACCEL_XOUT_H)
	acc_y = read_raw_data(ACCEL_YOUT_H)
	acc_z = read_raw_data(ACCEL_ZOUT_H)
	
	#Read Gyroscope raw value
	gyro_x = read_raw_data(GYRO_XOUT_H)
	gyro_y = read_raw_data(GYRO_YOUT_H)
	gyro_z = read_raw_data(GYRO_ZOUT_H)
	
	#Full scale range +/- 250 degree/C as per sensitivity scale factor
	Ax = acc_x/16384.0
	Ay = acc_y/16384.0
	Az = acc_z/16384.0

	Gx = gyro_x/131.0
	Gy = gyro_y/131.0
	Gz = gyro_z/131.0

	AxFifo.append(Ax)
	AyFifo.append(Ay)
	AzFifo.append(Az)
	GxFifo.append(Gx)
	GyFifo.append(Gy)
	GzFifo.append(Gz)

	movement_detected = (np.abs(AxFifo[LenFifo-1]-AxFifo[LenFifo-2])>Athr) | (np.abs(AyFifo[LenFifo-1]-AyFifo[LenFifo-2])>Athr) | (np.abs(AzFifo[LenFifo-1]-AzFifo[LenFifo-2])>Athr)

	if movement_detected:
		#print '%.2f, %.2f, %.2f, %.2f, %.2f, %.2f, %.2f' %(time.time(),Gx,Gy,Gz,Ax,Ay,Az)
		writer.writerow([time.time()] + list(AxFifo) + list(AyFifo) + list(AzFifo) + list(GxFifo) + list(GyFifo) + list(GzFifo) + [movement_class])
	#print 'Gx=%.2f, Gy=%.2f, Gz=%.2f, Ax=%.2f, Ay=%.2f, Az=%.2f' %(Gx,Gy,Gz,Ax,Ay,Az)	
	time.sleep(0.2)

close(csvfile)