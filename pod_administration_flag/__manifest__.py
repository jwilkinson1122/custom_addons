# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Podiatry Patient Flag",
    "version": "15.0.1.0.0",
    "author": "Eficent, CreuBlanca",
    "depends": ["pod_base"],
    "data": [
        "data/ir_sequence_data.xml",
        "security/pod_security.xml",
        "security/ir.model.access.csv",
        "views/pod_patient_views.xml",
        "views/pod_flag_views.xml",
        "views/pod_flag_category_views.xml",
    ],
    "demo": [],
    "website": "https://github.com/tegin/nwp-pod",
    "license": "AGPL-3",
    "installable": True,
    "auto_install": False,
}
