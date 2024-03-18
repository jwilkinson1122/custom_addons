# -*- coding: utf-8 -*-


from odoo import models, fields, api
import base64


dict_theme_style = {
    "style_1":  {
        "primary_color": "#673ab7",
        "secondary_color": "#dee2e6",
        "button_style": "style_1",
        "product_style": "style_1",
        "pod_cart_position": "left_side",
        "pod_image_display_in_cart": True,
        "pod_action_button_position": 'bottom',
        "pod_mobile_start_screen": 'product_screen',
        "body_background_type": 'bg_color',
        "body_font_family": "Roboto",
        "body_background_color": '#ffffff',
        "pod_list_view_border": 'bordered',
        "pod_header_sticky": True,
        "pod_list_row_hover": True,
        "pod_hover_background_color": "#dee2e6",
        "pod_even_row_color": "#dee2e6",
        "pod_odd_row_color": "#FFFFFF",
        "form_element_style": "style_1",
        "pod_display_product_image_name": "image_name",
        "product_background_color": "#FFFFFF",
    },
    "style_2":  {
        "primary_color": "#43A047",
        "secondary_color": "#dee2e6",
        "button_style": "style_2",
        "product_style": "style_2",
        "pod_cart_position": "right_side",
        "pod_image_display_in_cart": True,
        "pod_action_button_position": 'right_side',
        "pod_mobile_start_screen": 'cart_screen',
        "body_background_type": 'bg_color',
        "body_background_color": '#f1f2f4',
        "pod_list_view_border": 'without_bordered',
        "pod_header_sticky": False,
        "pod_list_row_hover": False,
        "pod_even_row_color": "#dee2e6",
        "pod_odd_row_color": "#FFFFFF",
        "form_element_style": "style_2",
        "body_font_family": "KoHo",
        "pod_display_product_image_name": "image",
        "product_background_color": "#FFFFFF",
    },
    "style_3":  {
        "primary_color": "#C8385E",
        "secondary_color": "#ebebeb",
        "button_style": "style_3",
        "product_style": "style_3",
        "pod_cart_position": "left_side",
        "pod_image_display_in_cart": True,
        "pod_action_button_position": 'left_side',
        "pod_mobile_start_screen": 'product_screen',
        "body_background_type": 'bg_img',
        "body_background_color": '#ffffff',
        "pod_list_view_border": 'without_bordered',
        "pod_header_sticky": True,
        "pod_list_row_hover": True,
        "pod_hover_background_color": "#dee2e6",
        "pod_even_row_color": "#dee2e6",
        "pod_odd_row_color": "#FFFFFF",
        "form_element_style": "style_3",
        "body_font_family": "Lato",
        "pod_display_product_image_name": "product_name",
        "product_background_color": "#FFFFFF",
    },
}


