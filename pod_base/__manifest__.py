{
    "name": "Podiatry Base",
    "summary": "Podiatry Base",
    "version": "15.0.1.0.0",
    "author": "NWPL",
    "category": "Podiatry",
    "website": "https://nwpodiatric.com",
    "license": "LGPL-3",
    "depends": [
        "base",
        "base_setup",
        "mail", 
        "base_fontawesome", 
        "uom"
        ],
    "data": [
        "security/pod_security.xml",
        "security/ir.model.access.csv",
        "views/res_partner.xml",
        "data/ir_sequence_data.xml",
        "views/pod_menu.xml",
        "views/pod_patient.xml",
        "views/res_config_settings_views.xml",
        # "templates/assets.xml",
    ],
    'assets': {
        'web.assets_backend': [
            'pod_base/static/src/js/one2many_field.js',
        ],
    },
    "demo": ["demo/pod_demo.xml"],
    "application": True,
}
