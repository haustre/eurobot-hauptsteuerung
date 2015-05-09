__author__ = 'mw'


import sys
import time
import queue
import math
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
        if target[0] == 65535 and target[1] == 65535:
                time.sleep(0.5)  # TODO: calculate rotation
        else:
            drive_time = self.calculate_time(self.robot_position, target, speed)
            direction = math.atan2(target[1]-self.robot_position[1], target[0]-self.robot_position[0])
            distance = math.sqrt((target[0]-self.robot_position[0])**2+(target[1]-self.robot_position[1]))
            avg_speed = distance/drive_time
            time_now = 0
            while time_now < drive_time:
                time_now += 0.02
                x = self.robot_position[0] + math.cos(direction) * time_now * avg_speed
                y = self.robot_position[1] + math.sin(direction) * time_now * avg_speed
                self.send_position((x, y), self.robot_angle)
                time.sleep(0.02)
            self.robot_position = target

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
        print(drive_time)
        return drive_time

if __name__ == "__main__":
    simulation = RobotSimulation()