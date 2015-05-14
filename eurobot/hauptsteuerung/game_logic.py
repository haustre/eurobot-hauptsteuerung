"""
This module decides which Task to do next
"""
__author__ = 'Wuersch Marcel'
__license__ = "GPLv3"

import math


class GameLogic():
    def __init__(self, game_tasks, drive, countdown, robots, side):
        self.points = {'stand': [6, 8, 6, 8, 8, 8],
                       'cup': [-100, -100, -100, -100, -100],
                       'clapper': [5, 5, 1],
                       'popcorn': [6, 4]}
        self.game_tasks = game_tasks
        self.drive = drive
        self.countdown = countdown
        self.robots = robots
        self.side = side
        self.running = True

    def start(self):
        while self.running:
            collected = self.game_tasks['stand'].collected
            if (collected >= 4) or (self.countdown.time_left() <= 20 and collected >= 2):
                point, angle = self.game_tasks['stand'].goto_empty()
                print("Empty Stands")
                if self.drive_fast(point, angle):
                    self.game_tasks['stand'].do_empty()
                    for i in range(len(self.points['stand'])):
                        self.points['stand'][i] /= 2

            collected = self.game_tasks['popcorn'].collected
            if (collected >= 10) or (self.countdown.time_left() <= 20 and collected >= 5):
                point, angle = self.game_tasks['popcorn'].goto_empty()
                print("Empty Popcorn")
                if self.drive_fast(point, angle):
                    self.game_tasks['popcorn'].do_empty()

            ratings = []
            for task_name, task in self.game_tasks.items():
                if task_name != 'stair':
                    distance_list = task.estimate_distances()
                    for game_element in distance_list:
                        distance, element_number = game_element
                        points = self.points[task_name][element_number]
                        rating = points - distance / 300
                        ratings.append((rating, task_name, element_number))
            index_of_task = ratings.index(max(ratings))
            _, task_name, element_number = ratings[index_of_task]
            point, angle = self.game_tasks[task_name].goto_task(element_number)
            print("Doing Task: " + str(task_name) + ", Nr:" + str(element_number))
            my_position = self.robots['me'].get_position()
            arrived = self.drive_fast(point, angle)
            if arrived:
                self.game_tasks[task_name].do_task(element_number)
                self.game_tasks[task_name].my_game_elements[element_number]['moved'] = True

    def calculate_distance(self, point1, point2):
        x1, y1 = point1
        x2, y2 = point2
        return math.sqrt((x1-x2)**2 + (y1-y2)**2)

    def drive_fast(self, destination, angle):
        path = []
        if self.side == 'left':
            path = [[700, 700], [700, 1300]]
        elif self.side == 'right':
            path = [[3000 - 700, 700], [3000 - 700, 1300]]
        if not(destination is None and angle is None):
            y_border = 800
            if (self.robots['me'].get_position()[1] > y_border) == (destination[1] > y_border):
                return self.drive.drive_path([], destination, angle)
            elif self.robots['me'].get_position()[1] < y_border:
                return self.drive.drive_path([path[0], path[1]], destination, angle)
            elif self.robots['me'].get_position()[1] > y_border:
                return self.drive.drive_path([path[1], path[0]], destination, angle)
        else:
            return True

    def stop(self):
        self.running = False
