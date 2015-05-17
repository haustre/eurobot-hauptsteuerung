"""
This is file displays the start screen
"""
__author__ = 'Wuersch Marcel'
__license__ = "GPLv3"

import sys

from colorama import init
init(strip=not sys.stdout.isatty())  # strip colors if stdout is redirected
from termcolor import cprint
from pyfiglet import figlet_format

def print_start_text(text):
    try:
        cprint(figlet_format(text, font='starwars'), 'red', 'on_blue', attrs=['bold'])
    except:
        print(text)
