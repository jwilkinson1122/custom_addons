

{
    "name": "Podiatry Diagnostic Report",
    "summary": """
        Allows to create reports for patients""",
    "version": "15.0.2.0.0",
    "license": "AGPL-3",
    "author": "NWPL",
    "website": "https://nwpodiatric.com",
    "depends": [
        "pod_administration_encounter",
        "pod_workflow",
        "web_editor",
        "pod_certify",
        "web_widget_bokeh_chart",
        "account",
    ],
    "data": [
        "security/security.xml",
        "wizards/pod_patient_create_diagnostic_report.xml",
        "data/report_paper_format.xml",
        "security/ir.model.access.csv",
        "wizards/patient_concept_evolution.xml",
        "wizards/pod_diagnostic_report_template_print.xml",
        "wizards/pod_diagnostic_report_expand.xml",
        # "templates/assets.xml",
        "views/pod_uom.xml",
        "data/uom.xml",
        "wizards/pod_encounter_create_diagnostic_report.xml",
        "data/ir_sequence_data.xml",
        "views/pod_diagnostic_report.xml",
        "views/pod_diagnostic_report_template.xml",
        "views/pod_encounter.xml",
        "views/pod_observation_concept.xml",
        "views/pod_patient.xml",
        "views/res_users.xml",
        "views/pod_observation_report.xml",
        "reports/pod_diagnostic_report_base.xml",
        "reports/pod_diagnostic_report_template.xml",
        "reports/pod_diagnostic_report_report.xml",
        "reports/pod_diagnostic_report_template_preview.xml",
        "reports/pod_diagnostic_report_report_preview.xml",
    ],
    'assets': {
        'web.assets_backend': [
            'pod_diagnostic_report/static/src/js/list_renderer.js',
            'pod_diagnostic_report/static/src/js/field_dynamic_options_dropdown.js',
            'pod_diagnostic_report/static/src/js/fields.js',
        ],
        'web.report_assets_common': [
            'pod_diagnostic_report/static/src/scss/pod_report_layout.scss',
        ],
    },
    "demo": ["demo/pod_diagnostic_report.xml"],
    "external_dependencies": {"python": ["numpy", "pandas", "bokeh==2.4.2"]},
}
