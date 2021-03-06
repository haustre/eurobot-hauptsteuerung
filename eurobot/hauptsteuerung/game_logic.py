"""
This module decides which Task to do next
"""
__author__ = 'Wuersch Marcel'
__license__ = "GPLv3"

import time

class GameLogic:
    def __init__(self, game_tasks, drive, countdown, robots, side):
        self.points = {'stand': [2, 8, 2, 8, 8, 8],
                       'cup': [-100, 4, -100, -100, -100],
                       'clapper': [5, 5, 1],
                       'popcorn': [6, 3]}
        self.game_tasks = game_tasks
        self.drive = drive
        self.countdown = countdown
        self.robots = robots
        self.side = side
        self.running = True
        self.finished = False

    def start(self):
        while self.running:
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

            stands_collected = self.game_tasks['stand'].collected
            popcorn_collected = self.game_tasks['popcorn'].collected
            if stands_collected >= 4 and not(task_name == 'clapper' and element_number == 0):
                point, angle = self.game_tasks['stand'].goto_empty()
                print("Empty Stands")
                if self.drive_fast(point, angle):
                    self.game_tasks['stand'].do_empty()
                continue
            if self.countdown.time_left() <= 20 or self.finished:
                point, angle = self.game_tasks['popcorn'].goto_empty()
                print("Empty Popcorn")
                if self.drive_fast(point, angle):
                    self.game_tasks['popcorn'].do_empty()
                    break
                continue
            if task_name == 'clapper' and element_number == 2:
                self.finished = True
                continue
            if task_name == 'cup':
                self.game_tasks[task_name].my_game_elements[element_number]['moved'] = True
                continue
            point, angle = self.game_tasks[task_name].goto_task(element_number)
            print("Doing Task: " + str(task_name) + ", Nr:" + str(element_number))
            arrived = self.drive_fast(point, angle)
            if arrived:
                self.game_tasks[task_name].do_task(element_number)
                self.game_tasks[task_name].my_game_elements[element_number]['moved'] = True
            else:
                self.points[task_name][element_number] -= 0.1
                time.sleep(0.1)

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
            elif destination[1] == 1000:  # empty popcorn
                return self.drive.drive_path([], destination, angle)
            elif self.robots['me'].get_position()[1] < y_border:
                return self.drive.drive_path([path[0], path[1]], destination, angle)
            elif self.robots['me'].get_position()[1] > y_border:
                return self.drive.drive_path([path[1], path[0]], destination, angle)
        else:
            return True

    def stop(self):
        self.running = False
