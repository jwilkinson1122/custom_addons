import base64
import fnmatch
import logging
import os
import re
import stat
from io import BytesIO
from stat import S_ISREG

import paramiko
from paramiko.ssh_exception import SSHException

from odoo import _, api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError

_logger = logging.getLogger(__name__)
DIR_PATH_REGEX = r'^\/.*$'
DEFAULT_TIMEOUT = 300
# Key types allow by default with paramiko
KEY_TYPES = [
    ("ssh-ed25519", "SSH-ED25519"),
    ("ecdsa-sha2-nistp256", "ECDSA-SHA2-NISTP256"),
    ("ecdsa-sha2-nistp384", "ECDSA-SHA2-NISTP384"),
    ("ecdsa-sha2-nistp521", "ECDSA-SHA2-NISTP521"),
    ("ssh-rsa", "SSH-RSA"),
    ("ssh-dss", "SSH-DSS"),
]


def paramiko_glob(path, pattern, sftp):
    """Search recursively for directories / files matching a given unix pattern.

    Parameters:
        path (str): Path to directory on remote machine.
        pattern (str): Python unix pattern.
        sftp (SFTPClient): paramiko SFTPClient.
    """
    root = sftp.listdir(path)
    file_list = []
    dir_list = []

    for f in (os.path.join(path, entry) for entry in root):
        f_stat = sftp.stat(f)
        # If it is a directory call paramiko_glob recursively.
        if stat.S_ISDIR(f_stat.st_mode):
            if fnmatch.fnmatch(f, pattern):
                dir_list.append(f)
            files, dirs = paramiko_glob(f, pattern, sftp)
            file_list += files
            dir_list += dirs
        # if it is a file, check the name pattern and append it to file_list.
        elif fnmatch.fnmatch(f, pattern):
            file_list.append(f)
    return file_list, dir_list


