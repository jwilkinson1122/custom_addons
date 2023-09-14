================
Podiatry Workflow
================

The Workflow Module focuses on the coordination of activities within and
across systems.

In addition to the Task resource, this specification defines three logical
models - Definition, `Request <https://www.hl7.org/fhir/request.html>`_ and
`Event <https://www.hl7.org/fhir/event.html>`_ that define the patterns for
resources that are typically involved in workflow. These patterns include
elements defining common attributes of each type of resource as well as
relationships between them.

Finally the `Plan definition <https://www.hl7.org/fhir/plandefinition.html>`_
and `Activity definition <https://www.hl7.org/fhir/activitydefinition.html>`_
resources combine to support the creation of protocols, orders sets,
guidelines and other workflow definitions by describing the types of
activities that can occur and setting rules about their composition,
sequencing, interdependencies and flow.

For more information about the FHIR Workflow model visit: https://www.hl7.org/fhir/workflow-module.html

Installation
============

#. To install this module, go to 'Podiatry / Configuration / Settings' and inside
   'Workflow' activate 'Workflow'.

Usage
=====

#. Go to 'Podiatry / Workflow / Workflow Types'
#. Click 'Create' and fill in all the required information.
#. Click 'Save'.
#. Go to 'Podiatry / Workflow / Activity definitions'
#. Click 'Create' and fill in all the required information.
#. Click 'Save'.
#. Go to 'Podiatry / Workflow / Plan definitions'
#. Click 'Create'.
#. Provide a name and create actions by providing a name and an Activity
   Definition or a Plan Definition.
#. Click 'Save'.

Plan definition on patients
---------------------------
#. Go to 'Podiatry / Configuration / Settings' and inside
   'Workflow' activate 'Plan definition on patients'.
#. Go to 'Podiatry / Administration / Patients'
#. Select a patient and press the button 'Add Plan definition'. Automatically
   the requests are generated.

Main activity on plan definitions
---------------------------------
#. Go to 'Podiatry / Configuration / Settings' and inside
   'Workflow' activate 'Main activity on plan definition'.
#. Go to 'Podiatry / Workflow / Plan definitions'
#. Add an activity definition to the plan.
