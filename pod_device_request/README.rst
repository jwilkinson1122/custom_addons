

==========================
Podiatry Device Request
==========================

The resource **Device Request** represents an order or request for both
supply of the device and the instructions for administration of the
device to a patient.

The resource **Device Administration** describes the event of a patient
consuming or otherwise being administered a device. This may be as simple
as swallowing a tablet or it may be a long running infusion. Related
resources tie this event to the authorizing prescription, and the specific
encounter between patient and health care practitioner.

For further information about FHIR Device Request visit: https://www.hl7.org/fhir/devicerequest.html
For further information about FHIR Device Administration visit: https://www.hl7.org/fhir/deviceadministration.html

Installation
============

To install this module, go to 'Podiatry / Configuration / Settings' and inside
'Device' activate 'Device administration & Device requests'.

Usage
=====

#. Go to 'Podiatry / Devices / Requests'
#. Click 'Create' and fill in all the required information.
#. Click 'Save'.
#. Go to 'Podiatry / Devices / Administration'
#. Click 'Create'.
#. Provide a patient, a product, a quantity and a pod location which must
   be already related to a stock location.
#. Click 'Save'.
#. Press the button 'Activate'.
#. Press the button 'Complete'.
#. Press the button 'Stock moves' to see the generated move.
