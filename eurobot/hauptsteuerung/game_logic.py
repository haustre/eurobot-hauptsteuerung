"""
This module decides which Task to do next
"""
__author__ = 'Wuersch Marcel'
__license__ = "GPLv3"

import math


class GameLogic():
    def __init__(self, game_tasks, drive, countdown, robots):
        self.game_tasks = game_tasks
        self.drive = drive
        self.countdown = countdown
        self.robots = robots
        self.running = True

    def start(self):
        while self.running:
            collected = self.game_tasks['stand'].collected
            if (collected >= 4) or (self.countdown.time_left() <= 20 and collected >= 2):
                point, angle = self.game_tasks['stand'].goto_empty()
                print("Empty Stands")
                if self.drive_fast(point, angle):
                    self.game_tasks['stand'].do_empty()
                    self.game_tasks['stand'].points_game_element /= 2

            collected = self.game_tasks['popcorn'].collected
            if (collected >= 10) or (self.countdown.time_left() <= 20 and collected >= 5):
                point, angle = self.game_tasks['popcorn'].goto_empty()
                print("Empty Popcorn")
                if self.drive_fast(point, angle):
                    self.game_tasks['popcorn'].do_empty()

            ratings = []
            for task_name, task in self.game_tasks.items():
                if task_name != 'stair':
                    distance, element_number = task.estimate_distance()
                    points = task.points_game_element
                    if task_name == 'clapper' and element_number == 2:
                        points /= 2
                    rating = points - distance / 300
                    ratings.append((rating, task_name, element_number))
            index_of_task = ratings.index(max(ratings))
            _, task_name, element_number = ratings[index_of_task]
            point, angle = self.game_tasks[task_name].goto_task(element_number)
            print("Doing Task: " + str(task_name) + ", Nr:" + str(element_number))
            my_position = self.robots['me'].get_position()
            if point:
                distance = self.calculate_distance(point, my_position)
            else:
                distance = 0
            if distance < 200:
                arrived = self.drive.drive_path([], point, angle)
            else:
                arrived = self.drive_fast(point, angle)
            if arrived:
                self.game_tasks[task_name].do_task(element_number)

    def calculate_distance(self, point1, point2):
        x1, y1 = point1
        x2, y2 = point2
        return math.sqrt((x1-x2)**2 + (y1-y2)**2)

    def drive_fast(self, destination, angle):
        y_border = 800
        print("Test")
        print(destination, self.robots['me'].get_position())
        if (self.robots['me'].get_position()[1] > y_border) == (destination[1] > y_border):
            return self.drive.drive_path([], destination, angle)
        else:
            return self.drive.drive_path([(2100, 1000)], destination, angle)

    def stop(self):
        self.running = False
