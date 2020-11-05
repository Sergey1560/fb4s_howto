#!/usr/bin/python

import serial
import io
import re

I_MAX=10
J_MAX=10

ser = serial.Serial(            
    port='/dev/ttyUSB0',
    baudrate = 115200,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=1
)

ser.write("M420 V T1\n".encode())

resp=""
get_ok = False

i=I_MAX-1
j=J_MAX-1

mesh_data = [[0] * I_MAX for i in range(J_MAX)]

while not get_ok:
    while ser.in_waiting > 0:
        data = ser.read()
        if data == b'\n':
            if re.match(r'^[-,\d]',resp):
                x = resp.split()
                mesh_data[i]=x
                i=i-1
            else:
                print(resp)
            
            if re.match(r'^ok\sP\d+\sB\d+.*',resp):
                get_ok = True
                break
            resp=""
        else:
            resp = resp + str(data,'utf-8')

ser.close()

for i in range(I_MAX):
    for j in range(J_MAX):
        print("M421 I",i," J",j," Z",mesh_data[j][i],sep='')