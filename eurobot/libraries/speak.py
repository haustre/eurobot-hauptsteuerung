"""
This package contains method's to entertain the user.
"""
__author__ = 'Würsch Marcel'
__license__ = "GPLv3"

import subprocess
import urllib.request
import json


def speak(text):  # TODO: check if espeak is installed
    """ This function gives out a string over loudspeaker
    :param text: String to give out
    :type text: str

    .. note::
        Needs "espeak" to be installed. ( Install with sudo apt-get install espeak)
    """
    language = 'en'
    speed = '0'  # Speed in words per minute, 80 to 450, default is 175
    print("speak:", text)
    command = subprocess.Popen(['espeak', '-v', language, '-s', speed, str(text)])


def tell_a_joke():
    """ This function downloads a Chuck Norris joke from a website.

    :return: joke
    :rtype: str
    """
    try:
        req = urllib.request.urlopen("http://api.icndb.com/jokes/random?limitTo=[nerdy]", timeout=1)
        full_json = req.read().decode('UTF-8')
        full = json.loads(full_json)
        joke = full['value']['joke']
        return joke
    except:
        print("No internet connection!")
        return ""