=======================
POS Session Pay invoice
=======================

This modules allows to pay an existing Supplier Invoice / Customer Refund, or
to collect payment for an existing Customer Invoice, from within a POS Session.

Configuration
=============

#.  Go to *Point of Sale / Configuration / Point of Sale* and activate the
    'Cash Control' setting.

Usage
=====

#.  Go to *Point of Sale / Dashboard* and create and open or access to an
    already open POS Session.
#.  Press the button **Pay Invoice** to pay a Supplier Invoice or a Customer
    Refund. It will be paid using Cash.
#.  Select **Collect Payment from Invoice** in to receive a payment of an
    existing Customer Invoice or a Supplier Refund. You will need to select
    a Journal if the POS Config has defined multiple Payment Methods.

Known issues / Roadmap
======================

* Cannot pay invoices in a different currency than that defined in the journal
  associated to the payment method used to pay/collect payment.

* Should depend on `pos_invoicing` but it requires a refactoring of `pos_invoicing`.
  It will be improved when migrating to 13.0
