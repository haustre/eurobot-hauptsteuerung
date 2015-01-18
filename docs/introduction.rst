Introduction
============

The main unit of the robot controls the whole robot over CAN bus. The software is writen in
`python3 <https://docs.python.org/3/>`_.

The software contains multiple parts:

* The :py:mod:`hauptsteuerung_main` module is running on the BeagleBone build in to the robot.
  It uses the functionality of the :doc:`hauptsteuerung` to run.
* The :py:mod:`laptop_main` module is running on a computer and allows tho connect to the robot over ethernet.
  It uses the functionality of the :doc:`laptop` to run.
* The :doc:`libraries` contains libraries used by the robot and the computer.
* The :doc:`tests` contains different test for the software.



Requirements
____________

Python3.4 or newer and a kernel with `SocketCAN <https://www.kernel.org/doc/Documentation/networking/can.txt>`_ support
is required to run the software. To use the :py:mod:`libraries.speak` module the
program `espeak <http://espeak.sourceforge.net/>`_ needs to be installed. On the computer you need to
install `pyqt4 <http://pyqt.sourceforge.net/Docs/PyQt4/introduction.html>`_ to be able to run the gui.

Code style and documentation
____________________________

:pep:`8` is used as style guide for the code. We used the PyCharm 4 Professional Edition Ide
from `Jetbrains <https://www.jetbrains.com/pycharm/>`_.

This documentation is written with `Sphinx <http://sphinx-doc.org/>`_ (a tool to make technical documentations).
The documentation is located in the docs folder.

Building and viewing this Documentation
'''''''''''''''''''''''''''''''''''''''

To build the documentation run::

    cd 'Directory of Project'
    sphinx-build -b html docs/  docs/_build/html

This creates the full documentation in docs/_build/html.

License
_______

The software is licensed with `GPLv3 <http://www.gnu.org/licenses/gpl-3.0.html>`_.

.. figure::  images/gplv3.png
   :align:   center