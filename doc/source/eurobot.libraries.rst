eurobot.libraries package
=========================

eurobot.libraries.can module
----------------------------

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



.. automodule:: eurobot.libraries.can
    :members:
    :undoc-members:
    :private-members:
    :show-inheritance:


eurobot.libraries.ethernet module
---------------------------------

.. automodule:: eurobot.libraries.ethernet
    :members:
    :undoc-members:
    :show-inheritance:

eurobot.libraries.speak module
------------------------------

.. automodule:: eurobot.libraries.speak
    :members:
    :undoc-members:
    :show-inheritance:
