"""
Gives a given String out over Loudspeaker.
"""
__author__ = 'Würsch Marcel'
__license__ = "GPLv3"

import subprocess
import urllib
import json


def speak(text):  # TODO: check if espeak is installed
    """
    :param text: String to give out
    :type text: str

    .. note::
        Needs "espeak" to be installed. ( Install with sudo apt-get install espeak)
    """
    language = 'en'
    speed = '175'  # Speed in words per minute, 80 to 450, default is 175
    print("speak:", text)
    command = subprocess.Popen(['espeak', '-v', language, '-s', speed, str(text)])