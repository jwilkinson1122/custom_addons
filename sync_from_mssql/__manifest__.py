{
    "name": "Sync From MS SQL SERVER",
    "version": "17.0.1.0.0",
    "license": "OPL-1",
    "summary": "Sync From MSSQL/SQL SERVER",
    "depends": ["base"],
    "data": [
        "security/ir.model.access.csv",
        "views/message_wizard.xml",
        "views/dbsync.xml",
        "data/ir_cron.xml",
        # "data/email_templates.xml",
    ],
    "application": True,
    "installable": True,
}
