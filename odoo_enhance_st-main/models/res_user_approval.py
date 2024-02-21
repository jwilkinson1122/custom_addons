# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, tools, _
from odoo.exceptions import AccessDenied
import logging

_logger = logging.getLogger(__name__)

class ResUsersApproval(models.Model):

    _name = 'res.users.approval'
    _description = "User Approval"

    user_id = fields.Many2one('res.users', string='User')
    approved_user = fields.Boolean("Approved")
    first_approval_status = fields.Boolean("First Approval status")
    block_user = fields.Boolean("Block")


    # Validate the user
    # @classmethod
    # def authenticate(cls, db, login, password, user_agent_env):
    #     uid = super(ResUsers, cls).authenticate(db, login, password, user_agent_env)
    #     if uid :
    #         with cls.pool.cursor() as cr:
    #             env = api.Environment(cr, uid, {})
    #             user = env.user
    #             if not user.approved_user and user._get_signup_invitation_scope() == 'b2c' and not user._is_superuser() and not user._is_admin():
    #                 raise AccessDenied("Not Approved User")
    #     return uid

    # Approve user
    def action_approve_user(self):
        for user in self:
            user.approved_user = True
            user.first_approval_status = True
            user.block_user = False
            template = self.env.ref('odoo_enhance_st.mail_template_user_account_approval',
                                       raise_if_not_found=False)
            if template:
                _logger.info("-----action_approve_user-----")
                _logger.info(user.user_id)
                template.sudo().send_mail(user.user_id.id, force_send=True)
                _logger.info("-----action_approve_user (done)-----")
            else:
                _logger.info("-----action_approve_user (template not found)-----")

    # Reject the user
    def action_reject_user(self):
        for user in self:
            user.approved_user = False
            user.block_user = True
            template = self.env.ref('odoo_enhance_st.mail_template_user_account_reject',raise_if_not_found=False)
            if template:
                _logger.info("-----action_reject_user-----")
                _logger.info(user.user_id)
                template.sudo().send_mail(user.user_id.id, force_send=True)
                _logger.info("-----action_reject_user (done)-----")
            else:
                _logger.info("-----action_reject_user (template not found)-----")

    # Block the user
    def action_block_user(self):
        for user in self:
            user.approved_user = False
            user.block_user = True
            user.first_approval_status = False
