# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "NWP Podiatry sequence configuration",
    "version": "15.0.1.0.0",
    "author": "Eficent, CreuBlanca",
    "depends": [
        "pod_administration_encounter_careplan",
        "pod_clinical_careplan",
        "pod_clinical_request_group",
        "pod_clinical_procedure",
        "pod_device_request",
        "pod_document",
        "pod_clinical_laboratory",
        "sequence_parser",
        "pod_diagnostic_report",
        "pod_administration_center",
        # "sequence_safe",
    ],
    "demo": ["demo/pod_demo.xml"],
    "data": [
        "data/config_parameter.xml",
        "views/res_partner_views.xml",
        "views/pod_encounter_view.xml",
    ],
    "website": "https://github.com/tegin/nwp-pod",
    "license": "AGPL-3",
    "installable": True,
    "auto_install": False,
    "external_dependencies": {"python": ["numpy", "pandas", "bokeh==2.3.1"]},
}
