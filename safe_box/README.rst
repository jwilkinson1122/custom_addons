===================
Cash Box management
===================

This module allows to define and manage safe box groups.
A safe box group is a set of accounts of different companies that allows to manage an integrated cash management.
This is useful for multicompany environments with an integrated management of cash.
Cash can be moved between safe boxes inside the group without creation of account moves.
Also, the cash of each safe box is shared between all the companies, but, we are unable to know which part belongs to each one.
However, the total amount of all safe boxes must be equal to the balance of all the accounts.

This module allows to manage a safe box group, including:

Configuration
=============

* Access `Invoicing / Safe box / Safe box group`
   * Create a Safe Box Group
   *  Add Safe boxes inside the safe box group
   *  Add coins and bill managed by the safe box group
   *  Assign coins and bill to each safe box
   * Assign specific users to a safe box
* Access `Invoicing / Configuration / Accounting / Chart of Accounts`
   * Create or edit an account and select a safe box group

Usage
=====

Access `Invoicing / Safe box / Safe box group` and select a Safe Box Group

Create an external move
~~~~~~~~~~~~~~~~~~~~~~~

* Press `Add external move`
* Select a journal, original account and safe box
* Set the amount.
    If negative, it will take the money from the safe box.
    If positive, it will add it to the safe box.
* Approve the move

Create an internal move
~~~~~~~~~~~~~~~~~~~~~~~

* Press `Add internal move`
* Select an original safe box, a destination safe box and amount
* Approve the move

Counting money
~~~~~~~~~~~~~~~~~~~~~~~

* Press `Count money`
* Select a safe box
* Set the value of the coins
    If the total amount of the coins is equal to the one of the safe box,
    a "Cash Box amount is correct" message will appear.
    If not, a "Cash Box amount is different" will appear.

