from odoo import models, fields, api


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    #
    

    product_attre = fields.Text(string='Product Attribute')


    # @api.onchange('product_id')
    # def confirm_attribute(self):
    #     for record in self:
    #         product_attribute = ""
    #         varient_list_items = []
    #         if record.product_id and record.product_id.name:
    #             product_name = record.name
    #             varients = product_name[product_name.find("("):]
    #             varients_items = varients.splitlines()
    #             for varient in varients_items:
    #                 if '(' in varient and ')' in varient:
    #                     varient_list_items.append(varient[varient.find('(') + 1:varient.find(")")])
    #                 elif ":" in varient:
    #                     varient_list_items.append({varient[0:varient.find(":")]: varient[varient.find(":") + 1:]})
    #         for items in varient_list_items:
    #             if type(items) == str:
    #                 product_attribute += items.replace(",", "-") + "-"
    #             elif type(items) == dict:
    #                 for item in items.values():
    #                     product_attribute += item + '-'
    #         record.product_attre = product_attribute.rstrip('-')

    def add_button(self):
        # print(self)
        existing_wizard = self.env['creating.wizard'].search([('sale_order_id','=', self.id)], limit=1)
        # print(existing_wizard.sale_order_id.name,">>>>>>>>>>>>>>.")
        existing_wizard.sale_order_id = self.id
        if existing_wizard:
            return {
                'name': 'Wizard Information',
                'type': 'ir.actions.act_window',
                'res_model': 'creating.wizard',
                'res_id': existing_wizard.id,
                'view_mode': 'form',
                'target': 'new',
            }
        else:
            new_wizard = self.env['creating.wizard'].create({})
            new_wizard.sale_order_id = self.id

            return {
                'name': 'Wizard Information',
                'type': 'ir.actions.act_window',
                'res_model': 'creating.wizard',
                'res_id': new_wizard.id,
                'view_mode': 'form',
                'target': 'new',
            }


class CreatingWizard(models.Model):
    _name = 'creating.wizard'

    normal_field = fields.Char('Details')
    sale_order_id = fields.Many2one('sale.order.line', string='Sale Order')

    data_ids = fields.One2many('another.one.two.many', 'one_id', string='Data')

    def add_descript(self):
        # print(record.date,'33333333333',record.id)
        self.sale_order_id.name = self.sale_order_id.product_template_id.name # we are taking product_template_id bcz we can't use for loop under the description field that's wy we are useing for loop under the product_template_id
        print(self.sale_order_id.name,'kkkkkkkkkkkkkkkkkkk')
        print(self.sale_order_id.product_template_id.name,'nnnnnnnnnnnnnnnnnnnn')
        print(self.sale_order_id.product_template_id,'222222222222222222')
        for record in self.data_ids:
            self.sale_order_id.name = self.sale_order_id.name + '\n' + str(record.date) + ':' + str(record.qty_id)

class AnotherOneTwoMany(models.Model):
    _name = 'another.one.two.many'

    one_id = fields.Many2one('creating.wizard', string='Template')

    date = fields.Date(string='Date')
    qty_id = fields.Integer(string='Quantity')








