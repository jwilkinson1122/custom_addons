{
    "name": "Crm Agreement",
    "summary": """
        Link of Podiatry Agreements and CRM""",
    "version": "15.0.1.0.0",
    "license": "AGPL-3",
    "author": "NWPL",
    "website": "https://nwpodiatric.com",
    "depends": [
        "sale_crm",
        "nwp_pod_quote",
        "pod_financial_coverage_agreement",
        "nwp_pod_administration_requester",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/mail_data.xml",
        "views/pod_quote.xml",
        "wizards/crm_lead_add_agreement.xml",
        "views/pod_coverage_agreement.xml",
        "views/crm_lead.xml",
    ],
}
