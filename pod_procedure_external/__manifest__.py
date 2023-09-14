# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Podiatry Procedure External",
    "summary": """
        Allows to create external requests for patients""",
    "version": "15.0.1.0.0",
    "license": "AGPL-3",
    "author": "CreuBlanca,Odoo Community Association (OCA)",
    "website": "https://github.com/tegin/pod-fhir",
    "depends": [
        "pod_workflow",
        "pod_certify",
        "pod_administration_encounter",
    ],
    "data": [
        "data/report_paper_format.xml",
        "data/ir_sequence_data.xml",
        "security/ir.model.access.csv",
        "wizards/pod_encounter_create_procedure_external.xml",
        "views/menu.xml",
        "views/pod_procedure_external_request.xml",
        "views/pod_procedure_external_request_template.xml",
        "views/pod_encounter.xml",
        "views/res_users.xml",
        "views/pod_patient.xml",
        "reports/pod_procedure_external_request_base.xml",
        "reports/pod_procedure_external_request_template.xml",
        "reports/pod_procedure_external_request_report.xml",
        "reports/pod_procedure_external_request_template_preview.xml",
        "reports/pod_procedure_external_request_preview.xml",
        # "templates/assets.xml",
    ],
    'assets': {
        'web.report_assets_common': [
            'pod_procedure_external/static/src/scss/pod_procedure_external_layout.scss',
        ],
    },
    "demo": ["demo/pod_procedure_external.xml"],
}
