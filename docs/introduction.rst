Introduction
============

The main unit of the robot controls the whole robot over CAN bus. The software is writen in
`python3 <https://docs.python.org/3/>`_.

The software contains multiple parts:

* The :doc:`hauptsteuerung` is running on the robot.
* The :doc:`laptop` contains the software for controlling the robot from a computer.
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

:pep:`8` is used as style guide for the code.

This documentation is written with `Sphinx <http://sphinx-doc.org/>`_ (a tool to make technical documentations).

License
_______

The software is licensed with `GPLv3 <http://www.gnu.org/licenses/gpl-3.0.html>`_.

.. figure::  images/gplv3.png
   :align:   center