===========================
Podiatry Clinical Impression
===========================

This module allows to create clinical impressions from patient and encounter. According to the HL7 standard, a clinical
impression is a record of a a clinical assessment performed to determine what problem(s) may affect the patient.

https://www.hl7.org/fhir/clinicalimpression.html

We use this concept to create part of the clinical history of the patient.

Some of the features of this module are:

* Create clinical impressions from patient and encounter and group them by pod specialities.
* Clinical findings and allergies can be added in these impressions. If those clinical findings have been previously configured to create conditions, when the impression is validated, those findings and allergies will create automatically conditions and allergies for that patient.
* Create the family history of the patient from patient and encounter.
* A report with impression/s can be printed. Private notes can be added to the impression, and those will not be added to the report, ss it represents that are comments that only the practitioner/s should see.
* A warning dropdown in patient and impression view has been added, in order to see fast warnings for this patient, like if she is pregnant, or they have a pacemaker...

TODO:

* Security
    * Who should create, view and edit impressions?
    * A practitioner can edit a impressions from other practitioner?
    * Enable that a impression can only be cancelled by who created it.


Usage
=====

#. Create a clinical finding and mark the field "create_condition_from_clinical_impression" in those which should create conditions automatically from impression.
#. Create an encounter for the patient.
#. Create a new impression:
    * If there are not impressions yet for a speciality, press the button "Create impression", choose a specialty and the encounter. The encounter can be changed and if it is older than a week a warning will appear. Then, click "Create". You can always use this wizard, even if there are already impressions for that specialty.
    * Once there are already impressions of that specialty for a patient, you  can access them from the stethoscope button found on the patient impressions page. Once there, pressing the "Create button" you can create impressions of that specialty.
#. Complete all the desired fields of the impression, also add findings or allergies if desired.
#. When everything is completed, validate the impression. Once validated, it can not be edited. The findings added whose create_condition_from_clinical_impression field was marked as true, will create a condition. The allergies added will also create a allergy.
#. The impression can also be cancelled. The related conditions and allergies created will be desactivated.
#. If desired, create a family history record from the button "Create Family History" at the patient or encounter view.
