==================
Podiatry Commission
==================

This module allows you to define fixed or variable fees on pod
services through actions. Commissions can be changed on Procedure Requests or
Procedures.

It also adds the commission agent field to practitioners in order to settle
the commissions to that agent once the service has been provided.

Installation
============

To install this module, simply follow the standard install process.

Usage
=====

Define service's fee
--------------------

#. Go to Podiatry / Workflow / Activity definition
#. Click on Resource Product and activate the boolean 'Podiatry Commissions'
#. Go to an action with that activity definition and specify the fixed or
   the variable fee for that service.

Add commission agent to a practitioner
--------------------------------------

#. Go to Sales / Commissions Management / Agents
#. Remove the filter 'Agents'
#. Search or create a partner that has to be the agent. Inside the partner
   view form, go to the 'Sales & Purchases' page and activate the flag 'Agent'
#. Go to Podiatry / Practitioners
#. Select the practitioner and inside the 'Commission Agents page' select the
   agent(s) for that practitioner.

Create a Procedure
------------------

#. Generate a Procedure with that service
#. Select the practitioner and if the practitioner only has one agent it is
   automatically set as Commission Agent in the page 'Commission Agent' in
   the form view. If more than one, select one from the given options.


Known Issues / Roadmap
======================

* The python files `sale_order.py`, `sale_order_line.py` and `account_move.py`
  can't be tested at the moment. They are pending to review when the module
  `careplan_sale` is ready.
