from odoo import api, fields, models, _
from odoo.tools import datetime


class DrPrescription(models.Model):
    _name = 'dr.prescription'
    _description = 'Doctor Prescription'
    _rec_name = 'name'

    company_id = fields.Many2one(
        comodel_name="res.company",
        default=lambda self: self.env.company,
        store=True,
    )
    dr = fields.Many2one('pod.dr', string='Podiatrist', readonly=True)
    customer = fields.Many2one(
        'res.partner', string='Customer', readonly=False)
    customer_age = fields.Integer(related='customer.age')
    checkup_date = fields.Date('Checkup Date', default=fields.Datetime.now())
    test_type = fields.Many2one('foot.test.type')
    diagnosis_client = fields.Text()
    notes_laboratory = fields.Text()
    podiatrist_observation = fields.Text()
    state = fields.Selection(
        [('Draft', 'Draft'), ('Confirm', 'Confirm')], default='Draft')

    def confirm_request(self):
        for rec in self:
            rec.state = 'Confirm'

    def default_foot_examination_chargeable(self):
        settings_foot_examination_chargeable = self.env['ir.config_parameter'].sudo().get_param(
            'foot_examination_chargeable')
        return settings_foot_examination_chargeable

    foot_examination_chargeable = fields.Boolean(
        default=default_foot_examination_chargeable, readonly=1)

    prescription_type = fields.Selection(
        [('Internal', 'Internal'), ('External', 'External')], default='internal')
    # OD
    od_sph_distance = fields.Char(
    )
    od_sph_near = fields.Char(
    )
    od_cyl_distance = fields.Char(
    )
    od_cyl_near = fields.Char(
    )
    od_av_near = fields.Char(
    )
    os_av_near = fields.Char(
    )
    od_ax_distance = fields.Char(
    )
    od_av_distance = fields.Char(
    )
    os_av_distance = fields.Char(
    )
    os_pupillary_distance = fields.Char()
    od_pupillary_distance = fields.Char()
    os_pupillary_near = fields.Char()
    od_pupillary_near = fields.Char()
    od_ax_near = fields.Char(
    )
    od_add_distance = fields.Char(
    )
    od_add_near = fields.Char(
    )
    od_prism_distance = fields.Char(
    )
    od_prism_near = fields.Char(
    )
    od_base_distance = fields.Char(
    )
    od_base_near = fields.Char(
    )
    os_sph_distance = fields.Char(
    )
    os_sph_near = fields.Char(
    )
    os_cyl_distance = fields.Char(
    )
    os_cyl_near = fields.Char(
    )
    os_ax_distance = fields.Char(
    )
    os_ax_near = fields.Char(
    )
    os_add_distance = fields.Char(
    )
    os_add_near = fields.Char(
    )
    os_prism_distance = fields.Char(
    )
    os_prism_near = fields.Char(
    )
    os_base_distance = fields.Char(
    )
    os_base_near = fields.Char(
    )

    # Extras
    ipd = fields.Char(string="ipd")
    cl_right = fields.Char(string="Cl Right")
    cl_left = fields.Char(string="Cl Left")
    base_curve = fields.Char(string="Base Curve")
    dim = fields.Char(string="Dim")

    # podiatry
    r_wc_close = fields.Char()
    r_wc_far = fields.Char()
    r_woc_close = fields.Char()
    r_woc_far = fields.Char()
    r_tonometria = fields.Char()
    l_wc_close = fields.Char()
    l_wc_far = fields.Char()
    l_woc_close = fields.Char()
    l_woc_far = fields.Char()
    l_tonometria = fields.Char()
    ad_wc_close = fields.Char()
    ad_wc_far = fields.Char()
    ad_woc_close = fields.Char()
    ad_woc_far = fields.Char()
    ad_tonometria = fields.Char()
    ph = fields.Text('P.H')
    cie_10 = fields.Selection([('cataract_foot', 'Cataract Foot'), ('pterygium', "Pterygium"), ('glaucoma', 'Glaucoma'), ('squint', 'Squint'), ('detachment', 'Detachment'), (
        'laser_myopia', 'laser_myopia'), ('ocular_prosthesis', 'Ocular Prosthesis'), ('chalazion', 'Chalazion'), ('conjunctivitis', 'Conjunctivitis')], string='CIE 10')
    main_symptoms = fields.Text('Main Symptoms')
    background = fields.Text('Background')
    podiatry_exam = fields.Text('Podiatry Exam')
    treatment = fields.Text('Treatment')
    other_exams = fields.Text('Other Exams')
    observations = fields.Text('Observations')

    # pdl = fields.Selection(
    #     [
    #         ('25', '25'), ('25.5', '25.5'), ('26', '26'), ('26.5', '26.5'), ('27', '27'),
    #         ('27.5', '27.5'),
    #         ('28', '28'), ('28.5', '28.5'), ('29', '29'), ('29.5', '29.5'),
    #         ('30', '30'), ('30.5', '30.5'), ('31', '31'), ('31.5', '31.5'), ('32', '32'),
    #         ('32.5', '32.5'),
    #         ('33', '33'), ('33.5', '33.5'), ('34', '34'), ('34.5', '34.5'), ('35', '35'),
    #         ('35.5', '35.5'), ('36', '36'), ('36.5', '36.5'), ('37', '37'), ('37.5', '37.5'),
    #         ('38', '38'), ('38.5', '38.5'), ('39', '39'),
    #         ('39.5', '39.5'), ('40', '40')
    #
    #
    #      ],default='25')
    # pdr = fields.Selection(
    #     [
    #         ('25', '25'), ('25.5', '25.5'), ('26', '26'),('26.5', '26.5'), ('27', '27'),('27.5', '27.5'),
    #         ('28', '28'),('28.5', '28.5'),('29', '29'),('29.5', '29.5'),
    #         ('30', '30'),('30.5', '30.5'), ('31', '31'),('31.5', '31.5'), ('32', '32'),
    #         ('32.5', '32.5'),
    #         ('33', '33'),('33.5','33.5'), ('34', '34'),('34.5', '34.5'), ('35', '35'),('35.5', '35.5'), ('36', '36'),('36.5', '36.5'), ('37', '37'),('37.5', '37.5'),('38','38'),('38.5','38.5'), ('39','39'),
    #         ('39.5','39.5'),('40','40')
    #
    #
    #      ],default='25')
    # Not required
    # prism = fields.Boolean('Prism')
    # prisml = fields.Float('Prism')
    # dim = fields.Float('Dim')
    # diml = fields.Float('Dim')
    # height = fields.Float('Height')
    # heightl = fields.Float('Height')
    # basel = fields.Selection(
    #     [('Select', 'Select'), ('IN', 'IN'), ('OUT', 'OUT'), ('UP', 'UP'), ('DOWN', 'DOWN'),
    #      ], 'basel')
    # prism_vall = fields.Selection(
    #     [('0.25', '0.25'), ('0.5', '0.5'), ('0.75', '0.75'), ('1', '1'),
    #      ('1.25', '1.25'), ('1.5', '1.5'),
    #      ('1.75', '1.75'), ('2', '2'), ('2.25', '2.25'), ('2.5', '2.5'), ('2.75', '2.75'),
    #      ('3', '3'), ('3.25', '3.25'), ('3.5', '3.5'), ('3.75', '3.75'), ('4', '4'), ('4.25', '4.25'),
    #      ('4.5', '4.5'), ('4.75', '4.75'),
    #      ('5', '5')], 'PrismL')
    # lpd = fields.Float('lpd')
    # lpdl = fields.Float('lpd')
    # dual_pd = fields.Boolean('I have Dual PD')
    # pd_distance = fields.Selection(
    #     [('47', '47'), ('48', '48'), ('49', '49'), ('50', '50'),
    #      ('60', '60'), ('70', '70')
    #         , ('79', '79')], 'PD')
    # pd_near = fields.Selection(
    #     [('47', '47'), ('48', '48'), ('49', '49'), ('50', '50'),
    #      ('60', '60'), ('70', '70')
    #         , ('79', '79')], 'PD')

    dr_notes = fields.Text('Notes')
    name = fields.Char(required=True, copy=False, readonly=True,
                       index=True, default=lambda self: _('New'))
    family_foot_history = fields.Text()
    ocular_history = fields.Text()
    consultation = fields.Text()

    @api.onchange('os_sph_distance', 'od_sph_distance')
    def onchange_sph_distance(self):
        if self.os_sph_distance and self.os_sph_distance.isdigit():
            self.os_sph_distance = "+" + \
                "{:.2f}".format(float(self.os_sph_distance))
        elif self.os_sph_distance:
            if '-' in self.os_sph_distance:
                self.os_sph_distance = "{:.2f}".format(
                    float(self.os_sph_distance))
        if self.od_sph_distance and self.od_sph_distance.isdigit():
            self.od_sph_distance = "+" + \
                "{:.2f}".format(float(self.od_sph_distance))
        elif self.od_sph_distance:
            if '-' in self.od_sph_distance:
                self.od_sph_distance = "{:.2f}".format(
                    float(self.od_sph_distance))

    @api.onchange('os_sph_near', 'od_sph_near')
    def onchange_sph_near(self):
        if self.os_sph_near and self.os_sph_near.isdigit():
            self.os_sph_near = "+" + "{:.2f}".format(float(self.os_sph_near))
        elif self.os_sph_near:
            if '-' in self.os_sph_near:
                self.os_sph_near = "{:.2f}".format(float(self.os_sph_near))
        if self.od_sph_near and self.od_sph_near.isdigit():
            self.od_sph_near = "+" + "{:.2f}".format(float(self.od_sph_near))
        elif self.od_sph_near:
            if '-' in self.od_sph_near:
                self.od_sph_near = "{:.2f}".format(float(self.od_sph_near))

    @api.onchange('od_cyl_distance', 'os_cyl_distance')
    def onchange_cyl_distance(self):
        if self.od_cyl_distance and self.od_cyl_distance.isdigit():
            self.od_cyl_distance = "+" + \
                "{:.2f}".format(float(self.od_cyl_distance))
        elif self.od_cyl_distance:
            if '-' in self.od_cyl_distance:
                self.od_cyl_distance = "{:.2f}".format(
                    float(self.od_cyl_distance))
        if self.os_cyl_distance and self.os_cyl_distance.isdigit():
            self.os_cyl_distance = "+" + \
                "{:.2f}".format(float(self.os_cyl_distance))
        elif self.os_cyl_distance:
            if '-' in self.os_cyl_distance:
                self.os_cyl_distance = "{:.2f}".format(
                    float(self.os_cyl_distance))

    @api.onchange('od_cyl_near', 'os_cyl_near')
    def onchange_cyl_near(self):
        if self.od_cyl_near and self.od_cyl_near.isdigit():
            self.od_cyl_near = "+" + "{:.2f}".format(float(self.od_cyl_near))
        elif self.od_cyl_near:
            if '-' in self.od_cyl_near:
                self.od_cyl_near = "{:.2f}".format(float(self.od_cyl_near))
        if self.os_cyl_near and self.os_cyl_near.isdigit():
            self.os_cyl_near = "+" + "{:.2f}".format(float(self.os_cyl_near))
        elif self.os_cyl_near:
            if '-' in self.os_cyl_near:
                self.os_cyl_near = "{:.2f}".format(float(self.os_cyl_near))

    @api.onchange('od_add_distance', 'os_add_distance')
    def onchange_add_distance(self):
        if self.od_add_distance and self.od_add_distance.isdigit():
            self.od_add_distance = "+" + \
                "{:.2f}".format(float(self.od_add_distance))
            value = "{:.2f}".format(
                float(self.od_sph_distance) + float(self.od_add_distance))
            self.od_sph_near = value if '-' in value else "+" + value
            self.od_cyl_near = self.od_cyl_distance
            self.od_ax_near = self.od_ax_distance
        if self.od_add_distance:
            if '-' in self.od_add_distance:
                self.od_add_distance = "{:.2f}".format(
                    float(self.od_add_distance))
                value = "{:.2f}".format(
                    float(self.od_sph_distance) + float(self.od_add_distance))
                self.od_sph_near = value if '-' in value else "+" + value
                self.od_cyl_near = self.od_cyl_distance
                self.od_ax_near = self.od_ax_distance
        if self.os_add_distance and self.os_add_distance.isdigit():
            self.os_add_distance = "+" + \
                "{:.2f}".format(float(self.os_add_distance))
            value = "{:.2f}".format(
                float(self.os_sph_distance) + float(self.os_add_distance))
            self.os_sph_near = value if '-' in value else "+" + value
            self.os_cyl_near = self.os_cyl_distance
            self.os_ax_near = self.os_ax_distance
        if self.os_add_distance:
            if '-' in self.os_add_distance:
                self.os_add_distance = "{:.2f}".format(
                    float(self.os_add_distance))
                value = "{:.2f}".format(
                    float(self.os_sph_distance) + float(self.os_add_distance))
                self.os_sph_near = value if '-' in value else "+" + value
                self.os_cyl_near = self.os_cyl_distance
                self.os_ax_near = self.os_ax_distance

    @api.onchange('od_av_distance', 'os_av_distance')
    def onchange_av_distance(self):
        if self.od_av_distance and self.od_av_distance.isdigit():
            self.od_av_distance = "20/" + self.od_av_distance
        if self.os_av_distance and self.os_av_distance.isdigit():
            self.os_av_distance = "20/" + self.os_av_distance

    def open_customer(self):
        sale_order = self.env['sale.order'].search(
            [('prescription_id', '=', self.id)], limit=1)
        print('fire', sale_order)
        if sale_order:
            return {
                'name': _('Doctor Prescription'),
                'view_type': 'form',
                'res_id': sale_order.id,
                'res_model': 'sale.order',
                'view_id': False,
                'view_mode': 'form',
                # 'context':{'default_dr':self.id},
                'type': 'ir.actions.act_window',
            }

        else:
            return {
                'name': _('Doctor Prescription'),
                'view_type': 'form',
                'res_model': 'sale.order',
                'view_id': False,
                'view_mode': 'form',
                'context': {'default_prescription_id': self.id, 'default_partner_id': self.customer.id},
                'type': 'ir.actions.act_window',
            }

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'pod.prescription.sequence')
        result = super(DrPrescription, self).create(vals)
        return result

    # def print_prescription_report(self):
    #     return {
    #         'type': 'ir.actions.report',
    #         'report_name': "pod_erp.doctor_prescription_template",
    #         'report_file': "pod_erp.doctor_prescription_template",
    #         'report_type': 'qweb-pdf',
    #     }

    def print_prescription_report_ticket_size(self):
        return self.env.ref("pod_erp.doctor_prescription_ticket_size2").report_action(self)

    # def print_ophtalmologic_prescription_report(self):
    #     return {
    #         'type': 'ir.actions.report',
    #         'report_name': "pod_erp.doctor_ophtalmological_prescription_template",
    #         'report_file': "pod_erp.doctor_ophtalmological_prescription_template",
    #         'report_type': 'qweb-pdf',
    #     }

    def print_ophtalmologic_prescription_report_ticket_size(self):
        return self.env.ref("pod_erp.doctor_prescription_ophtalmological_ticket_size2").report_action(self)
