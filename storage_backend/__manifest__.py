{
    "name": "Storage Bakend",
    "summary": "Implement the concept of Storage with amazon S3, sftp...",
    "version": "15.0.1.0.2",
    "category": "Storage",
    "website": "https://www.nwpodiatric.com",
    "author": "NWPL",
    "license": "LGPL-3",
    "installable": True,
    "depends": ["base", "component", "server_environment"],
    "data": [
        "views/backend_storage_view.xml",
        "data/data.xml",
        "security/ir.model.access.csv",
    ],
}
