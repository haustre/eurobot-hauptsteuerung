__author__ = 'mw'

import subprocess


def speak(text):
    """ Gives a given String out over Loudspeaker.

    .. note::
        Needs "espeak" to be installed.

    :param text: String to give out
    :type text: str
    """
    language = 'en'
    speed = '175'  # Speed in words per minute, 80 to 450, default is 175
    print("speak:", text)
    try:
        command = subprocess.Popen(['espeak', '-v', language, '-s', speed, str(text)])
    except FileNotFoundError:
        print("Espeak not working! (probably not installed)")