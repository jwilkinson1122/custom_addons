# -*- coding: utf-8 -*-


from odoo import api, fields, models, _, Command
from odoo.exceptions import UserError


class ShopFloor(models.Model):

    _name = 'shop.floor'
    _description = 'Manufacturing Shop Floor'
    _order = "sequence, name"

    name = fields.Char('Floor Name', required=True)
    pos_config_ids = fields.Many2many('pos.config', string='Point of Sales', domain="[('module_pos_shop', '=', True)]")
    background_image = fields.Binary('Background Image')
    background_color = fields.Char('Background Color', help='The background color of the floor in a html-compatible format', default='rgb(210, 210, 210)')
    section_ids = fields.One2many('shop.section', 'floor_id', string='Sections')
    sequence = fields.Integer('Sequence', default=1)
    active = fields.Boolean(default=True)

    @api.ondelete(at_uninstall=False)
    def _unlink_except_active_pos_session(self):
        confs = self.mapped('pos_config_ids').filtered(lambda c: c.module_pos_shop)
        opened_session = self.env['pos.session'].search([('config_id', 'in', confs.ids), ('state', '!=', 'closed')])
        if opened_session and confs:
            error_msg = _("You cannot remove a floor that is used in a PoS session, close the session(s) first: \n")
            for floor in self:
                for session in opened_session:
                    if floor in session.config_id.floor_ids:
                        error_msg += _("Floor: %s - PoS Config: %s \n", floor.name, session.config_id.name)
            raise UserError(error_msg)

    def write(self, vals):
        for floor in self:
            for config in floor.pos_config_ids:
                if config.has_active_session and (vals.get('pos_config_ids') or vals.get('active')):
                    raise UserError(
                        'Please close and validate the following open PoS Session before modifying this floor.\n'
                        'Open session: %s' % (' '.join(config.mapped('name')),))
        return super(ShopFloor, self).write(vals)

    def rename_floor(self, new_name):
        for floor in self:
            floor.name = new_name

    @api.model
    def create_from_ui(self, name, background_color, config_id):
        floor_fields = {
            "name": name,
            "background_color": background_color,
        }
        pos_floor = self.create(floor_fields)
        pos_floor.pos_config_ids = [Command.link(config_id)]
        return {
            'id': pos_floor.id,
            'name': pos_floor.name,
            'background_color': pos_floor.background_color,
            'section_ids': [],
            'sequence': pos_floor.sequence,
            'sections': [],
        }

    def deactivate_floor(self, session_id):
        draft_orders = self.env['pos.order'].search([('session_id', '=', session_id), ('state', '=', 'draft'), ('section_id.floor_id', '=', self.id)])
        if draft_orders:
            raise UserError(_("You cannot delete a floor when orders are still in draft for this floor."))
        for section in self.section_ids:
            section.active = False
        self.active = False

class ShopSection(models.Model):

    _name = 'shop.section'
    _description = 'Manufacturing Shop Section'

    name = fields.Char('Section Name', required=True, help='An internal identification of a section')
    floor_id = fields.Many2one('shop.floor', string='Floor')
    shape = fields.Selection([('square', 'Square'), ('round', 'Round')], string='Shape', required=True, default='square')
    position_h = fields.Float('Horizontal Position', default=10,
        help="The section's horizontal position from the left side to the section's center, in pixels")
    position_v = fields.Float('Vertical Position', default=10,
        help="The section's vertical position from the top to the section's center, in pixels")
    width = fields.Float('Width', default=50, help="The section's width in pixels")
    height = fields.Float('Height', default=50, help="The section's height in pixels")
    seats = fields.Integer('Seats', default=1, help="The default number of customer served at this section.")
    color = fields.Char('Color', help="The section's color, expressed as a valid 'background' CSS property value", default="#35D374")
    active = fields.Boolean('Active', default=True, help='If false, the section is deactivated and will not be available in the point of sale')

    def are_orders_still_in_draft(self):
        draft_orders_count = self.env['pos.order'].search_count([('section_id', 'in', self.ids), ('state', '=', 'draft')])
        return draft_orders_count > 0

    @api.ondelete(at_uninstall=False)
    def _unlink_except_active_pos_session(self):
        confs = self.mapped('floor_id.pos_config_ids').filtered(lambda c: c.module_pos_shop)
        opened_session = self.env['pos.session'].search([('config_id', 'in', confs.ids), ('state', '!=', 'closed')])
        if opened_session:
            error_msg = _("You cannot remove a section that is used in a PoS session, close the session(s) first.")
            if confs:
                raise UserError(error_msg)
