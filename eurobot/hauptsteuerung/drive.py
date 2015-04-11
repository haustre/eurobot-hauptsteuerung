"""
This module sends waypoints to the drive. The coordinates are first checked if they are on the table.
Then redundend points are removed
"""
__author__ = 'Wuersch Marcel'
__license__ = "GPLv3"

import time
import copy
import queue
from libraries import can


class Drive():
    def __init__(self, can_socket):
        self.can_socket = can_socket

    def send_path(self, path, destination, angle, path_speed=25, end_speed=25, blocking=True, close_range=False):
        in_save_zone = True
        wrong_point = None
        filtered_path = copy.copy(path)
        self.filter_path(filtered_path)
        save_zone = [[300, 2700], [300, 2700]]
        for point in filtered_path:
            if save_zone[0][0] > point[0] > save_zone[0][1] or save_zone[1][0] > point[1] > save_zone[1][1]:
                in_save_zone = False
                wrong_point = point
        if save_zone[0][0] > destination[0] > save_zone[0][1] or save_zone[1][0] > destination[1] > save_zone[1][1]:
            in_save_zone = False
            wrong_point = destination
        if in_save_zone:
            can_msg = {
                'type': can.MsgTypes.Goto_Position.value,
                'x_position': int(destination[0]),
                'y_position': int(destination[1]),
                'angle': int((abs(angle) % 360000)*100),
                'speed': end_speed,
                'path_length': len(path),
            }
            self.can_socket.send(can_msg)
            time.sleep(0.002)
            if len(path) > 0:
                for point in path:
                    can_msg = {
                        'type': can.MsgTypes.Path.value,
                        'x': point[0],
                        'y': point[1],
                        'speed': path_speed
                    }
                    self.can_socket.send(can_msg)
            if blocking:   # TODO: add timeout
                self.wait_for_arrival(close_range, path, speed=max(path_speed, end_speed))
        else:
            can_msg = {
                'type': can.MsgTypes.Emergency_Stop.value,
                'code': 0,
            }
            self.can_socket.send(can_msg)
            raise Exception('Coordinates outside the table:' + wrong_point)

    def filter_path(self, path):
        if len(path) > 3:
            points_to_delete = []
            for i in range(len(path)-2):
                for dir in (0, 1):
                    if ((path[i][dir] == path[i+1][dir] and path[i+1][dir] == path[i+2][dir]) or
                            (path[i][0] - path[i+1][0] == path[i+1][0] - path[i+2][0]) and
                            (path[i][1] - path[i+1][1] == path[i+1][1] - path[i+2][1])):
                        points_to_delete.append(i+1)
            print(len(path), set(points_to_delete))
            for index in reversed(sorted(list(set(points_to_delete)))):
                del path[index]

    def wait_for_arrival(self, close_range, path, speed=100):    # TODO: add timeout
        break_distance = 250 + (300 / 100 * speed)  # TODO: not tested
        drive_queue = queue.Queue()
        close_range_queue = queue.Queue()
        drive_queue_number = self.can_socket.create_queue(can.MsgTypes.Drive_Status.value, drive_queue)
        close_range_queue_number = self.can_socket.create_queue(can.MsgTypes.Close_Range_Dedection.value, close_range_queue)
        arrived = False
        emergency = False
        while arrived is False and emergency is False:
            try:
                close_range_msg = drive_queue.get_nowait()
                if close_range_msg['status'] == 0:
                    arrived = True
            except queue.Empty:
                pass
            if close_range:
                try:
                    close_range_msg = close_range_queue.get_nowait()
                    if ((close_range_msg['front_middle_correct'] and close_range_msg['distance_front_middle'] < break_distance) or
                       (close_range_msg['front_left_correct'] and close_range_msg['distance_front_left'] < break_distance) or
                       (close_range_msg['front_right_correct'] and close_range_msg['distance_front_right'] < break_distance)):
                        emergency = True
                        can_msg = {
                            'type': can.MsgTypes.Emergency_Stop.value,
                            'code': 0,
                        }
                        self.can_socket.send(can_msg)
                except queue.Empty:
                    pass
            time.sleep(0.001)
        self.can_socket.remove_queue(close_range_queue_number)
        self.can_socket.remove_queue(drive_queue_number)
        if emergency:
            return False
        else:
            return True