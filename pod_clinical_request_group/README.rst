=====================
Podiatry Request Group
=====================

The Request Group resource is used to represent a group of optional activities
that may be performed for a specific patient or context. This resource is
often, but not always, the result of applying a specific PlanDefinition to a
particular patient.

Request Groups can contain hierarchical groups of actions, where each
specific action references the action to be performed (in terms of a Request
resource), and each group describes additional behavior, relationships, and
applicable conditions between the actions in the overall group.

For more information about the FHIR Request Group visit: https://www.hl7.org/fhir/requestgroup.html

Installation
============

To install this module, go to 'Podiatry / Configuration / Settings' and inside
'Clinical' activate 'Request groups'.

Usage
=====

#. Go to 'Podiatry / Clinical / Requests / Request groups'
#. Click 'Create'.
#. Fill in the information.
#. Click 'Save'.
