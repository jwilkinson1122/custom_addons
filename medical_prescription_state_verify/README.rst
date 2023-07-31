.. image:: https://img.shields.io/badge/license-GPL--3-blue.svg
    :target: http://www.gnu.org/licenses/lgpl-3.0-standalone.html
    :alt: License: GPL-3

============================================
Prescription Verification - States and Logic
============================================

This module introduces the notion of verification to the prescription states 
added in `medical_prescription_state`, which can now be either verified or 
unverified. It also adds the following logic:

* Once a prescription order is in a verified state, it can be cancelled or 
  marked as an exception, but no other changes to the order are allowed
* When a prescription order moves from an unverified state to a verified one, 
  its order lines automatically move to a hold state
* When a prescription order is cancelled or marked as an exception, its order 
  lines are automatically marked as exceptions
* Once a prescription order line is in a verified state, it cannot be moved to 
  an unverified state other than the exception state

Usage
=====

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/159/10.0

Bug Tracker
===========

Bugs are tracked on 
`GitHub Issues <https://github.com/OCA/vertical-medical/issues>`_. In case of 
trouble, please check there if your issue has already been reported. If you 
spotted it first, help us smash it by providing detailed and welcome feedback.

Credits
=======

Images
------

* Odoo Community Association: 
  `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Dave Lasley <dave@laslabs.com>
* Ken Mak <kmak@laslabs.com>
* Oleg Bulkin <obulkin@laslabs.com>

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
