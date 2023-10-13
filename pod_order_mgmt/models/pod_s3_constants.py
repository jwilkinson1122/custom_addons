###################################################################################################
# ###############################     AWS S3 Basic      ###########################################
###################################################################################################

DEFAULT_INDEX = -1
S3_CREDENTIALS_MODEL = 's3.credentials'
CONTACT_MODEL = 'res.partner'
IR_MODEL = 'ir.model'
RES_USERS_MODEL = 'res.users'
IR_ATTACHMENT_MODEL = 'ir.attachment'
DB_IR_ATTACHMENT_MODEL = 'ir_attachment'
CLASS_IR_ATTACHMENT_REL_MODEL = 's3_class_ir_attachments_rel'

AWS_REDIRECT_URI = '/aws_success'
AWS_REDIRECT_ODOO_URI = '/web'
#################################################################################################
# ###############################     S3 Section      ###########################################
#################################################################################################

AWS_S3_DEFAULT = 's3'
AWS_S3_RESPONSE_KEY = 'ResponseMetadata'
AWS_S3_LIST_KEY = 'Contents'
AWS_S3_FILE_NOT_FND = 'Oops, no files found. Please try again.'
AWS_S3_EXP_EXCEPT = 'Oops, Export directory files failed, Please try again.'
AWS_S3_IMP_SERV_EXCEPT = 'Oops, Import Directory from Server failed, Please try again.'
AWS_S3_IMP_SERV_ERR = 'Oops, unable to fetch directory from Server. Please try again.'
AWS_S3_IMP_SERV_DIR_NOT_FND = 'Oops, no files found in directory from server. Please try again.'
AWS_S3_OPT_KEY = 'SUC'

#################################################################################################
# ##############################      Connection Section      ###################################
#################################################################################################

# System Messages
FAILURE_POP_UP_TITLE = 'System Alert'
CREDENTIAL_SAVE_MSG = 'Credentials saved successfully.'
CREDENTIAL_UPDATE_MSG = 'Credentials updated successfully.'
CREDENTIAL_EXCEPT_MSG = 'Credentials fail to stored.'

CREDENTIAL_NOT_FND_MSG = 'Oops, credentials are not found. Please try again.'
CREDENTIAL_EXCEPT_FETCH_MSG = 'Oops, unable to fetch credentials from storage. Please try again.'
SYNC_REQ_ERROR = 'Oops, unable to process given request, Please try again'
NO_OPT_SECTION_ERR = 'Oops, no operation is not being selected, Please some operation to proceed.'
SYNC_PROCESS_MSG = "Synchronization process completed"
# DateTime Format
DEFAULT_DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
DEFAULT_TZ_DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S'
