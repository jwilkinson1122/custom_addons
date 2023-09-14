====================
Account cash invoice
====================

This modules allows to pay an existing Supplier Invoice / Customer Refund, or
to collect payment for an existing Customer Invoice from a Cash Statement.


Usage
=====

#.  Go to *Settings* and activate the developer mode.
#.  Go to *Settings / Users & Companies / Users* and set the flag
    'Show Full Accounting Features'.
#.  Go to *Invoicing / Dashboard* and create and/or open an existing
    Cash Statement from a Cash Journal.
#.  Press the button **Pay Invoice** to pay a Supplier Invoice or a Customer
    Refund. You will need to select the expected Journal
#.  Select **Collect Payment from Invoice** in to receive a payment of an
    existing Customer Invoice or a Supplier Refund.
#.  Press **Validate** on the statement. The payment will then be reconciled
    with the invoice.

Known issues / Roadmap
======================

* Cannot pay invoices in a different currency than that defined in the journal
  associated to the payment method used to pay/collect payment.


