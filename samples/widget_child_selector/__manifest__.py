# -*- coding: utf-8 -*-

{
    "name": "Widget Child Selector M2O",
    "summary": "Widget used for navigation on hierarchy field Many2one",
    "version": "1.0",
    "license": "OPL-1",
    "depends": ["web"],
    "assets": {
        "web.assets_backend": [
            "/widget_child_selector/static/src/scss/widget_child_selector.scss",
            "/widget_child_selector/static/src/js/widget_child_selector.js",
        ],
        "web.assets_qweb": [
            "/widget_child_selector/static/src/xml/widget_child_selector.xml"
        ],
    },
    "installable": True,
    "application": True,
    "auto_install": False,
}
