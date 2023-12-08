# -*- coding: utf-8 -*-


from odoo.fields import Command
from odoo.tests import TransactionCase

from odoo.addons.account.tests.common import AccountTestInvoicingCommon
from odoo.addons.product.tests.common import ProductCommon
from odoo.addons.pod_prescriptions_team.tests.common import PrescriptionsTeamCommon


class PrescriptionCommon(
    ProductCommon, # BaseCommon, UomCommon
    PrescriptionsTeamCommon,
):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Not defined in product common because only used in prescriptions
        # cls.group_discount_per_so_line = cls.env.ref('product.group_discount_per_so_line')

        cls.empty_order = cls.env['prescriptions.order'].create({
            'partner_id': cls.partner.id,
        })
        cls.prescriptions_order = cls.env['prescriptions.order'].create({
            'partner_id': cls.partner.id,
            'order_line': [
                Command.create({
                    'product_id': cls.consumable_product.id,
                    'product_uom_qty': 5.0,
                }),
                Command.create({
                    'product_id': cls.service_product.id,
                    'product_uom_qty': 12.5,
                })
            ]
        })

    @classmethod
    def _enable_pricelists(cls):
        cls.env.user.groups_id += cls.env.ref('product.group_product_pricelist')


class TestPrescriptionCommonBase(TransactionCase):
    ''' Setup with prescriptions test configuration. '''

    @classmethod
    def setup_prescriptions_configuration_for_company(cls, company):
        Users = cls.env['res.users'].with_context(no_reset_password=True)

        company_data = {
            # Prescriptions Team
            'default_prescriptions_team': cls.env['crm.team'].with_context(tracking_disable=True).create({
                'name': 'Test Channel',
                'company_id': company.id,
            }),

            # Users
            'default_user_prescriptionsman': Users.create({
                'name': 'default_user_prescriptionsman',
                'login': 'default_user_prescriptionsman.comp%s' % company.id,
                'email': 'default_user_prescriptionsman@example.com',
                'signature': '--\nMark',
                'notification_type': 'email',
                'groups_id': [(6, 0, cls.env.ref('pod_prescriptions_team.group_prescriptions_prescriptionsman').ids)],
                'company_ids': [(6, 0, company.ids)],
                'company_id': company.id,
            }),
            'default_user_portal': Users.create({
                'name': 'default_user_portal',
                'login': 'default_user_portal.comp%s' % company.id,
                'email': 'default_user_portal@gladys.portal',
                'groups_id': [(6, 0, [cls.env.ref('base.group_portal').id])],
                'company_ids': [(6, 0, company.ids)],
                'company_id': company.id,
            }),
            'default_user_employee': Users.create({
                'name': 'default_user_employee',
                'login': 'default_user_employee.comp%s' % company.id,
                'email': 'default_user_employee@example.com',
                'groups_id': [(6, 0, [cls.env.ref('base.group_user').id])],
                'company_ids': [(6, 0, company.ids)],
                'company_id': company.id,
            }),

            # Pricelist
            'default_pricelist': cls.env['product.pricelist'].with_company(company).create({
                'name': 'default_pricelist',
                'currency_id': company.currency_id.id,
            }),

            # Product category
            'product_category': cls.env['product.category'].with_company(company).create({
                'name': 'Test category',
            }),
        }

        company_data.update({
            # Products
            'product_service_delivery': cls.env['product.product'].with_company(company).create({
                'name': 'product_service_delivery',
                'categ_id': company_data['product_category'].id,
                'standard_price': 200.0,
                'list_price': 180.0,
                'type': 'service',
                'uom_id': cls.env.ref('uom.product_uom_unit').id,
                'uom_po_id': cls.env.ref('uom.product_uom_unit').id,
                'default_code': 'SERV_DEL',
                'invoice_policy': 'delivery',
                'taxes_id': [(6, 0, [])],
                'supplier_taxes_id': [(6, 0, [])],
            }),
            'product_service_order': cls.env['product.product'].with_company(company).create({
                'name': 'product_service_order',
                'categ_id': company_data['product_category'].id,
                'standard_price': 40.0,
                'list_price': 90.0,
                'type': 'service',
                'uom_id': cls.env.ref('uom.product_uom_hour').id,
                'uom_po_id': cls.env.ref('uom.product_uom_hour').id,
                'description': 'Example of product to invoice on order',
                'default_code': 'PRE-PAID',
                'invoice_policy': 'order',
                'taxes_id': [(6, 0, [])],
                'supplier_taxes_id': [(6, 0, [])],
            }),
            'product_order_cost': cls.env['product.product'].with_company(company).create({
                'name': 'product_order_cost',
                'categ_id': company_data['product_category'].id,
                'standard_price': 235.0,
                'list_price': 280.0,
                'type': 'consu',
                'weight': 0.01,
                'uom_id': cls.env.ref('uom.product_uom_unit').id,
                'uom_po_id': cls.env.ref('uom.product_uom_unit').id,
                'default_code': 'FURN_9999',
                'invoice_policy': 'order',
                'expense_policy': 'cost',
                'taxes_id': [(6, 0, [])],
                'supplier_taxes_id': [(6, 0, [])],
            }),
            'product_delivery_cost': cls.env['product.product'].with_company(company).create({
                'name': 'product_delivery_cost',
                'categ_id': company_data['product_category'].id,
                'standard_price': 55.0,
                'list_price': 70.0,
                'type': 'consu',
                'weight': 0.01,
                'uom_id': cls.env.ref('uom.product_uom_unit').id,
                'uom_po_id': cls.env.ref('uom.product_uom_unit').id,
                'default_code': 'FURN_7777',
                'invoice_policy': 'delivery',
                'expense_policy': 'cost',
                'taxes_id': [(6, 0, [])],
                'supplier_taxes_id': [(6, 0, [])],
            }),
            'product_order_prescriptions_price': cls.env['product.product'].with_company(company).create({
                'name': 'product_order_prescriptions_price',
                'categ_id': company_data['product_category'].id,
                'standard_price': 235.0,
                'list_price': 280.0,
                'type': 'consu',
                'weight': 0.01,
                'uom_id': cls.env.ref('uom.product_uom_unit').id,
                'uom_po_id': cls.env.ref('uom.product_uom_unit').id,
                'default_code': 'FURN_9999',
                'invoice_policy': 'order',
                'expense_policy': 'prescriptions_price',
                'taxes_id': [(6, 0, [])],
                'supplier_taxes_id': [(6, 0, [])],
            }),
            'product_delivery_prescriptions_price': cls.env['product.product'].with_company(company).create({
                'name': 'product_delivery_prescriptions_price',
                'categ_id': company_data['product_category'].id,
                'standard_price': 55.0,
                'list_price': 70.0,
                'type': 'consu',
                'weight': 0.01,
                'uom_id': cls.env.ref('uom.product_uom_unit').id,
                'uom_po_id': cls.env.ref('uom.product_uom_unit').id,
                'default_code': 'FURN_7777',
                'invoice_policy': 'delivery',
                'expense_policy': 'prescriptions_price',
                'taxes_id': [(6, 0, [])],
                'supplier_taxes_id': [(6, 0, [])],
            }),
            'product_order_no': cls.env['product.product'].with_company(company).create({
                'name': 'product_order_no',
                'categ_id': company_data['product_category'].id,
                'standard_price': 235.0,
                'list_price': 280.0,
                'type': 'consu',
                'weight': 0.01,
                'uom_id': cls.env.ref('uom.product_uom_unit').id,
                'uom_po_id': cls.env.ref('uom.product_uom_unit').id,
                'default_code': 'FURN_9999',
                'invoice_policy': 'order',
                'expense_policy': 'no',
                'taxes_id': [(6, 0, [])],
                'supplier_taxes_id': [(6, 0, [])],
            }),
            'product_delivery_no': cls.env['product.product'].with_company(company).create({
                'name': 'product_delivery_no',
                'categ_id': company_data['product_category'].id,
                'standard_price': 55.0,
                'list_price': 70.0,
                'type': 'consu',
                'weight': 0.01,
                'uom_id': cls.env.ref('uom.product_uom_unit').id,
                'uom_po_id': cls.env.ref('uom.product_uom_unit').id,
                'default_code': 'FURN_7777',
                'invoice_policy': 'delivery',
                'expense_policy': 'no',
                'taxes_id': [(6, 0, [])],
                'supplier_taxes_id': [(6, 0, [])],
            }),
        })

        return company_data


class TestPrescriptionCommon(AccountTestInvoicingCommon, TestPrescriptionCommonBase):
    ''' Setup to be used post-install with prescriptions and accounting test configuration.'''

    @classmethod
    def setup_company_data(cls, company_name, chart_template=None, **kwargs):
        company_data = super().setup_company_data(company_name, chart_template=chart_template, **kwargs)

        company_data.update(cls.setup_prescriptions_configuration_for_company(company_data['company']))

        company_data['product_category'].write({
            'property_account_income_categ_id': company_data['default_account_revenue'].id,
            'property_account_expense_categ_id': company_data['default_account_expense'].id,
        })

        return company_data
