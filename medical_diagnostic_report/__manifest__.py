# Copyright 2021 CreuBlanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Medical Diagnostic Report",
    "summary": """
        Allows to create reports for patients""",
    "version": "14.0.2.0.0",
    "license": "AGPL-3",
    "author": "CreuBlanca,Odoo Community Association (OCA)",
    "website": "https://github.com/tegin/medical-fhir",
    "depends": [
        "medical_administration_encounter",
        "medical_workflow",
        "web_editor",
        "medical_certify",
        "web_widget_bokeh_chart",
        "account",
    ],
    "data": [
        "security/security.xml",
        "wizards/medical_patient_create_diagnostic_report.xml",
        "data/report_paper_format.xml",
        "security/ir.model.access.csv",
        "wizards/patient_concept_evolution.xml",
        "wizards/medical_diagnostic_report_template_print.xml",
        "wizards/medical_diagnostic_report_expand.xml",
        # "templates/assets.xml",
        "views/medical_uom.xml",
        "data/uom.xml",
        "wizards/medical_encounter_create_diagnostic_report.xml",
        "data/ir_sequence_data.xml",
        "views/medical_diagnostic_report.xml",
        "views/medical_diagnostic_report_template.xml",
        "views/medical_encounter.xml",
        "views/medical_observation_concept.xml",
        "views/medical_patient.xml",
        "views/res_users.xml",
        "views/medical_observation_report.xml",
        "reports/medical_diagnostic_report_base.xml",
        "reports/medical_diagnostic_report_template.xml",
        "reports/medical_diagnostic_report_report.xml",
        "reports/medical_diagnostic_report_template_preview.xml",
        "reports/medical_diagnostic_report_report_preview.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "medical_diagnostic_report/static/src/js/list_renderer.js",
            "medical_diagnostic_report/static/src/js/field_dynamic_options_dropdown.js",
            "medical_diagnostic_report/static/src/js/fields.js",
        ],
        'web.report_assets_common': [
            "medical_diagnostic_report/static/src/scss/medical_report_layout.scss",
        ],
    },
    "demo": ["demo/medical_diagnostic_report.xml"],
    "external_dependencies": {"python": ["numpy", "pandas", "bokeh==2.4.2"]},
}