class IrSftpServer(models.Model):
    _name = "ir.sftp_server"
    _description = "Sftp Server"

    name = fields.Char(required=True, index=True)
    active = fields.Boolean(default=True)
    url = fields.Char(required=True)
    port = fields.Integer(required=True, default=22)
    username = fields.Char(required=True)
    password = fields.Char(required=True)
    timeout = fields.Integer(
        default=DEFAULT_TIMEOUT,
        help="If no timeout selected the default value is 300 seconds.",
    )
    server_type = fields.Selection([("in", "Incoming"), ("out", "Outgoing")], default='out')
    fingerprint = fields.Char(help='If this field is filled out, it adds the key to the authentication.')
    key_type = fields.Selection(
        KEY_TYPES,
        default="ssh-rsa",
        help='This needs to be filled out, if fingerprint is set (ex. ssh-rsa)',
    )
    path_for_connection_test = fields.Char(help='This sets the path to use for executing the connection test. '
                                                'It uses ssh-rsa if nothing is set.')

    @api.constrains("timeout")
    def _check_timeout(self):
        for record in self:
            if record.timeout and record.timeout < 0:
                raise ValidationError(_("Timeout must be equal or greater than 0."))

    # pylint: disable=R0201
    @api.model
    def _check_path(self, path):
        if re.match(DIR_PATH_REGEX, path) is None:
            raise UserError(_('Invalid directory path for SFTP connection: %s. All path must start with /.', path))

    def test_get_connection(self):
        sftp, transport = self.get_connection(self.path_for_connection_test)
        with sftp, transport:
            pass

    # TODO: check how to test this.
    def get_connection(self, path='/'):
        """Returns an sftp connection pointing to the given path or /"""
        self.ensure_one()
        self._check_path(path)
        transport = None
        sftp = None
        timeout = self.timeout or DEFAULT_TIMEOUT
        try:
            transport = paramiko.Transport((self.url, self.port))
            self._connect(
                transport,
                timeout=timeout,
                fingerprint=self.fingerprint,
                key_type=self.key_type,
                username=self.username,
                password=self.password,
            )
            sftp = paramiko.SFTPClient.from_transport(transport)
            sftp.get_channel().settimeout(timeout)
            sftp.chdir(path)
            return sftp, transport
        except SSHException:
            if transport:
                transport.close()
            if sftp:
                sftp.close()
            raise AccessError(_("Connection \'%s\' failed! Please check parameters.", self.name))
        except IOError:
            if transport:
                transport.close()
            if sftp:
                sftp.close()
            raise UserError(_('Invalid remote path: %s.', path))

    # pylint: disable=R0913
    def _connect(
            self,
            transport,
            timeout=timeout,
            fingerprint="",
            key_type="",
            username="",
            password=None,
            pkey=None,
            gss_host=None,
            gss_auth=False,
            gss_kex=False,
            gss_deleg_creds=True,
            gss_trust_dns=True,
    ):
        """Customization of paramiko connect to reduce the amount
        of connections needed to check the fingerprint. For more
        info check https://docs.paramiko.org/en/stable/api/transport.html#paramiko.transport.Transport.connect"""
        evaluate_fingerprint = fingerprint and key_type
        if evaluate_fingerprint:
            transport._preferred_keys = [key_type]
        transport.set_gss_host(
            gss_host=gss_host,
            trust_dns=gss_trust_dns,
            gssapi_requested=gss_kex or gss_auth,
        )
        transport.start_client(timeout=timeout)
        if evaluate_fingerprint:
            key = transport.get_remote_server_key()
            if (
                    key.get_name() != key_type or
                    key.get_fingerprint().hex() != fingerprint.replace(':', '')
            ):
                raise AccessError(_("Connection \'%s\' failed! Fingerprint is not valid.", self.name))
        if (pkey is not None) or (password is not None) or gss_auth or gss_kex:
            if gss_auth:
                transport.auth_gssapi_with_mic(
                    username, transport.gss_host, gss_deleg_creds
                )
            elif gss_kex:
                transport.auth_gssapi_keyex(username)
            elif pkey is not None:
                transport.auth_publickey(username, pkey)
            else:
                transport.auth_password(username, password)

    def get_matching_folders(self, unix_path):
        """Returns a list of the folders matching the given unix path"""
        sftp, transport = self.get_connection()
        with sftp, transport:
            file_list, dir_list = paramiko_glob('/', unix_path, sftp)
            return dir_list

    def send_file_by_path(self, local_path, file_name, remote_path='/', remote_file_name=None):
        """Given a local path for a file it sends it to the remote server"""
        self.ensure_one()
        if not local_path or not file_name:
            raise UserError(_('Missing file path or file name.'))
        if not remote_file_name:
            remote_file_name = file_name
        sftp, transport = self.get_connection(remote_path)
        with sftp, transport:
            path = os.path.join(local_path, file_name)
            sftp.put(path, remote_file_name)

    def send_files_by_binary_data(self, files_data, remote_path='/'):
        """Given the binary content, it sends the file to the remote system.

        :param files_data: files to be write in the remote system. Structured as list of dicts [{
            'binary_file': data to be writen in the remote system.
            'file_name': file name for the remote system
        }]
        :param remote_path: global path to the remote folder where the files will be written.
        """
        self.ensure_one()
        sftp, transport = self.get_connection(remote_path)
        with sftp, transport:
            for files_data in files_data:
                with BytesIO(base64.b64decode(files_data['binary_file'])) as file:
                    sftp.putfo(file, files_data['file_name'])

    def get_files_in_folder(self, remote_path="/", file_names=None, encoding=None):
        """Downloads given files present in a given folder or all files in a given folder"""
        self.ensure_one()
        res = []
        if encoding:
            encodings = [encoding, 'utf-8', 'utf-16', 'ISO-8859-1']
        else:
            encodings = ['utf-8', 'utf-16', 'ISO-8859-1']
        sftp, transport = self.get_connection(remote_path)
        with sftp, transport:
            file_names = file_names or self.list_files_from_open_connection(sftp)
            for file_name in file_names:
                with BytesIO() as file:
                    sftp.getfo(file_name, file)
                    file.seek(0)
                    content = file.read()
                    for enc in encodings:
                        try:
                            content = content.decode(enc)
                        except UnicodeDecodeError:
                            pass
                        else:
                            break
                    res.append({"file_name": file_name, "file_content": content})
        return res

    @api.model
    def list_files_from_open_connection(self, sftp):
        """List only all files and no folders from the current directory of the sftp client"""
        return [entry.filename for entry in sftp.listdir_attr() if S_ISREG(entry.st_mode)]

    def list_files(self, remote_path="/"):
        """List all files in a given path"""
        self.ensure_one()
        sftp, transport = self.get_connection(remote_path)
        with sftp, transport:
            return self.list_files_from_open_connection(sftp)

    def remove_files_in_folder(self, remote_path="/", file_names=None):
        """Remove given files present in a given folder or all files in a given folder"""
        self.ensure_one()
        res = []
        sftp, transport = self.get_connection(remote_path)
        with sftp, transport:
            file_names = file_names or self.list_files_from_open_connection(sftp)
            error_msg_format = _('Error during removing the file "%s" from the folder "%s": %s')
            for file_name in file_names:
                try:
                    sftp.remove(file_name)
                    res.append({"file_name": file_name})
                except Exception as e:
                    error_msg = error_msg_format % (file_name, remote_path, str(e))
                    res.append({"file_name": file_name, "error": e, "error_msg": error_msg})
        return res
