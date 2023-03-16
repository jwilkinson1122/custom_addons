from . import s3_constants
import logging
import base64
import boto3


class S3:
    def __init__(self, aws_credential):
        self.__logging = logging.getLogger(__name__)
        self.__aws_credentials = aws_credential
        self.__aws_client = boto3.client(s3_constants.AWS_S3_DEFAULT,
                                         aws_access_key_id=self.__aws_credentials['access_key'],
                                         aws_secret_access_key=self.__aws_credentials['secret_key'])
        self.__default_bucket = self.__aws_credentials['bucket']
        self.__js_resp = {
            "err_status": True,
            "response": None,
            "total": 0,
            "success": 0,
            "failed": 0
        }

    def reset_response(self):
        self.__js_resp["err_status"] = True
        self.__js_resp["response"] = None
        self.__js_resp["total"] = 0
        self.__js_resp["success"] = 0
        self.__js_resp["failed"] = 0

    def export_documents(self, res_data):
        self.reset_response()
        try:
            for file in res_data["files"]:
                server_rp = self.__aws_client.put_object(
                    Bucket=self.__default_bucket,
                    Key=res_data["res_name"] + '/' + file["name"],
                    ContentType=file["mimetype"],
                    Body=file["db_datas"]
                )
                if s3_constants.AWS_S3_RESPONSE_KEY in server_rp:
                    self.__js_resp["success"] += 1
                else:
                    self.__js_resp["failed"] += 1
            self.__js_resp["err_status"] = False
        except Exception as ex:
            self.__logging.exception("Export S3 Bucket Exception: " + str(ex))
            self.__js_resp["response"] = s3_constants.AWS_S3_EXP_EXCEPT
        return self.__js_resp

    def check_file_exists(self, db_cursor, file_name, file_type, user_rec):
        chk_eir_file = False
        try:
            db_cursor.execute("select id from " + s3_constants.DB_IR_ATTACHMENT_MODEL +
                              " where name='" + file_name +
                              "' and mimetype='" + file_type + "'")
            file_rec = db_cursor.fetchall()
            if file_rec and len(file_rec) > 0:
                for file in file_rec:
                    query = "select * from " + s3_constants.CLASS_IR_ATTACHMENT_REL_MODEL + \
                            " where class_id = " + str(user_rec.id) + " and attachment_id = " + str(file[0])
                    db_cursor.execute(query)
                    res = db_cursor.fetchone()
                    if res and len(res) > 0:
                        chk_eir_file = True
        except Exception as ex:
            self.__logging.exception("file search info: " + str(ex))
        return chk_eir_file

    def import_documents(self, db_cursor, user_rcd, self_env=None):
        self.reset_response()
        try:
            dir_serv_resp = self.__aws_client.list_objects_v2(
                Bucket=self.__default_bucket,
                Prefix=user_rcd.name,
                MaxKeys=100)
            if s3_constants.AWS_S3_RESPONSE_KEY in dir_serv_resp and s3_constants.AWS_S3_LIST_KEY in dir_serv_resp:
                if len(dir_serv_resp[s3_constants.AWS_S3_LIST_KEY]) > 0:
                    self.__js_resp["err_status"] = False
                    for serv_file in dir_serv_resp[s3_constants.AWS_S3_LIST_KEY]:
                        file_serv_resp = self.__aws_client.get_object(
                            Bucket=self.__default_bucket, Key=serv_file['Key'])
                        if s3_constants.AWS_S3_RESPONSE_KEY in file_serv_resp:
                            file_datas = file_serv_resp['Body'].read()
                            try:
                                chk_status = self.check_file_exists(db_cursor,
                                                                    serv_file['Key'].split('/')[1],
                                                                    file_serv_resp["ContentType"],
                                                                    user_rcd)
                                if not chk_status:
                                    byte_data = base64.b64encode(file_datas)
                                    save_rec = self_env[s3_constants.IR_ATTACHMENT_MODEL].create({
                                                                            'name': serv_file['Key'].split('/')[1],
                                                                            'datas': byte_data,
                                                                            'mimetype': file_serv_resp["ContentType"],
                                                                            'type': 'binary',
                                                                            'res_model': s3_constants.CONTACT_MODEL,
                                                                            'res_id': 0,
                                                                            })

                                    db_cursor.execute("insert into " + s3_constants.CLASS_IR_ATTACHMENT_REL_MODEL +
                                                      " (class_id, attachment_id) values (" + str(user_rcd["id"]) +
                                                      "," + str(save_rec.id) + ")")
                                    self.__js_resp["success"] += 1
                            except Exception as ex:
                                self.__logging.info("Log >> Read Drive Internal Exception: " + str(ex))
                                self.__js_resp["failed"] += 1
                        else:
                            self.__js_resp["failed"] += 1
                else:
                    self.__js_resp["response"] = s3_constants.AWS_S3_IMP_SERV_DIR_NOT_FND
            else:
                self.__js_resp["response"] = s3_constants.AWS_S3_IMP_SERV_ERR

        except Exception as ex:
            self.__logging.exception("Import Directory Exception: " + str(ex))
            self.__js_resp["response"] = s3_constants.AWS_S3_IMP_SERV_EXCEPT
        return self.__js_resp
