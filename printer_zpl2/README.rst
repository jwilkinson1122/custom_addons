==============
Printer ZPL II
==============

This module extends the **Report to printer** (``base_report_to_printer``)
module to add a ZPL II label printing feature.

This module is meant to be used as a base for module development, and does not provide a GUI on its own.
See below for more details.

Installation
============

Nothing special, just install the module.

Configuration
=============

To configure this module, you need to:

#. Go to *Settings > Printing > Labels > ZPL II*
#. Create new labels
#. Import ZPL2 code
#. Use the Test Mode tab during the creation

It's also possible to add a label printing wizard on any model by creating a new *ir.actions.act_window* record.
For example, to add the printing wizard on the *product.product* model ::

    <act_window id="action_wizard_purchase"
      name="Print Label"
      src_model="product.product"
      res_model="wizard.print.record.label"
      view_mode="form"
      target="new"
      key2="client_action_multi"/>

Usage
=====

To print a label, you need to call use the label printing method from anywhere (other modules, server actions, etc.).

Example : Print the label of a product ::

    self.env['printing.label.zpl2'].browse(label_id).print_label(
        self.env['printing.printer'].browse(printer_id),
        self.env['product.product'].browse(product_id))

You can also use the generic label printing wizard, if added on some models.

