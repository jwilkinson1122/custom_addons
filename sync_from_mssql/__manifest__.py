{
    "name": "Sync From MS SQL SERVER",
    "version": "17.0.1.0.0",
    "license": "OPL-1",
    "summary": "Sync From MSSQL/SQL SERVER",
    "depends": ["base", "pod_partner_hierarchy", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "views/message_wizard.xml",
        "views/dbsync.xml",
        "data/ir_cron.xml",
        "data/crm_all_active_accounts.csv",
        "data/crm_active_parent_accounts.csv",
        "data/crm_active_child_accounts.csv",
        # "data/email_templates.xml",
    ],
    "application": True,
    "installable": True,
}
