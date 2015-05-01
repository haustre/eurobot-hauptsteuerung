.. _hauptsteuerung-package:

hauptsteuerung package
######################

.. automodule:: hauptsteuerung.__init__

Structure
=========

.. figure::  images/kern_dfd_1.*
   :align:   right

   Task-Model of robot software

The program is build up with multiple tasks, each running on its own thread.
This is important because the robot wil have to do multiple things in parallel.
The communication between the threads is implemented with `queues <https://docs.python.org/3.4/library/queue.html>`_.


The blue tasks are not jet programmed. Everything in blue is only a rough structure for the software of PA2.
Those parts of the software will contain all the 'intelligence' of the program.

The Tasks-Model shows the structure of the program. Here is a description of each task:

*   Wait for new connections, :py:func:`libraries.ethernet.Server.wait_connections`
        Thread waiting for new tcp connections. For each new connection a new connection thread is created.
*   Connection1,2, :py:func:`libraries.ethernet.Server._connection`
        One thread per parallel connection. Checks sending queue for messages to send over tcp. And puts new incoming
        tcp data in the receive queue.
*   Debug, :py:func:`hauptsteuerung.debug.LaptopCommunication`
        This thread collects data from the robot to send to the computer and saves it to memory.
*   CAN out, :py:func:`libraries.can.Can._send_connection`
        Thread sending out the CAN messages from the send queue.
*   CAN in, :py:func:`libraries.can.Can._recv_connection`
        Thread putting new received CAN messages in the receive queue.
*   Navigation
        Knows the position of each robot and every thing else on the table.
*   Game logic
        Has the overview of the game and decides where to go and which task to start.
*   Game tasks
        One thread per task. Can send and receive CAN messages and communicates with the game logic task.

.

Submodules
==========

hauptsteuerung_main
-------------------

For an overview of the whole package look :ref:`hauptsteuerung-package`

.. automodule:: hauptsteuerung_main
    :members:
    :undoc-members:
    :show-inheritance:

hauptsteuerung.debug module
---------------------------

.. automodule:: hauptsteuerung.debug
    :members:
    :undoc-members:
    :show-inheritance:

hauptsteuerung.drive module
---------------------------

.. automodule:: hauptsteuerung.drive
    :members:
    :undoc-members:
    :show-inheritance:

hauptsteuerung.game_logic module
--------------------------------

.. automodule:: hauptsteuerung.game_logic
    :members:
    :undoc-members:
    :show-inheritance:

hauptsteuerung.robot module
---------------------------

.. automodule:: hauptsteuerung.robot
    :members:
    :undoc-members:
    :show-inheritance:

hauptsteuerung.route_finding module
-----------------------------------

.. automodule:: hauptsteuerung.route_finding
    :members:
    :undoc-members:
    :show-inheritance: