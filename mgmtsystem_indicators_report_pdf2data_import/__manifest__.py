

{
    "name": "Mgmtsystem Indicators Report Pdf2data Import",
    "summary": """
        This addon allows to create a indicators report
        extracting the data from a pdf""",
    "version": "15.0.1.0.0",
    "license": "AGPL-3",
    "author": "NWPL",
    "website": "https://nwpodiatric.com",
    "depends": ["mgmtsystem_indicators_report", "edi_pdf2data_oca"],
    "data": [
        "views/pdf2data_template.xml",
        "views/mgmtsystem_menu.xml",
        "data/edi_pdf2data_type.xml",
    ],
    "demo": [],
}
