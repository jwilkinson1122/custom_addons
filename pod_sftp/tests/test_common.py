import os

from copy import deepcopy
from odoo.tests.common import TransactionCase
from odoo.modules.module import get_resource_path
from pytest_sftpserver.sftp.server import SFTPServer


class TestCommon(TransactionCase):

    @classmethod
    def setUpClass(cls):
        """Method to configure test values"""
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        cls.test_files_dict = {
            'a_folder': {
                'somefile1.txt': 'File content1',
                'somefile2.txt': 'File content2',
                'somefile3.txt': 'File content3',
            },
            'b_folder': {
                'c_folder': {
                    'somefile4.txt': 'File content4',
                },
                'somefile5.txt': 'File content5',
                'somefile6.txt': 'File content6',
            },
            'empty_folder': {},
        }

        cls.sftp_dict = deepcopy(cls.test_files_dict)
        cls.sftpserver = SFTPServer(content_object=cls.sftp_dict)
        cls.sftpserver.start()

        cls.ir_sftp_server = cls.env['ir.sftp_server'].create({
            'name': 'Income SFTP Test Server',
            'url': cls.sftpserver.host,
            'port': cls.sftpserver.port,
            'username': 'user',
            'password': 'pw',
            'server_type': 'in',
            'path_for_connection_test': '/',
        })

    def send_file_by_path_and_check_file(self, file_name, decoding):
        with self.sftpserver.serve_content(deepcopy(self.test_files_dict)):
            local_path = get_resource_path('pod_sftp', 'tests', 'tests_files')
            self.ir_sftp_server.send_file_by_path(local_path, file_name, '/empty_folder')

            files = self.ir_sftp_server.get_files_in_folder('/empty_folder', [file_name])
            self.assertEqual(len(files), 1)
            file = files[0]
            self.assertTrue('error' not in file)
            self.assertTrue('error_msg' not in file)
            self.assertEqual(file['file_name'], file_name)
            with open(os.path.join(local_path, file_name), 'rb') as f:
                self.assertEqual(file['file_content'], f.read().decode(decoding))
