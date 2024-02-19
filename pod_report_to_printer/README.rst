=================
Report to printer
=================

This module allows users to send reports to a printer attached to the server.

It adds an optional behaviour on reports to send it directly to a printer.

* `Send to Client` is the default behaviour providing you a downloadable PDF
* `Send to Printer` prints the report on selected printer

It detects trays on printers installation plus permits to select the
paper source on which you want to print directly.

Report behaviour is defined by settings.

You will find this option on default user config, on default report
config and on specific config per user per report.

This allows you to dedicate a specific paper source for example for
preprinted paper such as payment slip.

Settings can be configured:

* globally
* per user
* per report
* per user and report


Installation
============

To install this module, you need to:

#. Install PyCups - https://pypi.python.org/pypi/pycups

.. code-block:: bash

   sudo apt-get install cups
   sudo apt-get install libcups2-dev
   sudo apt-get install python3-dev
   sudo pip install pycups

Configuration
=============

To configure this module, you need to:

#. Enable the "Printing / Print User" option under access
   rights to give users the ability to view the print menu.


The jobs will be sent to the printer with a name matching the print_report_name
of the report (truncated at 80 characters). By default this will not be
displayed by CUPS web interface or in Odoo. To see this information, you need
to change the configuration of your CUPS server and set the JobPrivateValue
directive to "none" (or some other list of values which does not include
"job-name") , and reload the server. See `cupsd.conf(5)
<https://www.cups.org/doc/man-cupsd.conf.html>` for details.

Usage
=====

Guidelines for use:

 * To update the CUPS printers in *Settings > Printing > Update Printers
   from CUPS*
 * To print a report on a specific printer or tray, you can change
   these in *Settings > Printing > Reports* to define default behaviour.
 * To print a report on a specific printer and/or tray for a user, you can
   change these in *Settings > Printing > Reports* in
   *Specific actions per user*
 * Users may also select a default action, printer or tray in their preferences.

When no tray is configured for a report and a user, the
default tray setup on the CUPS server is used.
