laptop package
##############

This packet contains a GUI program for controlling and debugging the robot. The GUI is written with
`pyqt4 <http://pyqt.sourceforge.net/Docs/PyQt4/introduction.html>`_.

.. figure::  images/gui1.png
   :width: 600px
   :align:   center

   Screenshot

The GUI has the following functions:

* Connection to the robot over ethernet. ( :py:class:`laptop.communication.EditHost`,
  :py:class:`laptop.gui.CanWindow.connect_host`, :py:class:`laptop.communication.TcpConnection`)
* Receiving all CAN messages received by the robot and display them in a table.
  ( :py:class:`laptop.communication.Table`, :py:class:`laptop.communication.CanTableControl` )
* Send CAN messages from the robot. ( :py:class:`laptop.communication.SendCan` )
* Show the position of each robot on a map. ( :py:class:`laptop.field.GameField` )

Submodules
==========

laptop_main
-----------

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