class pod_pos_theme_settings(models.Model):
    _name = "pod.pos.theme.settings"
    _description = "POS Theme Settings"

    name = fields.Char(string="POS Theme Settings",
                       default="POS Theme Settings")
    pod_cart_position = fields.Selection([('left_side', 'Left Side'), (
        'right_side', 'Right Side')], string="Cart Position", default='left_side', required=True)
    pod_image_display_in_cart = fields.Boolean(
        string="Is Image Display In Cart?")
    pod_action_button_position = fields.Selection([('left_side', 'Left Side'), ('bottom', 'Bottom'), (
        'right_side', 'Right Side')], string="Action Button Position", default='left_side', required=True)
    pod_mobile_start_screen = fields.Selection([('product_screen', 'Product Screen'), ('cart_screen', 'Cart Screen')], string="Startup Screen", default='product_screen', required=True)
    theme_style = fields.Selection([
        ("style_1", "Style 1"),
        ("style_2", "Style 2"),
        ("style_3", "Style 3"),
    ], string="Theme Style", default="style_1", required="true")
    pod_pos_switch_view = fields.Boolean(string="Enable Product Switch View")
    pod_default_view = fields.Selection([('list_view', 'List View'), (
        'grid_view', 'Grid View')], default="grid_view", string="Default Product View")
    pod_display_product_name = fields.Boolean(
        string="Display Product Name", default="true")
    pod_display_product_image = fields.Boolean(
        string="Display Product Image", default="true")
    pod_display_product_price = fields.Boolean(
        string="Display Product Price", default="true")
    pod_display_product_code = fields.Boolean(
        string="Display Product Code", default="true")
    pod_display_product_type = fields.Boolean(string="Display Product Type")
    pod_display_product_onhand = fields.Boolean(
        string="Display Product On Hand", default="true")
    pod_display_product_forecasted = fields.Boolean(
        string="Display Product Forecasted Quantity")
    pod_display_product_uom = fields.Boolean(string="Display Product UOM")
    pod_product_image_size = fields.Selection([('small_size', 'Small Size'), ('medium_size', 'Medium Size'), (
        'large_size', 'Large Size')], default="medium_size", string="Image Size", required=1)
    primary_color = fields.Char(string="Primary Color")
    secondary_color = fields.Char(string="Secondary Color")
    product_style = fields.Selection([
        ("style_1", "Style 1"),
        ("style_2", "Style 2"),
        ("style_3", "Style 3"),
    ], string="Product Box Style", default="style_1", required="true")
    button_style = fields.Selection([
        ("style_1", "Style 1"),
        ("style_2", "Style 2"),
        ("style_3", "Style 3"),
    ], string="Button Style", default="style_1", required="true")
    body_background_type = fields.Selection([
        ("bg_color", "Color"),
        ("bg_img", "Image")
    ], string="Body Background Type", default="bg_color")

    body_background_color = fields.Char(string="Body Background Color")
    body_background_image = fields.Binary(string="Body Background Image")
    body_font_family = fields.Selection([
        ("Roboto", "Roboto"),
        ("Raleway", "Raleway"),
        ("Poppins", "Poppins"),
        ("Oxygen", "Oxygen"),
        ("OpenSans", "OpenSans"),
        ("KoHo", "KoHo"),
        ("Ubuntu", "Ubuntu"),
        ("Montserrat", "Montserrat"),
        ("Lato", "Lato"),
        ("custom_google_font", "Custom Google Font"),
    ], string="Body Font Family", required="true")

    body_google_font_family = fields.Char(string="Google Font Family")
    is_used_google_font = fields.Boolean(string="Is use google font?")
    pod_list_view_border = fields.Selection([
        ("bordered", "Bordered"),
        ("without_bordered", "Without Border")
    ], string="List View Border", default="bordered", required="true")
    pod_header_sticky = fields.Boolean(string=" Is Header Sticky?")
    pod_list_row_hover = fields.Boolean(string="Rows Hover?")
    pod_hover_background_color = fields.Char(string="Hover Background Color")
    pod_even_row_color = fields.Char(string="Even Row Color")
    pod_odd_row_color = fields.Char(string="Odd Row Color")
    form_element_style = fields.Selection([
        ("style_1", "Style 1"),
        ("style_2", "Style 2"),
        ("style_3", "Style 3"),
    ], string="Form Element Style", default="style_1", required="true")
    theme_logo = fields.Binary(string="Logo")
    pod_display_product_image_name = fields.Selection([
        ("image", "Image"),
        ("product_name", "Product Name"), ('image_name', 'Image + Name'),
    ], string="Product Detail", default="image_name", required="1")
    product_background_color = fields.Char(string="Product Background Color")
    display_cart_order_item_count = fields.Boolean("Display Cart Item Qty (Mobile)")
    display_product_cart_qty = fields.Boolean("Display Product Qty")

    @api.onchange('theme_style')
    def onchage_theme_style(self):
        if self and self.theme_style:
            selected_theme_style_dict = dict_theme_style.get(
                self.theme_style, False)
            if selected_theme_style_dict:
                self.update(selected_theme_style_dict)

    def write(self, vals):
        """
           Write theme settings data in a less file
        """

        res = super(pod_pos_theme_settings, self).write(vals)

        for rec in self:
            IrAttachment = self.env["ir.attachment"]
    
            URL = "/pod_pos_master/static/pod_pos_theme_responsive/static/src/overrides/pos_theme_variables.scss"

            attachment = IrAttachment.sudo().search([
                ("url", "=", URL)
            ], limit=1)

            content = """     
                $pod_cart_position: %(pod_cart_position)s;
                $pod_image_display_in_cart: %(pod_image_display_in_cart)s;
                $pod_action_button_position: %(pod_action_button_position)s;
                $pod_mobile_start_screen: %(pod_mobile_start_screen)s;
                $pod_pos_theme_style: %(theme_style)s;
                $pod_pos_primary_color: %(primary_color)s;
                $pod_pos_secondary_color: %(secondary_color)s;
                $pod_pos_product_style: %(product_style)s;
                $pod_pos_button_style: %(button_style)s;
                $pod_pos_body_background_type: %(body_background_type)s;
                $pod_pos_body_background_color: %(body_background_color)s;
                $pod_pos_body_background_image: %(body_background_image)s;
                $pod_pos_body_font_family: %(body_font_family)s;
                $pod_pos_body_google_font_family: %(body_google_font_family)s;
                $pod_pos_is_used_google_font: %(is_used_google_font)s;
                $pod_list_view_border: %(pod_list_view_border)s;
                $pod_list_row_hover: %(pod_list_row_hover)s;
                $pod_hover_background_color: %(pod_hover_background_color)s;
                $pod_even_row_color: %(pod_even_row_color)s;
                $pod_odd_row_color: %(pod_odd_row_color)s;
                $pod_header_sticky: %(pod_header_sticky)s;
                
                $pod_form_element_style: %(form_element_style)s;
                $pod_display_product_image_name: %(pod_display_product_image_name)s;
                $product_background_color: %(product_background_color)s;
            """ % {
                "pod_cart_position": rec.pod_cart_position,
                "pod_image_display_in_cart": rec.pod_image_display_in_cart,
                "pod_action_button_position": rec.pod_action_button_position,
                "pod_mobile_start_screen": rec.pod_mobile_start_screen,
                "theme_style": rec.theme_style,
                "primary_color": rec.primary_color,
                "secondary_color": rec.secondary_color,
                "product_style": rec.product_style,
                "button_style": rec.button_style,
                "body_background_type": rec.body_background_type,
                "body_background_color": rec.body_background_color,
                "body_background_image": rec.body_background_image,
                "body_font_family": rec.body_font_family,
                "body_google_font_family": rec.body_google_font_family,
                "is_used_google_font": rec.is_used_google_font,
                "pod_list_view_border": rec.pod_list_view_border,
                "pod_list_row_hover": rec.pod_list_row_hover,
                "pod_even_row_color": rec.pod_even_row_color,
                "pod_odd_row_color": rec.pod_odd_row_color,
                "pod_header_sticky": rec.pod_header_sticky,
                "pod_hover_background_color": rec.pod_hover_background_color,
                "form_element_style": rec.form_element_style,
                "pod_display_product_image_name": rec.pod_display_product_image_name,
                "product_background_color": rec.product_background_color,
            }

            # Check if the file to save had already been modified
            datas = base64.b64encode((content or "\n").encode("utf-8"))

            if attachment:
                # If it was already modified, simply override the corresponding attachment content
                attachment.write({"datas": datas})

            else:
                # If not, create a new attachment
                new_attach = {
                    "name": "POS Theme Settings Variables",
                    "type": "binary",
                    "mimetype": "text/scss",
                    "datas": datas,
                    "url": URL,
                    "public": True,
                    "res_model": "ir.ui.view",
                }

                IrAttachment.sudo().create(new_attach)

                # self.env["ir.qweb"].clear_all_cache()

        return res
