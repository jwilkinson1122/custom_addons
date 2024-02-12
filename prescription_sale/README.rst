=============================================================
Return Merchandise Authorization Management - Link with Sales
=============================================================

This module allows you to link a sales order to an Prescription.
This can be done by creating an Prescription from scratch and selecting the sales
order, creating one or more Prescriptions from a sales order form view or from a sales
order web portal page.

Usage
=====

To use this module, you need to:

#. Go to *Prescription > Orders* and create a new Prescription.
#. Select a sales order to be linked to the Prescription if you want.
#. Now you can do the rest of the instructions described in the
   *readme* of the prescription module.

If you want to create one or more Prescriptions from a sale order:

#. Go to *Sales > Orders > Orders*.
#. Create a new sales order or select an existing one.
#. If the sales order is in 'Sales Order' state you can see in the status bar
   a button labeled 'Create Prescription', click it and a wizard will appear.
#. Modify the data at your convenience and click on 'Accept' button.
#. As many Prescriptions as lines with quantity greater than zero will be created.
   Those Prescriptions will be linked to the sales order.

The customer can also create Prescriptions from a sales order portal page:

#. Go to a confirmed sales order portal page.
#. In the left sidebar you can see a button named 'Request Prescriptions'.
#. By clicking on this button a popup will appear to allow you to define
   the quantity per product and delivery order line.
#. Click on the 'Request Prescriptions' button and Prescriptions will be created linked to
   the sales order.
