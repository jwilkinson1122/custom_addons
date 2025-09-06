==========================
Attached products in sales
==========================

This module allows to define a set of products which will be added atomatically to the
sales order whenever that product is present on it.

Configuration
=============

To configure attached products:

#. Go to *Sales > Products > Products* and choose on you want to attach products to.
#. Go to the *Sales* tab and then to the *Attached products* section.
#. Add as many products as you want to.

If you want to autoupdate the products when they are added, set this config parameter:

  - `sale_attached_product.auto_update_attached_lines`

Otherwise, the lines will be added, but they can be modified, deleted, etc.

Usage
=====

Now that you have your product configured:

#. Place a new sale order and then add that product in a new line.
#. Once you save your order, the attached products will be added in new lines to the
   order with as many quantities as the main one.

If the global `sale_attached_product.auto_update_attached_lines` setting is on:

#. Update the main product quantity and the attached product quantities will be updated
   in the same amount as well.
#. If we delete the main line, the attached ones will go away in any case.
