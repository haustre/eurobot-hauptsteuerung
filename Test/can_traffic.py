__author__ = 'mw'

import socket
import struct
import sys
import time
import random

# CAN frame packing/unpacking (see `struct can_frame` in <linux/can.h>)
can_frame_fmt = "=IB3x8s"

def build_can_frame(can_id, data):
       can_dlc = len(data)
       data = data.ljust(8, b'\x00')
       return struct.pack(can_frame_fmt, can_id, can_dlc, data)

def dissect_can_frame(frame):
       can_id, can_dlc, data = struct.unpack(can_frame_fmt, frame)
       return (can_id, can_dlc, data[:can_dlc])

if len(sys.argv) != 2:
       print('Provide CAN device name (can0, slcan0 etc.)')
       sys.exit(0)
print(sys.argv[1])

# create a raw socket and bind it to the given CAN interface
s = socket.socket(socket.AF_CAN, socket.SOCK_RAW, socket.CAN_RAW)
s.bind((sys.argv[1],))


packer_position = struct.Struct('BHHH')
x = 10000
y = 10000
angle = 18000
count = 0
while True:
    x += random.randrange(-2, 3)
    y += random.randrange(-2, 3)
    angle += random.randrange(-2, 3)
    #x += 1
    #y += 1
    #angle += 2
    try:
        data = packer_position.pack(3, angle, y, x)
        s.send(build_can_frame(0x61F, data))
        data = packer_position.pack(3, angle + 10, y + 100, x + 100)
        s.send(build_can_frame(0x62F, data))
        #print(count)
        print(count)
        count += 1
    except socket.error:
        print('Error1 sending CAN frame')
    time.sleep(1/200)


