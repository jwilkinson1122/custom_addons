{
    "name": "Filesystem Storage Backend",
    "summary": "Implement the concept of Storage with amazon S3, sftp...",
    "version": "1.0",
    "category": "File Storage",
    "license": "LGPL-3",
    "installable": True,
    "depends": ["base", "base_sparse_field", "server_environment"],
    "data": [
        "views/file_storage_view.xml",
        "security/ir.model.access.csv",
        "wizards/file_test_connection.xml",
    ],
    "demo": ["demo/file_storage.xml"],
    "external_dependencies": {"python": ["fsspec"]},
    # "external_dependencies": {"python": ["fsspec>=2024.5.0"]},
}
