__author__ = 'mw'


import sys
import time
import queue
import math
import threading
from eurobot.libraries import can


class RobotSimulation():
    start_position = (2632, 947)
    start_angle = 2.4821 / (2*math.pi) * 360

    diameter = 73.025
    transmission = 18
    rpm_per_ss = 10000
    rpm_max = 5000
    mm_per_rot = diameter * math.pi / transmission
    accel = mm_per_rot * rpm_per_ss / 60
    speed_max = mm_per_rot * rpm_max / 60

    def __init__(self):
        if len(sys.argv) != 2:
                print('Provide CAN device name (can0, vcan0 etc.)')
                sys.exit(0)
        self.can_socket = can.Can(sys.argv[1], can.MsgSender.Navigation)
        self.robot_position = self.start_position
        self.robot_angle = self.start_angle
        self.drive_thread = threading.Thread(target=self.drive)
        self.drive_thread.setDaemon(1)
        self.clapper_thread = threading.Thread(target=self.clapper)
        self.clapper_thread.setDaemon(1)
        self.stands_thread = threading.Thread(target=self.stands)
        self.stands_thread.setDaemon(1)
        self.popcorn_thread = threading.Thread(target=self.popcorn)
        self.popcorn_thread.setDaemon(1)
        self.start_game()

    def start_game(self):
        self.send_position(self.robot_position, self.robot_angle)
        time.sleep(0.5)
        can_msg = {
            'type': can.MsgTypes.Peripherie_inputs.value,
            'emergency_stop': False,
            'key_inserted': False
        }
        self.can_socket.send(can_msg)
        self.drive_thread.start()
        self.clapper_thread.start()
        self.stands_thread.start()
        self.popcorn_thread.start()
        time.sleep(100)

    def clapper(self):
        clapper_queue = queue.Queue()
        self.can_socket.create_queue(can.MsgTypes.Clapper_Command.value, clapper_queue)
        while True:
            clapper_msg = clapper_queue.get()
            time.sleep(1)
            can_msg = {
                'type': can.MsgTypes.Clapper_Status.value,
                'state': 0,
                'collected_pieces': 1
            }
            self.can_socket.send(can_msg)

    def stands(self):
        collected = 0
        stands_queue = queue.Queue()
        self.can_socket.create_queue(can.MsgTypes.Stands_Command.value, stands_queue)
        while True:
            clapper_msg = stands_queue.get()
            if clapper_msg['command'] == 1:
                collected += 1
            elif clapper_msg['command'] == 3:
                collected = 0
                time.sleep(2)
            can_msg = {
                'type': can.MsgTypes.Stands_Status.value,
                'state': 1,
                'collected_pieces': collected
            }
            self.can_socket.send(can_msg)

    def popcorn(self):
        collected = 0
        popcorn_queue = queue.Queue()
        self.can_socket.create_queue(can.MsgTypes.Popcorn_Command.value, popcorn_queue)
        while True:
            popcorn_msg = popcorn_queue.get()
            if popcorn_msg['command'] == 0:  # collect
                time.sleep(3)
                can_msg = {
                    'type': can.MsgTypes.Popcorn_Status.value,
                    'state': 1,
                    'collected_pieces': collected
                }
                self.can_socket.send(can_msg)
                time.sleep(3)
                collected += 5
            elif popcorn_msg['command'] == 1:
                time.sleep(5)
                collected = 0
            can_msg = {
                'type': can.MsgTypes.Popcorn_Status.value,
                'state': 1,
                'collected_pieces': collected
            }
            self.can_socket.send(can_msg)

    def drive(self):
        goto_queue = queue.Queue()
        self.can_socket.create_queue(can.MsgTypes.Goto_Position.value, goto_queue)
        path_queue = queue.Queue()
        self.can_socket.create_queue(can.MsgTypes.Path.value, path_queue)
        while True:
            goto_msg = goto_queue.get()
            path = []
            for _ in range(goto_msg['path_length']):
                path_msg = path_queue.get()
                path.append(((path_msg['x'], path_msg['y']), path_msg['speed']))
            target_position = goto_msg['x_position'], goto_msg['y_position']
            target_angle = goto_msg['angle']
            speed = goto_msg['speed']
            self.drive_path(path, target_position, speed)

            self.robot_angle = target_angle
            self.send_position(self.robot_position, self.robot_angle)
            self.send_arrived()

    def drive_path(self, path, target, speed):
        rotation_time = 0.75  # approximation of 1/4 turn
        if target[0] == 65535 and target[1] == 65535:
                time.sleep(rotation_time)  # TODO: calculate rotation
        else:
            if len(path) == 0:
                self.drive_line(self.robot_position, target, speed)
            else:
                point, path_speed = path[0]
                self.drive_line(self.robot_position, point, path_speed)
                time.sleep(rotation_time)
                if len(path) > 1:
                    for i in range(len(path)-1):
                        point1, path_speed = path[i]
                        point2, _ = path[i+1]
                        self.drive_line(point1, point2, path_speed)
                        time.sleep(rotation_time)  # TODO: calculate rotation
                    point, path_speed = path[len(path)-1]
                    self.drive_line(point, target, speed)
            self.robot_position = target

    def drive_line(self, start_point, target, speed):
        drive_time = self.calculate_time(start_point, target, speed)
        direction = math.atan2(target[1]-start_point[1], target[0]-start_point[0])
        distance = math.sqrt((target[0]-start_point[0])**2+(target[1]-start_point[1])**2)
        avg_speed = distance/drive_time
        time_now = 0
        while time_now < drive_time:
            time_now += 0.1
            x = start_point[0] + math.cos(direction) * time_now * avg_speed
            y = start_point[1] + math.sin(direction) * time_now * avg_speed
            self.send_position((x, y), self.robot_angle)
            time.sleep(0.1)

    def drive_angle(self):
        pass

    def send_arrived(self):
        can_msg = {
            'type': can.MsgTypes.Drive_Status.value,
            'status': 0,
            'time_to_destination': 0
        }
        self.can_socket.send(can_msg)

    def send_position(self, point, angle):
        can_msg = {
            'type': can.MsgTypes.Position_Robot_big.value,
            'x_position': int(point[0]),
            'y_position': int(point[1]),
            'angle': int((angle % 360) * 100),
            'position_correct': True,
            'angle_correct': True,
        }
        self.can_socket.send(can_msg)

    def calculate_time(self, point1, point2, speed_percent):
        distance = math.sqrt((point2[0]-point1[0])**2+(point2[1]-point1[1])**2)
        speed = self.speed_max*abs(speed_percent/100)
        acc_time = speed/self.accel
        drive_time = math.sqrt((distance*4)/self.accel)
        if drive_time > 2*acc_time:
            distance -= (speed**2/self.accel)
            drive_time = distance / speed
            drive_time += 2*acc_time
        return drive_time

if __name__ == "__main__":
    simulation = RobotSimulation()