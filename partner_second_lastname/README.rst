========================
Partner second last name
========================

This module was written to extend the functionality of ``partner_firstname`` to
support having a second lastname for contact partners.

In some countries, it's important to have a second last name for contacts.

Contact partners will need to fill at least one of the name fields
(*First name*, *First last name* or *Second last name*).

Configuration
=============

You can configure some common name patterns for the inverse function
in Settings > Configuration > General settings:

* Lastname SecondLastname Firstname: For example 'Anderson Lavarge Robert'
* Lastname SecondLastname, Firstname: For example 'Anderson Lavarge, Robert'
* Firstname Lastname SecondLastname: For example 'Robert Anderson Lavarge'

After applying the changes, you can recalculate all partners name clicking
"Recalculate names" button. Note: This process could take so much time depending
how many partners there are in database.

You can use *_get_inverse_name* method to get firstname, lastname and
second lastname from a simple string and also *_get_computed_name* to get a
name form the firstname, lastname and second lastname.
These methods can be overridden to change the format specified above.

Usage
=====

To use this module, you need to:

* Edit any partner's form.
* Make sure the partner is not a company.
* Enter firstname and lastnames.

If you directly enter the full name instead of entering the other fields
separately (maybe from other form), this module will try to guess the best
match for your input and split it between firstname, lastname and second
lastname using an inverse function.

If you can, always enter it manually please. Automatic guessing could fail for
you easily in some corner cases.
