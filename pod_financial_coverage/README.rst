================
Podiatry Coverage
================

The **Coverage** Resource represents a Financial instrument which may be used
to reimburse or pay for health care products and services.

The Coverage resource is intended to provide the high level identifiers and
potentially descriptors of an insurance plan which may used to pay for, in
part or in whole, the provision of health care products and services.

This resource may also be used to register 'SelfPay' where an individual or
organization other than an insurer is taking responsibility for payment for a
portion of the health care costs.

The **Payor** Resorce represents the identity of the insurer or party paying
for services.

For more information about the FHIR Coverage visit: https://www.hl7.org/fhir/coverage.html
For more information about the FHIR Payor visit: https://www.hl7.org/fhir/coverage-definitions.html#Coverage.payor

Installation
============

To install this module, go to 'Podiatry / Configuration / Settings' and inside
'Financial' activate 'Covarages'.

Usage
=====

#. Go to 'Podiatry / Financial / Payors'
#. Click 'Create'.
#. Fill in the information.
#. Click 'Save'.
#. Go to 'Podiatry / Financial / Coverage Template'
#. Click 'Create'.
#. Provide a name for that template and a payor.
#. Click 'Save'.
#. Go to 'Podiatry / Financial / Coverage'
#. Click 'Create'.
#. Provide a patient, a subscriber id and a coverage template.
#. Click 'Save'.

