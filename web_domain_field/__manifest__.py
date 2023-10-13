{
    "name": "Web Domain Field",
    "summary": """
        Use computed field as domain""",
    "version": "16.0.1.0.1",
    "license": "AGPL-3",
    "author": "NWPL",
    "website": "https://www.nwpodiatric.com",
    "depends": ["web"],
    "data": [],
    "assets": {
        "web.assets_backend": [
            "/web_domain_field/static/lib/js/*.js",
        ],
        "web.qunit_suite_tests": [
            "/web_domain_field/static/tests/**/*.js",
        ],
    },
    "installable": True,
}
