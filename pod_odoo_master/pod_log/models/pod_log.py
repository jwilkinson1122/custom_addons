# -*- coding: utf-8 -*-

import os
import time

from odoo import api, models, fields, _


class PodLog(models.Model):
    _name = 'pod.log'
    _description = 'Logs'
    _rec_name = 'message'
    _log_access = False
    _order = 'log_date desc'

    @api.depends('log_uid')
    def _get_user_name(self):
        for log in self:
            user = self.env['res.users'].browse(log.log_uid)
            if user.exists():
                log.log_user_name = "%s [%s]" % (user.name, log.log_uid)
            else:
                log.log_user_name = "[%s]" % log.log_uid

    @api.depends('res_id')
    def _get_res_name(self):
        for log in self:
            log.log_res_name = ""
            res = self.env[log.model_name].browse(log.res_id)
            infos = res.name_get()
            if infos:
                log.log_res_name = infos[0][1]

    log_date = fields.Datetime('Date', readonly=True)
    log_uid = fields.Integer('User', readonly=True)
    log_user_name = fields.Char(
        string='User', size=256, compute='_get_user_name')
    log_res_name = fields.Char(
        string='Resource name', size=256, compute='_get_res_name')
    model_name = fields.Char('Model name', size=64, readonly=True, index=True)
    res_id = fields.Integer(
        'Resource id', readonly=True, group_operator="count", index=True)
    pid = fields.Integer(readonly=True, group_operator="count")
    level = fields.Char(size=16, readonly=True)
    message = fields.Text('Message', readonly=True)

    @api.model
    def archive_and_delete_old_logs(self, nb_days=90, archive_path=''):
        # Thanks to transaction isolation, the COPY and DELETE will find
        # the same pod_log records
        if archive_path:
            file_name = time.strftime("%Y%m%d_%H%M%S.log.csv")
            file_path = os.path.join(archive_path, file_name)
            self.env.cr.execute("""COPY (SELECT * FROM pod_log
            WHERE log_date + interval'%s days' < NOW() at time zone 'UTC')
            TO %s
            WITH (FORMAT csv, ENCODING utf8)""", (nb_days, file_path,))
        self.env.cr.execute(
            "DELETE FROM pod_log "
            "WHERE log_date + interval '%s days' < NOW() at time zone 'UTC'",
            (nb_days,))
        return True


    # def action_delete_selected_logs(self):
    #     """Unlink exactly the records you have selected."""
    #     # `self` here is the recordset of whatever rows were checked
    #     self.unlink()
    #     # reload the view so the UI updates
    #     return {'type': 'ir.actions.client', 'tag': 'reload'}

    # @api.model
    # def action_clear_all_logs(self):
    #     """Unlink every pod.log in the database."""
    #     self.search([]).unlink()
    #     return {'type': 'ir.actions.client', 'tag': 'reload'}
