.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=====================================
Customer Order Number for Sale Orders
=====================================

* Adds a simple customer order number field to Sale Orders
* Intended for situations where the customer has supplied their own order # to
  be used along with the Odoo standard SOxxx.

Configuration
=============
* Optional: Go to sales configuration and check the 'Pass Customer Order Number
  to Invoice' checkbox. This transfers the order number to the Terms and
  Conditions freetext field when creating an invoice from the sale.

Usage
=====
\- 

Known issues / Roadmap
======================
* Note that previously this module provided a Customer Order Number field also
  for invoices. Due to invoicing integrations field limitations this field has
  been removed, and the data is now appended to the Terms and Conditions field
  instead.

Credits
=======

Contributors
------------
* Timo Talvitie <timo.talvitie@tawasta.fi>

Maintainer
----------

.. image:: http://tawasta.fi/templates/tawastrap/images/logo.png
   :alt: Oy Tawasta OS Technologies Ltd.
   :target: http://tawasta.fi/

This module is maintained by Oy Tawasta OS Technologies Ltd.
