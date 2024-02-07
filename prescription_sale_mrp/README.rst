================================================================
Return Product Authorization Management - Link with MRP Kits
================================================================

This module enables Prescription for kits, wich isn't compatible with the base modules.
In the backend side, we can return separate component while in the frontend
side, customers can return the whole kit and the proper Prescription will be generated.

Usage
=====

To use this module, you need to:

#. Make a a sale order with a kit on it and deliver its components.
#. Go to the portal view for the order and launch the Prescription wizard.
#. You'll see a line for the kit.
#. There will be a limit of kits to return that should much the number of kits
   delivered.
#. Once you validate the wizard with the number of kits to deliver, you'll
   have as many Prescription as components those kits have with the proper quantities
   for each one.
#. If you refund the components, the kit in the sale line will be used as the
   reference.
