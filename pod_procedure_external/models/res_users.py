from odoo import api, Command, fields, models, _

class ResUsers(models.Model):
    _inherit = "res.users"
    
    digital_signature = fields.Binary(attachment=True)
    
    @property
    def SELF_READABLE_FIELDS(self):
        return super().SELF_READABLE_FIELDS + ["digital_signature"]

    @property
    def SELF_WRITEABLE_FIELDS(self):
        return super().SELF_WRITEABLE_FIELDS + ["digital_signature"]
