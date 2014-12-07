libraries package
#################

This module contains classes used to control hardware. It is used on the robot and on the computer.

* The :ref:`ethernet-module` allows the communication between the robot and the computer over tcp.
* The :ref:`can-module` is used to send CAN messages and it contains information over the messages
  that are used to display them on the computer.
* The :ref:`speak-module` allows to give out a text over loudspeaker on both the robot and the computer.

Submodules
==========

.. _can-module:

libraries.can module
--------------------

Example
^^^^^^^

    Here a short example how to use the CAN interface:
    First you have to create a new object:

    >>> can_connection = libraries.can.Can("can0", MsgSender.Debugging)

    To send a message you have to put it in a dictionary:

    >>> can_msg = {
            'type': can.MsgTypes.Position_Robot_1,
            'position_correct': True,
            'angle_correct': False,
            'angle': angle,
            'y_position': y,
            'x_position': x
        }
    >>> can_connection.send(can_msg)

    The received messages are taken from the buffer like this:

    >>> can_msg = can_connection.queue_position_Robot_1.get()

.. note::
    There are 2 different ways to get the next value from a buffer:

    * buffer.get()  This method waits for new data. The program is blocked.
    * buffer.get_nowait()   This method returns None if there is no data available.


Description
^^^^^^^^^^^

.. automodule:: libraries.can
    :members:
    :undoc-members:
    :show-inheritance:
    :exclude-members: MsgSender, MsgTypes

.. todo:: document MsgSender, MsgTypes

.. _ethernet-module:

libraries.ethernet module
-------------------------

The ethernet module allows the connection between the robot and a computer.
2 components are used to make the connection:

* :py:class:`libraries.ethernet.Server` runs on the Robot.
* :py:class:`libraries.ethernet.Client` runs on the computer

Example
^^^^^^^

Here a short example how to use the ethernet interface:

On the robot you have to create a server object:

>>> tcp = libraries.ethernet.Server()

On the computer you have to create a client object:

>>> tcp = ethernet.Client(self.host, int(self.port))

Sending and receiving messages works the same on both sides:

>>> tcp.write(msg)
>>> tcp.read_block()

.. note::
    There are 2 different ways to get the next message from the ethernet interface:

    * tcp.read_block()  This method waits for new data. The program is blocked.
    * tcp.read_block()  This method returns None if there is no data available.

Description
^^^^^^^^^^^

.. automodule:: libraries.ethernet
    :members:
    :undoc-members:
    :show-inheritance:

.. _speak-module:

libraries.speak module
----------------------

.. automodule:: libraries.speak
    :members:
    :undoc-members:
    :show-inheritance:
