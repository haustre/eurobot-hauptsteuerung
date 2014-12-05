libraries package
=================

Submodules
----------

libraries.can module
--------------------

Example
^^^^^^^

    Here a short example how to use the CAN interface:
    First you have to create a new object:

    >>> can_connection = Can("can0", MsgSender.Debugging)

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

libraries.ethernet module
-------------------------

.. automodule:: libraries.ethernet
    :members:
    :undoc-members:
    :show-inheritance:

libraries.speak module
----------------------

.. automodule:: libraries.speak
    :members:
    :undoc-members:
    :show-inheritance:


Module contents
---------------

.. automodule:: libraries
    :members:
    :undoc-members:
    :show-inheritance:
