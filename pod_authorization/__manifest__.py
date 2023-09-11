{
    "name": "Podiatry Authorization",
    "summary": "Podiatry financial coverage request",
    "version": "15.0.1.0.0",
    "author": "NWPL",
    "website": "https://nwpodiatric.com",
    "license": "AGPL-3",
    "depends": ["pod_financial_coverage_request"],
    "data": [
        "security/ir.model.access.csv",
        "wizards/pod_request_group_uncheck_authorization.xml",
        "views/pod_authorization_method_view.xml",
        "wizards/pod_request_group_check_authorization_views.xml",
    ],
    "application": False,
    "installable": True,
    "auto_install": False,
}
