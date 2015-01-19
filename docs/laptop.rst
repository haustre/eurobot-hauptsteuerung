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

This window allows to send a CAN message from the robot.
It contains the following parts:

*   The message type combo box for choosing which CAN message type is to send.
*   The send button for sending the message
*   The data fields. Each field represents one byte of data to be send. The text in the fields gets update every time
    the selection of the message type changes.

.. figure::  images/remote_control.*
   :align:   center
   :width:   20%

   Screenshot control window

This window allows to control the drive of the robot.
It contains the following parts:

*   The slider to select the speed.
*   The Drive button which has to be pressed down the whole time. If it is released the robot immanently stops.
*   The Close button for closing the window.

Structure
=========

The GUI is build up with multiple widgets. Each widget has its own build in functionality.
The communication between the widgets is implemented with
`QT Signal and Slots <http://qt-project.org/doc/qt-4.8/signalsandslots.html>`_.

.. figure::  images/gui_dfd_1.*
   :align:   right

   Data Flow Diagram of the laptop software

The data flow diagram shows the structure of the program. Here is a description of each widget:

*   TcpConnection, :py:class:`laptop.communication.TcpConnection`
        Receives and sends TCP data from the robot.
*   CAN Packer, :py:class:`libraries.can._pack`
        Packs a the data to be send to a Can message and unpacks the received CAN messages.
*   Field, :py:class:`laptop.field.GameField`
        Draws the position of each robot on a map.
*   Edit Host, :py:class:`laptop.communication.EditHost`
        Sets the IP address and the port of the TCP connection.
*   CAN Table Control, :py:class:`laptop.communication.CanTableControl`
        Filters the CAN messages to be displayed.
*   CAN Table, :py:class:`laptop.communication.Table`
        Displays all received CAN messages.
*   Send CAN, :py:class:`laptop.communication.SendCan`
        Send CAN messages from the robot.
*   Remote Control, :py:class:`laptop.remote_control.RemoteControlWindow`
        Remote control the robot

When new date arrives over tcp it first gets packed to a dictionary. Then it is send to the CAN table control which
controls which data should be displayed in the table. Then it is put in the table. At the same time the dictionary is
sent to the field widget. The field widget filters out the position data and draws it on the map.

There are 2 ways to send data. The first is to use the send can widget.
Here you can select which type of data you want to send and then manually enter it.
The second way is the remote control widget. It allows to control the drive with the keyboard.

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

