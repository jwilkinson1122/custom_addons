{
    "name": "Base Fontawesome",
    "summary": """Up to date Fontawesome resources.""",
    "version": "15.0.5.15.4",
    "license": "LGPL-3",
    "website": "https://nwpodiatric.com",
    "author": "NWPL",
    "depends": ["web"],
    "assets": {
        "web.assets_common": [
            (
                "replace",
                "web/static/lib/fontawesome/css/font-awesome.css",
                "base_fontawesome/static/src/css/fontawesome.css",
            ),
            "base_fontawesome/static/lib/fontawesome-5.15.4/css/all.css",
            "base_fontawesome/static/lib/fontawesome-5.15.4/css/v4-shims.css",
            "base_fontawesome/static/src/js/form_renderer.js",
            "base_fontawesome/static/src/js/list_renderer.js",
        ],
        "web.report_assets_common": [
            (
                "replace",
                "web/static/lib/fontawesome/css/font-awesome.css",
                "base_fontawesome/static/src/css/fontawesome.css",
            ),
            "base_fontawesome/static/lib/fontawesome-5.15.4/css/all.css",
            "base_fontawesome/static/lib/fontawesome-5.15.4/css/v4-shims.css",
        ],
    },
}
