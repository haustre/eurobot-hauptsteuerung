.. _laptop-package:

laptop package
##############

.. automodule:: laptop.__init__

Screenshots
===========

The GUI has multiple windows. Here is a short description of each.

.. figure::  images/mainwindow.*
   :align:   center
   :width:   80%

   Screenshot main window

The main windows contains multiple parts. Each with its own function.

*   Connection to Host
        Type in the IP and port of the robot you want to connect to. Normally the big robot has the IP 192.168.1.101
        and the small robot has the address 192.168.1.101. Both listen on the port 42233. Press Connect to connect.
*   The map draws the position and orientation of each robot. Each robot has its own image. The positions are updated
    when the robot is connected.
*   The table on the top shows the CAN messages the robot has received.
*   CanTable
        Only the message types that are selected will be displayed. The messages are only received if the run button
        is activated. Auto Scroll activates auto scroll of the table.
*   Send CAN message
        This button opens the can send window.
*   Activate Remote Control
        This button opens the remote control windows.


.. figure::  images/can_send.*
   :align:   center
   :width:   40%

   Screenshot can send window

.. figure::  images/remote_control.*
   :align:   center
   :width:   20%

   Screenshot control window

Structure
=========

The GUI is build up with multiple widgets. Each widget has its own build in functionality.
The communication between the widgets is implemented with
`QT Signal and Slots <http://qt-project.org/doc/qt-4.8/signalsandslots.html>`_.

Data Flow Diagram
-----------------

.. figure::  images/gui_dfd_1.*
   :align:   center

   Data Flow Diagram of the laptop software

* TCP Connection: Connection to the robot over TCP.
    :py:class:`laptop.communication.EditHost` and :py:class:`laptop.communication.TcpConnection`.
* Receiving all CAN messages received by the robot and display them in a table.
    This is done with :py:class:`laptop.communication.CanTableControl` and :py:class:`laptop.communication.Table`.
* Send CAN messages from the robot.
    This is done with :py:class:`laptop.communication.SendCan`
* Show the position of each robot on a map.
    This is done with :py:class:`laptop.field.GameField`
* Remote control the robot.
    This is done with :py:class:`laptop.remote_control.RemoteControlWindow`.

When new date arrives over tcp it first gets packed to a dictionary. Then it is send to the CAN table control which
controls which data should be displayed in the table. Then it is put in the table. At the same time the dictionary is
sent to the field widget. The field widget filters out the position data and draws it on the map.

There are 2 ways to send data. The first is to use the send can widget.
Here you can select which type of data you want to send and then manually enter it.
The second way is the remote control widget.


* TcpConnection
    Receives new TCP data with :py:class:`laptop.communication.TcpConnection`.

Submodules
==========

laptop_main module
------------------

For an overview of the whole package look :ref:`laptop-package`

.. automodule:: laptop_main
    :members:
    :undoc-members:
    :show-inheritance:
    :exclude-members: bin_, hex_, oct_

laptop.communication module
---------------------------

.. automodule:: laptop.communication
    :members:
    :undoc-members:
    :show-inheritance:
    :exclude-members: bin_, hex_, oct_

laptop.field module
-------------------

.. automodule:: laptop.field
    :members:
    :undoc-members:
    :show-inheritance:
    :exclude-members: bin_, hex_, oct_

laptop.remote_control module
----------------------------

.. automodule:: laptop.remote_control
    :members:
    :undoc-members:
    :show-inheritance:
    :exclude-members: bin_, hex_, oct_

