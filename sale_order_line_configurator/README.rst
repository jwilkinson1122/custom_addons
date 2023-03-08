.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

============================
Sale Order line configurator
============================

The button "Configure a product" no longer exist on 14.0 standard version. This module
adds the same functionality that was used on Odoo 12.0 version.

Configuration
=============
The configurator should open only with 'context="{'open_product_configurator': True}"'
set to form's tree line.

Usage
=====
Go to sale order form view and search "Configure a product" in the sale order line list.
This button is shown if product variants are used in the system.

IMPORTANT!!!
The module depends on sale_product_configurator module(!) that modifies sale order form view.
But this module modifies the same form view to hide product.template-field and makes
product.product-field visible.

Known issues / Roadmap
======================
\-

Credits
=======

Contributors
------------

* Timo Kekäläinen <timo.kekalainen@tawasta.fi>

Maintainer
----------

.. image:: http://tawasta.fi/templates/tawastrap/images/logo.png
   :alt: Oy Tawasta OS Technologies Ltd.
   :target: http://tawasta.fi/

This module is maintained by Oy Tawasta OS Technologies Ltd.
