import os
import paramiko
from datetime import datetime
from odoo import models, fields, api
from odoo.exceptions import ValidationError
import logging
import keyring

keyring.set_keyring(keyring.backends.SecretService.Keyring())  
_logger = logging.getLogger(__name__)

class SFTPConnector:
    # ... (SFTPConnector class remains the same)

    def upload(self, local_path, remote_path, overwrite=False):
        try:
            if self.sftp.exists(remote_path):
                if overwrite:
                    self.sftp.remove(remote_path)
                    _logger.info(f"Existing file '{remote_path}' overwritten.")
                else:
                    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
                    new_remote_path = f"{os.path.splitext(remote_path)[0]}_{timestamp}{os.path.splitext(remote_path)[1]}"
                    remote_path = new_remote_path
                    _logger.info(f"File renamed to '{new_remote_path}' to avoid overwriting.")
            
            file_size = os.path.getsize(local_path)
            self.sftp.put(local_path, remote_path)
            _logger.info(f"File '{local_path}' (size: {file_size} bytes) uploaded successfully to '{remote_path}'")
            return True
        except (paramiko.SSHException, FileNotFoundError, PermissionError) as e:
            _logger.error(f"Error uploading file: {e}")
            return False

class ResPartner(models.Model):
    _inherit = 'res.partner'

    # ... (Existing code)
    
    @api.model
    def upload_file_sftp(self, file_data, overwrite=False):
        customer_id = file_data.get('customer_id')
        file_content = file_data.get('file')

        partner = self.browse(customer_id)
        if not partner:
            raise ValidationError("Customer not found.")

        host = '192.168.2.10'
        port = 22
        username = 'sftp'
        password = keyring.get_password('SFTP', username)

        customer_folder = os.path.join('/srv/sftp', partner.name.replace(' ', '_'))

        connector = SFTPConnector(host, port, username, password, customer_folder) 
        
        if connector.connect():
            if not connector.sftp.exists(customer_folder):
                connector.sftp.mkdir(customer_folder) 
                _logger.info(f"Customer folder '{customer_folder}' created.")

            remote_path = os.path.join(customer_folder, os.path.basename(file_content.filename))
            result = connector.upload(file_content.name, remote_path, overwrite)  

            if result:
                self.message_post(body=f"File '{file_content.filename}' uploaded successfully to SFTP server.")
            else:
                raise ValidationError("File upload failed. Check the server logs for details.")
        else:
            raise ValidationError("Could not connect to SFTP server. Check your credentials and network.")
