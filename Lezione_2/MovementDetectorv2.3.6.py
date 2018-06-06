'''
        Detect movements.
		USAGE: python MovementDetector.py
'''
import smbus			#import SMBus module of I2C
import time         
import collections
import numpy as np
import csv
import sys
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import config
import socket


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

LenFifo = config.LenFifo
Athr = config.Athr
tCycle = config.tCycle
tDelay = config.tDelay
ricorrenze = config.ricorrenze
sogliaRic = config.sogliaRic
minMovRec = config.minMovRec

AxFifo = collections.deque(LenFifo*[0], LenFifo)
AyFifo = collections.deque(LenFifo*[0], LenFifo)
AzFifo = collections.deque(LenFifo*[0], LenFifo)
GxFifo = collections.deque(LenFifo*[0], LenFifo)
GyFifo = collections.deque(LenFifo*[0], LenFifo)
GzFifo = collections.deque(LenFifo*[0], LenFifo)
MvFifo = collections.deque(LenFifo*[0], LenFifo)

#Model training
print 'Training AI model'
n_col = LenFifo * 6 
train_data = pd.read_csv('movements.csv', index_col=0, header=None)
X_train = train_data.iloc[:,0:n_col].values
y_train = train_data.iloc[:,n_col].values

algorithm = RandomForestClassifier(n_estimators=100, random_state=0) #max_depth=10,
algorithm.fit(X_train, y_train)
print 'AI model trained'
print "Inizio client"


host = '192.168.1.192'
port = 1026
countGen = 0

while True:
    #sock.bind((host, port))
    #sock.listen(1)

    #c, add = sock.accept()
    count = 0
    volte = 0 
    while True:
        #print 'Reading Data of Gyroscope and Accelerometer'
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
            count += 1
            countGen += 1
            X = np.array(list(AxFifo) + list(AyFifo) + list(AzFifo) + list(GxFifo) + list(GyFifo) + list(GzFifo)).reshape(-1,n_col)
            y_predict = algorithm.predict(X)
            predict_proba = algorithm.predict_proba(X)
            print y_predict
		    #print ('Detected movement %d, probabilities :' % y_predict) + str(predict_proba)
            MvFifo.append(y_predict)
            if (count > minMovRec) and (countGen > LenFifo):
                #print str(MvFifo[LenFifo - 1]) 
                for x in MvFifo:
                    v = x[0] - 1
                    #print v
                    #print ricorrenze
                    ricorrenze[v] += 1
                        
                massimo = max(ricorrenze)
                numMax = ricorrenze.index(massimo)
                if numMax != 5 and massimo >= sogliaRic:
                    toSend = (ricorrenze.index(massimo)) + 1
                    print toSend
                    sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)    
                    sock.connect((host, port))
                    sock.send(str(toSend))
                    count = 0
                    for i,r in enumerate(ricorrenze):
                        ricorrenze[i] = 0
                    sock.close()
                    time.sleep(tDelay)

                '''else:
                    print "999"
                    c.send("999") '''
                
	    time.sleep(tCycle)
close(csvfile)