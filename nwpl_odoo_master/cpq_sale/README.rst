--------
cpq_sale
--------

Integrate CPQ and sale modules.

Requires the use of `sale_product_configurator`.

Hooks the sale_product_configurator widget to inject the Cpq ConfigureDialog
widget.

-------------
base_revision
-------------

Provides a base model for revision management in Odoo, allowing for
versioning of records. 

Making revision(s) of a document is a common need across many area.

This module does not provide a functionality by itself but an abstract
model to implement revision capality in other models (e.g. purchase
orders, sales orders, budgets, expenses...).

example with sale_order_revision installed,

On a cancelled orders, you can click on the "New copy of Quotation"
button. This will create a new revision of the quotation, with the same
base number and a '-revno' suffix appended. A message is added in the
chatter saying that a new revision was created.

In the form view, a new tab is added that lists the previous revisions,
with the date they were made obsolete and the user who performed the
action.

The old revisions of a sale order are flagged as inactive, so they don't
clutter up searches.

