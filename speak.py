__author__ = 'mw'

import subprocess


def speak(text):
    language = 'en'
    speed = '175'  # Speed in words per minute, 80 to 450, default is 175
    command1 = subprocess.Popen(['espeak', '-v', language, '-s', speed, str(text)])