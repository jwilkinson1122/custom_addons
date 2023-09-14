

{
    "name": "Podiatry Diagnostic Report Graph",
    "summary": """
        This addons enables to add a graph to the pod diagnostic report""",
    "version": "15.0.1.0.0",
    "license": "AGPL-3",
    "author": "NWPL",
    "website": "https://nwpodiatric.com",
    "depends": ["pod_diagnostic_report"],
    "data": [
        "views/pod_diagnostic_report_template.xml",
        "views/pod_diagnostic_report.xml",
        "reports/pod_diagnostic_report_base.xml",
        "reports/pod_diagnostic_report_template.xml",
    ],
    "demo": ["demo/auditory_test.xml", "demo/visual_acuity_test.xml"],
    "external_dependencies": {
        "python": [
            "bokeh",
            "numpy",
            "pandas",
            "selenium",
            "chromedriver-binary",
        ]
    },
}
