{
    "name": "Safe Box with PoS",
    "version": "15.0.1.0.0",
    "author": "NWPL",
    "depends": ["safe_box", "pos_close_approval", "pos_session_pay_invoice"],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_sequence_data.xml",
        "views/pos_session_validation_views.xml",
        "views/pos_session_views.xml",
        "views/pos_config_views.xml",
        "views/safe_box_group_views.xml",
        "views/safe_box_coin_views.xml",
    ],
    "website": "https://nwpodiatric.com",
    "license": "AGPL-3",
    "installable": True,
    "auto_install": False,
}
