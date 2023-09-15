

{
    "name": "Podiatry sequence configuration",
    "version": "15.0.1.0.0",
    "author": "NWPL",
    "depends": [
        "pod_administration_encounter_careplan",
        "pod_clinical_careplan",
        "pod_clinical_request_group",
        "pod_clinical_procedure",
        "pod_device_request",
        "pod_document",
        "pod_clinical_laboratory",
        "sequence_parser",
        # "pod_diagnostic_report",
        "pod_administration_center",
        # "sequence_safe",
    ],
    "demo": ["demo/pod_demo.xml"],
    "data": [
        "data/config_parameter.xml",
        "views/res_partner_views.xml",
        "views/pod_encounter_view.xml",
    ],
    "website": "https://nwpodiatric.com",
    "license": "AGPL-3",
    "installable": True,
    "auto_install": False,
    "external_dependencies": {"python": ["numpy", "pandas", "bokeh==2.4.2"]},
}
