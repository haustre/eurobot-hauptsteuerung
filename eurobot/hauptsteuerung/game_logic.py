"""
This module decides which Task to do next
"""
__author__ = 'Wuersch Marcel'
__license__ = "GPLv3"


class GameLogic():
    def __init__(self, game_tasks, drive):
        self.game_tasks = game_tasks
        self.drive = drive
        self.running = True

    def start(self):
        while self.running:
            ratings = []
            for task_name, task in self.game_tasks.items():
                if task_name != 'stair':
                    distance, element_number = task.estimate_distance()
                    points = task.points_game_element
                    rating = points - distance / 300
                    ratings.append((rating, task_name, element_number))
            index_of_task = ratings.index(max(ratings))
            _, task_name, element_number = ratings[index_of_task]
            point, angle = self.game_tasks[task_name].goto_task(element_number)
            print("Doing Task: " + str(task_name) + ", Nr:" + str(element_number))
            if self.drive.drive_route(point, angle):
                self.game_tasks[task_name].do_task(element_number)

    def stop(self):
        self.running = False
