{
    "name": "Pos Manual Order",
    "summary": """
        Add Orders manually on a PoS Session""",
    "version": "15.0.1.0.0",
    "website": "https://nwpodiatric.com",
    "license": "AGPL-3",
    "author": "NWPL",
    "depends": ["point_of_sale"],
    "data": [
        "security/ir.model.access.csv",
        "wizards/pos_session_add_order.xml",
        "views/pos_session.xml",
    ],
}
