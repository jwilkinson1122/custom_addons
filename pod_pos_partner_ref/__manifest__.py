{
    "name": "NWPL Pos - Partner contact ref",
    "summary": "Adds the partner ref in the customer screen of POS",
    "version": "17.0.0.0.0",
    "category": "Point of sale",
    "website": "https://www.nwpodiatric.com",
    "author": "NWPL",
    "license": "LGPL-3",
    "installable": True,
    "depends": [
        "point_of_sale",
    ],
    "assets": {
        "point_of_sale._assets_pos": [
            "pod_pos_partner_ref/static/src/xml/screens.xml",
            "pod_pos_partner_ref/static/src/js/ClientDetailsEdit.esm.js",
            "pod_pos_partner_ref/static/src/js/PosDB.esm.js",
        ]
    },
}
