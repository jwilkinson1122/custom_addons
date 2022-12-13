# NH Clinical
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/40c8b82dfcc74bba88c4e02770323039)](https://www.codacy.com/app/BJSS/nhclinical?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=NeovaHealth/nhclinical&amp;utm_campaign=Badge_Grade)

NHClinical is a set of [Odoo](https://www.odoo.com/) modules that add clinical models 
and functionality to Odoo.

NHClinical adds clinical models and functionality such as:
- Clinical Activities
- Clinical Locations
- Clinical User Groups
- Patients
- Patient Admission, Discharge and Transfer
- Patient Visits
- Ward Staff Management

These models create a basic hospital set up but it's recommended to install
[Open-eObs](https://github.com/NeovaHealth/openeobs) which adds all the functionality
needed to run an Acute or Mental Health hospital.

## Installation
We currently develop against [our own tag of Odoo](https://github.com/bjss/odoo/tree/liveobs_1.11.1), 
this is to ensure consistency so it's recommended when installing Odoo that you 
install this version.

Once you've downloaded Odoo, installed it's dependencies and installed PostgreSQL 9.3
you need to update the `server.cfg` file of your Odoo installation to point to 
the NhClinical directory.

After restarting the server you can then log in as the admin user and install the
`nh_clinical` module. This installs the different models you can work with.

## Contributing
We welcome contributions via the creation of issues (for feedback, bugs and suggestions)
and pull requests (for submitting code). 

You can read our contribution guidelines for more information on how to contribute
and what you can expect when contributing to NHClinical.

