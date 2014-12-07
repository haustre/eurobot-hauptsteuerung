Introduction
============

The main unit of the robot controls the whole robot over CAN bus. The software is writen in
`python3 <https://docs.python.org/3/>`_.

The software contains 3 parts:

* The :py:class:`kern` module is running on the robot.
* The :py:class:`gui` module contains the software for controlling the robot which is running on a computer.
* The :py:class:`libraries` module contains libraries used by the robot and the computer:
    * :py:class:`libraries.ethernet` allows the communication between the robot and the computer over tcp.
    * :py:class:`libraries.can` is used to send CAN messages and it contains information over the messages
      that are used to display them on the computer.
    * :py:class:`libraries.speak` allows to give out a text over loudspeaker on both the robot and the computer.

Python3.4 or newer and a kernel with `SocketCAN <https://www.kernel.org/doc/Documentation/networking/can.txt>`_ support
is required to run the software. To use the :py:class:`libraries.speak` module the
program `espeak <http://espeak.sourceforge.net/>`_ needs to be installed. On the computer you need to
install `pyqt4 <http://pyqt.sourceforge.net/Docs/PyQt4/introduction.html>`_ to be able to run the gui.

This documentation is written with `Sphinx <http://sphinx-doc.org/>`_ (a tool to make technical documentations).