from base64 import b64encode
from copy import deepcopy

from odoo.exceptions import AccessError, UserError
from .test_common import TestCommon


class TestIrSftpServer(TestCommon):

    @classmethod
    def setUpClass(cls):
        super(TestIrSftpServer, cls).setUpClass()

    def test_001_correct_path(self):
        self.ir_sftp_server._check_path('/')
        self.ir_sftp_server._check_path('/folder1')
        self.ir_sftp_server._check_path('/folder1/')
        self.ir_sftp_server._check_path('/folder1/folder2')
        self.ir_sftp_server._check_path('/folder1/folder2/')

    def test_002_wrong_path(self):
        with self.assertRaises(UserError):
            self.ir_sftp_server._check_path('')

        with self.assertRaises(UserError):
            self.ir_sftp_server._check_path('folder1')

        with self.assertRaises(UserError):
            self.ir_sftp_server._check_path('folder1/folder2')

    def test_003_successful_connection(self):
        self.ir_sftp_server.test_get_connection()

    def test_004_connection_wrong_url(self):
        self.ir_sftp_server.url = '127.0.0.1/no-existing-url'

        with self.assertRaises(UserError):
            self.ir_sftp_server.test_get_connection()

    def test_005_connection_wrong_port(self):
        self.ir_sftp_server.port += 10

        with self.assertRaises(AccessError):
            self.ir_sftp_server.test_get_connection()

    def test_006_connection_wrong_path(self):
        with self.assertRaises(UserError):
            self.ir_sftp_server.get_connection('/no_existing_folder')

    def test_007_list_files(self):
        file_names = self.ir_sftp_server.list_files('/a_folder')
        self.assertEqual(file_names, list(self.test_files_dict['a_folder'].keys()))

    def test_008_list_files_without_folders(self):
        file_names = self.ir_sftp_server.list_files('/b_folder')
        self.assertEqual(file_names, ['somefile5.txt', 'somefile6.txt'])

    def test_009_list_files_empty_folder(self):
        file_names = self.ir_sftp_server.list_files('/')
        self.assertEqual(file_names, [])

    def test_010_get_files_in_folder(self):
        files = self.ir_sftp_server.get_files_in_folder('/a_folder')
        folder_dict = self.test_files_dict['a_folder']
        for file in files:
            self.assertTrue('error' not in file)
            self.assertTrue('error_msg' not in file)
            self.assertTrue(file['file_name'] in folder_dict)
            self.assertEqual(file['file_content'], folder_dict[file['file_name']])

        self.assertEqual(len(files), 3)

    def test_011_get_specific_file_in_folder(self):
        files = self.ir_sftp_server.get_files_in_folder('/a_folder', ['somefile1.txt'])
        self.assertEqual(len(files), 1)
        folder_dict = self.test_files_dict['a_folder']
        file = files[0]
        self.assertTrue('error' not in file)
        self.assertTrue('error_msg' not in file)
        self.assertTrue(file['file_name'] in folder_dict)
        self.assertEqual(file['file_content'], folder_dict[file['file_name']])

    def test_012_get_files_in_folder_with_error(self):
        file_names = ['somefile5.txt', 'somefile6.txt', 'not_existing_file.txt']
        with self.assertRaises(FileNotFoundError):
            self.ir_sftp_server.get_files_in_folder('/b_folder', file_names)

    def test_013_remove_files_in_folder(self):
        with self.sftpserver.serve_content(deepcopy(self.test_files_dict)):
            files = self.ir_sftp_server.remove_files_in_folder('/a_folder')
            folder_dict = self.test_files_dict['a_folder']

            for file in files:
                self.assertTrue('error' not in file)
                self.assertTrue('error_msg' not in file)
                self.assertTrue(file['file_name'] in folder_dict)

            self.assertEqual(len(files), len(folder_dict))
            self.assertEqual(self.ir_sftp_server.list_files('/a_folder'), [])

    def test_014_remove_specific_file_in_folder(self):
        with self.sftpserver.serve_content(deepcopy(self.test_files_dict)):
            files = self.ir_sftp_server.remove_files_in_folder('/a_folder', ['somefile1.txt'])
            self.assertEqual(len(files), 1)
            file = files[0]
            self.assertTrue('error' not in file)
            self.assertTrue('error_msg' not in file)
            self.assertEqual(file['file_name'], 'somefile1.txt')
            self.assertEqual(len(self.ir_sftp_server.list_files('/a_folder')), 2)

    def test_015_remove_files_in_folder_with_error(self):
        with self.sftpserver.serve_content(deepcopy(self.test_files_dict)):
            folder_dict = self.test_files_dict['b_folder']
            file_names = ['somefile5.txt', 'somefile6.txt', 'not_existing_file.txt']
            files = self.ir_sftp_server.remove_files_in_folder('/b_folder', file_names)

            for file in files:
                if file['file_name'] == 'not_existing_file.txt':
                    self.assertTrue('error' in file)
                    self.assertTrue('error_msg' in file)
                else:
                    self.assertTrue('error' not in file)
                    self.assertTrue('error_msg' not in file)
                    self.assertTrue(file['file_name'] in folder_dict)

            self.assertEqual(len(files), len(file_names))
            self.assertEqual(self.ir_sftp_server.list_files('/b_folder'), [])

    def test_016_send_files_by_binary_data(self):
        with self.sftpserver.serve_content(deepcopy(self.test_files_dict)):
            decoded_content = ['Test message1', 'Test message2']
            files_data = [
                {
                    'file_name': 'file1.txt',
                    'binary_file': b64encode(decoded_content[0].encode()),
                },
                {
                    'file_name': 'file2.txt',
                    'binary_file': b64encode(decoded_content[1].encode()),
                }
            ]
            self.ir_sftp_server.send_files_by_binary_data(files_data, '/empty_folder')

            files = self.ir_sftp_server.get_files_in_folder('/empty_folder', [x['file_name'] for x in files_data])
            self.assertEqual(len(files), 2)

            for index, file in enumerate(files):
                self.assertTrue('error' not in file)
                self.assertTrue('error_msg' not in file)
                self.assertEqual(file['file_name'], files_data[index]['file_name'])
                self.assertEqual(file['file_content'], decoded_content[index])

    def test_017_send_csv_file_by_path(self):
        file_name = '001_sample_file.csv'
        self.send_file_by_path_and_check_file(file_name, 'utf-8')

    def test_018_send_xls_file_by_path(self):
        file_name = '002_sample_file.xls'
        self.send_file_by_path_and_check_file(file_name, 'ISO-8859-1')

    def test_019_get_matching_folders(self):
        """Check that the folders are properly matched by unix path"""
        with self.sftpserver.serve_content(deepcopy(self.test_files_dict)):
            matching_folders = self.ir_sftp_server.get_matching_folders('/*folder')
            self.assertIn('/a_folder', matching_folders)
            self.assertIn('/b_folder', matching_folders)
            self.assertIn('/empty_folder', matching_folders)
            # TODO: IS THIS THE BEHAVIOUR WE SHOULD EXPECT?, SINCE IT IS NOT THE GLOB ONE
            self.assertIn('/b_folder/c_folder', matching_folders)

            matching_folders = self.ir_sftp_server.get_matching_folders('/*/*folder')
            self.assertIn('/b_folder/c_folder', matching_folders)
            self.assertNotIn('/b_folder', matching_folders)
