==========================
Podiatry Prescription Request
==========================

The resource **Prescription Request** represents an order or request for a prescription.

The resource **Prescription Administration** describes the event of a patient
being administered a prescription. Related resources tie this event to the 
authorizing prescription, and the specific
encounter between patient and health care practitioner.

For further information about FHIR Prescription Request visit: https://www.hl7.org/fhir/prescriptionrequest.html
For further information about FHIR Prescription Administration visit: https://www.hl7.org/fhir/prescriptionadministration.html

Installation
============

To install this module, go to 'Podiatry / Configuration / Settings' and inside
'Prescription' activate 'Prescription administration & Prescription requests'.

Usage
=====

#. Go to 'Podiatry / Prescriptions / Requests'
#. Click 'Create' and fill in all the required information.
#. Click 'Save'.
#. Go to 'Podiatry / Prescriptions / Administration'
#. Click 'Create'.
#. Provide a patient, a product, a quantity and a pod location which must
   be already related to a stock location.
#. Click 'Save'.
#. Press the button 'Activate'.
#. Press the button 'Complete'.
#. Press the button 'Stock moves' to see the generated move.
