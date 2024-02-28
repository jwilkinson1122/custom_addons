# -*- coding: utf-8 -*-

import base64
from odoo.tests.common import tagged, TransactionCase

GIF = b"R0lGODdhAQABAIAAAP///////ywAAAAAAQABAAACAkQBADs="
TEXT = base64.b64encode(bytes("workflow bridge product", 'utf-8'))


@tagged('post_install', '-at_install')
class TestCasePrescriptionsBridgeProduct(TransactionCase):
    
    def setUp(self):
        super(TestCasePrescriptionsBridgeProduct, self).setUp()
        self.folder_test = self.env['prescriptions.folder'].create({'name': 'folder_test'})
        self.company_test = self.env['res.company'].create({
            'name': 'test bridge products',
            'product_folder': self.folder_test.id,
            'prescriptions_product_settings': False
        })
        self.template_test = self.env['product.template'].create({
            'name': 'template_test',
            'company_id': self.company_test.id,
        })
        self.product_test = self.template_test.product_variant_id
        self.template_test_1 = self.env['product.template'].create({
            'name': 'template_test_1',
            'company_id': self.company_test.id,
        })
        self.product_test_1 = self.template_test_1.product_variant_id
        self.template_test_2 = self.env['product.template'].create({
            'name': 'Box',
            'company_id': self.company_test.id,
        })
        self.product_test_2 = self.template_test_2.product_variant_id
        self.attachment_txt_two = self.env['ir.attachment'].create({
            'datas': TEXT,
            'name': 'fileTextTwo.txt',
            'mimetype': 'text/plain',
        })
        self.attachment_gif_two = self.env['ir.attachment'].create({
            'datas': GIF,
            'name': 'fileTwoGif.gif',
            'mimetype': 'image/gif',
        })
        self.attachment_gif = self.env['ir.attachment'].create({
            'datas': GIF,
            'name': 'fileGif.gif',
            'mimetype': 'image/gif',
        })

    def test_bridge_folder_product_settings_on_write(self):
        """
        Makes sure the settings apply their values when a prescription is assigned a res_model, res_id.
        """
        self.company_test.write({'prescriptions_product_settings': True})
        
        self.attachment_gif_two.write({
            'res_model': 'product.product',
            'res_id': self.product_test.id
        })
        self.attachment_txt_two.write({
            'res_model': 'product.template',
            'res_id': self.template_test.id
        })

        txt_doc = self.env['prescriptions.prescription'].search([('attachment_id', '=', self.attachment_txt_two.id)])
        gif_doc = self.env['prescriptions.prescription'].search([('attachment_id', '=', self.attachment_gif_two.id)])

        self.assertEqual(txt_doc.folder_id, self.folder_test, 'the text two prescription should have a folder')
        self.assertEqual(gif_doc.folder_id, self.folder_test, 'the gif two prescription should have a folder')

    def _products_search(self, record, field_name):
        """
        Make sure the search prescriptions based on product/product template.
        Test Flow:
            -  Actived  Centralize files attached to products
            -  Upload three prescriptions in the product/product template
            -  Search a prescription based on the product/product template
            -  Check search prescription and expected prescription
        """
        self.company_test.write({'prescriptions_product_settings': True})
        self.attachment_gif_two.write({
            'res_model': record._name,
            'res_id': record[0].id,
        })
        self.attachment_txt_two.write({
            'res_model': record._name,
            'res_id': record[1].id,
        })
        self.attachment_gif.write({
            'res_model': record._name,
            'res_id': record[2].id,
        })

        docs = self.env['prescriptions.prescription'].search([('res_id', 'in', record.ids), ('res_model', '=', record._name)], order='id')
        docs.flush_recordset()
        cases = [
            ([(field_name, 'ilike', 'template')], docs[0:2]),
            ([(field_name, 'not ilike', 'template')], docs[2]),
            ([(field_name, '=', 'template_test')], docs[0]),
            ([(field_name, '!=', 'template_test')], docs[1:]),
            ([(field_name, '=', record[0].id)], docs[0]),
            ([(field_name, '=', True)], docs),
            ([(field_name, '=', False)], self.env['prescriptions.prescription'].search([]) - docs),
            ([(field_name, 'in', record.ids)], docs),
            ([(field_name, 'not in', record.ids)], self.env['prescriptions.prescription']),
            (['|', (field_name, 'in', [record[2].id]), (field_name, 'ilike', 'template')], docs),
        ]
        for domain, result in cases:
            with self.subTest(domain=domain):
                self.assertEqual(self.env['prescriptions.prescription'].search(domain), result)

    def test_product_template_prescription_search(self):
        product_templates = self.template_test + self.template_test_1 + self.template_test_2
        return self._products_search(product_templates, 'product_template_id')

    def test_product_product_prescription_search(self):
        products = self.product_test + self.product_test_1 + self.product_test_2
        return self._products_search(products, 'product_id')

    def test_bridge_folder_product_settings_default_company(self):
        """
        Makes sure the settings apply their values when a prescription is assigned a res_model, res_id but when
        the product/template doesn't have a company_id.
        """
        company_test = self.env['res.company'].create({
            'name': 'test bridge products two',
            'product_folder': self.folder_test.id,
            'prescriptions_product_settings': True,
        })
        test_user = self.env['res.users'].create({
            'name': "prescriptions test prescriptions user",
            'login': "dtdu",
            'email': "dtdu@yourcompany.com",
            # group_system is used as it is required to write on product.product and product.template
            'groups_id': [(6, 0, [self.ref('prescriptions.group_prescriptions_user'), self.ref('base.group_system')])],
            'company_ids': [(6, 0, [company_test.id])],
            'company_id': company_test.id,
        })
        template_test = self.env['product.template'].create({
            'name': 'template_test',
        })
        self.attachment_txt_two.with_user(test_user).write({
            'res_model': 'product.template',
            'res_id': template_test.id,
        })
        txt_doc = self.env['prescriptions.prescription'].search([('attachment_id', '=', self.attachment_txt_two.id)])
        self.assertEqual(txt_doc.folder_id, self.folder_test, 'the text two prescription should have a folder')

        product_test = self.env['product.product'].create({
            'name': 'product_test',
        })
        self.attachment_gif_two.with_user(test_user).write({
            'res_model': 'product.product',
            'res_id': product_test.id,
        })
        gif_doc = self.env['prescriptions.prescription'].search([('attachment_id', '=', self.attachment_gif_two.id)])
        self.assertEqual(gif_doc.folder_id, self.folder_test, 'the gif two prescription should have a folder')

    def test_default_res_id_model(self):
        """
        Test default res_id and res_model from context are used for prescription creation.
        """
        self.company_test.write({'prescriptions_product_settings': True})

        attachment = self.env['ir.attachment'].with_context(
            default_res_id=self.product_test.id,
            default_res_model=self.product_test._name,
        ).create({
            'datas': GIF,
            'name': 'fileTwoGif.gif',
            'mimetype': 'image/gif',
        })
        prescription = self.env['prescriptions.prescription'].search([('attachment_id', '=', attachment.id)])
        self.assertTrue(prescription, "It should have created a prescription from default values")

    def test_create_product_from_workflow(self):

        prescription_gif = self.env['prescriptions.prescription'].create({
            'datas': GIF,
            'name': 'file.gif',
            'mimetype': 'image/gif',
            'folder_id': self.folder_test.id,
        })

        workflow_rule = self.env['prescriptions.workflow.rule'].create({
            'domain_folder_id': self.folder_test.id,
            'name': 'workflow product',
            'create_model': 'product.template',
        })

        action = workflow_rule.apply_actions([prescription_gif.id])
        new_product = self.env['product.template'].browse([action['res_id']])

        self.assertEqual(prescription_gif.res_model, 'product.template')
        self.assertEqual(prescription_gif.res_id, new_product.id)
        self.assertEqual(new_product.image_1920, prescription_gif.datas)
