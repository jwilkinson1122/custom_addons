# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Cb Podiatry Diagnostic Report",
    "summary": """Allows the creation of pod diagnostic reports""",
    "version": "15.0.2.0.0",
    "license": "AGPL-3",
    "author": "CreuBlanca",
    "website": "https://github.com/tegin/nwp-pod",
    "depends": [
        "pod_diagnostic_report",
        "pod_base",
        "pod_signature_storage",
        "sequence_parser",
        "pod_encounter_identifier",
        "web_drop_target",
        "web_tree_image_tooltip",
        "storage_file",
    ],
    "data": [
        "data/ir_parameter.xml",
        "security/department_security.xml",
        "security/ir.model.access.csv",
        "data/ir_sequence_data.xml",
        "views/pod_department.xml",
        "views/pod_diagnostic_report_template.xml",
        "views/pod_diagnostic_report.xml",
        "views/pod_report_category.xml",
        "reports/pod_diagnostic_report_template.xml",
        "wizards/pod_diagnostic_report_expand.xml",
        # "templates/assets.xml",
    ],
    'assets': {
        'web.assets_backend': [
            'nwp_pod_diagnostic_report/static/src/js/diagnostic_report_controller.js',
            'nwp_pod_diagnostic_report/static/src/js/diagnostic_report_renderer.js',
            'nwp_pod_diagnostic_report/static/src/js/diagnostic_report_view.js',
            'nwp_pod_diagnostic_report/static/src/scss/diagnostic_report_view.scss',
        ],
        'web.report_assets_common': [
            'nwp_pod_diagnostic_report/static/src/scss/pod_report_layout.scss',
        ],
    },
    "demo": ["demo/pod_diagnostic_report.xml"],
}
