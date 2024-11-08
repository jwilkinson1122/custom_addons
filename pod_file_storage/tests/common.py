import base64
import os
import shutil
import tempfile
from unittest import mock

from odoo.tests.common import TransactionCase

from ..models.file_storage import FileStorage


class TestFileStorageCase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.backend: FileStorage = cls.env.ref("pod_file_storage.default_file_storage")
        cls.backend.json_options = {"target_options": {"auto_mkdir": "True"}}
        cls.filedata = base64.b64encode(b"This is a simple file")
        cls.filename = "test_file.txt"
        cls.case_with_subdirectory = "subdirectory/here"
        cls.demo_user = cls.env.ref("base.user_demo")
        cls.temp_dir = tempfile.mkdtemp()

    def setUp(self):
        super().setUp()
        mocked_backend = mock.patch.object(
            self.backend.__class__, "_get_filesystem_storage_path"
        )
        mocked_get_filesystem_storage_path = mocked_backend.start()
        mocked_get_filesystem_storage_path.return_value = self.temp_dir
        self.backend.write({"directory_path": self.temp_dir})

        # pylint: disable=unused-variable
        @self.addCleanup
        def stop_mock():
            mocked_backend.stop()
            # recursively delete the tempdir
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)

    def _create_file(self, backend: FileStorage, filename: str, filedata: str):
        with backend.file.open(filename, "wb") as f:
            f.write(filedata)
