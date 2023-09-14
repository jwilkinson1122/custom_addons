

{
    "name": "Web Register Login",
    "summary": """
        Register Logins""",
    "version": "15.0.1.0.0",
    "license": "AGPL-3",
    "author": "NWPL",
    "website": "https://nwpodiatric.com",
    "depends": ["base_remote"],
    "data": [
        "security/ir.model.access.csv",
        "security/res_users_access_log_security.xml",
        "views/base_remote.xml",
        "views/res_users_access_log.xml",
        "views/res_users.xml",
    ],
}
