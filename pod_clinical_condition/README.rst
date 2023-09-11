=================
Podiatry Condition
=================

This resource is used to record detailed information about a condition,
problem, diagnosis, or other event, situation, issue, or clinical concept
that has risen.

It can be used to record information about a disease/illness identified from
application of clinical reasoning over the pathologic and pathophysiologic
findings (diagnosis), or identification of health issues/situations that a
practitioner considers harmful, potentially harmful and may be investigated
and managed (problem), or other health issue/situation that may require
ongoing monitoring and/or management (health issue/concern).

For further information about FHIR Condition visit: https://www.hl7.org/fhir/condition.html


TODO:

* Decide if field pod_condition_ids should contain allergies or not. On one side, allergies are pod.condition records. On the other hand, the information is repeated and can cause confusion as the conditions can be seen from the "Condition" button and the "Allergies" button.
* If finally pod_condition_ids do not contain allergies, the warning_dropdowm from pod_clinical_impression should be modified, as it is computed with the pod_condition_ids.

**Table of contents**

.. contents::
   :local:

Installation
============

To install this module, go to 'Podiatry / Configuration / Settings' and inside
'Clinical' activate 'Podiatry condition'.

Usage
=====

#. Go to 'Podiatry / Terminologies / Clinical Finding Codes'
#. Click 'Create'.
#. Provide a name and (if desired) a description and a Sct Code. You can also select if this finding should create a warning.
#. Click 'Save'.
#. Go to 'Podiatry / Terminologies / Allergy Substance Codes'
#. Click 'Create'.
#. Provide a name and (if desired) a description and a Sct Code. You can also select if this substance should create a warning.
#. Click 'Save'.
#. Go to 'Podiatry / Administration / Patients' or to 'Podiatry / Administration / Encounters'
#. Select a patient/encounter and create a condition or an allergy.
#. You can view conditions, allergies and warnings from encounter or patient through smart buttons.
