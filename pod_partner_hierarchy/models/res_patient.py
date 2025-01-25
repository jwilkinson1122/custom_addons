from odoo import api, fields, models
from odoo.exceptions import ValidationError

class ResPatient(models.Model):
    _name = 'res.patient'
    _description = 'Patient Data for Orthotics'

    # Basic Patient Information
    name = fields.Char(string="Full Name", required=True)
    date_of_birth = fields.Date(string="Date of Birth", required=True)
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], string="Gender")
    contact_phone = fields.Char(string="Phone Number")
    contact_email = fields.Char(string="Email Address")
    address = fields.Text(string="Address")

    # Medical History and Lifestyle
    medical_history = fields.Text(string="Medical History")
    height = fields.Float(string="Height (cm)")
    weight = fields.Float(string="Weight (kg)")
    activity_level = fields.Selection([
        ('sedentary', 'Sedentary'),
        ('active', 'Active'),
        ('athletic', 'Athletic')
    ], string="Activity Level")
    occupation = fields.Char(string="Occupation")

    # Prescription Details
    orthotic_type = fields.Selection([
        ('full_length', 'Full Length'),
        ('three_quarters', '3/4 Length'),
        ('heel_cups', 'Heel Cups'),
        ('custom_insoles', 'Custom Insoles'),
        ('other', 'Other')
    ], string="Orthotic Type", required=True)

    # Measurements
    foot_length_left = fields.Float(string="Left Foot Length (cm)")
    foot_length_right = fields.Float(string="Right Foot Length (cm)")
    foot_width_left = fields.Float(string="Left Foot Width (cm)")
    foot_width_right = fields.Float(string="Right Foot Width (cm)")
    arch_height = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High')
    ], string="Arch Height")
    heel_width = fields.Float(string="Heel Width (cm)")
    toe_box_dimensions = fields.Char(string="Toe Box Dimensions")

    # Diagnosis and Biomechanics
    primary_diagnosis = fields.Text(string="Primary Diagnosis")
    secondary_conditions = fields.Text(string="Secondary Conditions")
    gait_analysis = fields.Text(string="Gait Analysis Results")
    pressure_mapping_data = fields.Text(string="Pressure Mapping Data")

    # Material Preferences
    top_cover_material = fields.Selection([
        ('leather', 'Leather'),
        ('eva', 'EVA'),
        ('fabric', 'Fabric')
    ], string="Top Cover Material")
    base_layer_material = fields.Selection([
        ('carbon_fiber', 'Carbon Fiber'),
        ('polypropylene', 'Polypropylene'),
        ('eva', 'EVA')
    ], string="Base Layer Material")
    cushioning_level = fields.Selection([
        ('soft', 'Soft'),
        ('medium', 'Medium'),
        ('hard', 'Hard')
    ], string="Cushioning Level")

    # Design Features
    heel_lift = fields.Boolean(string="Heel Lift")
    arch_support = fields.Boolean(string="Arch Support")
    metatarsal_pad = fields.Boolean(string="Metatarsal Pad")
    toe_separator = fields.Boolean(string="Toe Separator")
    specific_modifications = fields.Text(string="Specific Modifications")

    # Footwear Compatibility
    shoe_type = fields.Selection([
        ('athletic', 'Athletic'),
        ('dress', 'Dress'),
        ('work_boots', 'Work Boots')
    ], string="Shoe Type")
    shoe_size = fields.Char(string="Shoe Size")
    toe_box_style = fields.Selection([
        ('open', 'Open'),
        ('closed', 'Closed')
    ], string="Toe Box Style")

    activity_level = fields.Selection([
        ('sedentary', 'Sedentary'),
        ('active', 'Active'),
        ('athletic', 'Athletic')
    ], string="Activity Level", default='active')

    # Additional Information
    allergies = fields.Text(string="Known Allergies")
    discomfort_areas = fields.Text(string="Specific Areas of Discomfort")
    physician_notes = fields.Text(string="Physician/Orthotist Recommendations")

    # Manufacturing Details
    prescription_date = fields.Date(string="Date of Prescription", required=True)
    manufacturing_priority = fields.Selection([
        ('urgent', 'Urgent'),
        ('standard', 'Standard')
    ], string="Manufacturing Priority", default='standard')
    delivery_date = fields.Date(string="Expected Delivery Date")
    previous_adjustments = fields.Text(string="Adjustments from Previous Orthotics")

    # Follow-Up Information
    delivery_status = fields.Selection([
        ('pending', 'Pending'),
        ('delivered', 'Delivered'),
        ('adjusted', 'Adjusted')
    ], string="Delivery Status", default='pending')
    warranty_details = fields.Text(string="Warranty Details")

    @api.constrains('prescription_date', 'delivery_date')
    def _check_prescription_delivery_dates(self):
            for record in self:
                if record.delivery_date and record.delivery_date < record.prescription_date:
                    raise ValidationError(_("Delivery date cannot be earlier than the prescription date."))

class OrthoticPrescription(models.Model):
    _name = 'orthotic.prescription'
    _description = 'Orthotic Patient Data'

    partner_id = fields.Many2one(
        'res.partner', string="Patient", ondelete='cascade', required=True
    )
    prescription_date = fields.Date(string="Prescription Date", required=True)
    practitioner = fields.Char(string="Practitioner")
    material = fields.Char(string="Material")
    special_notes = fields.Text(string="Special Notes")
    left_foot_details = fields.Text(string="Left Foot Details")
    right_foot_details = fields.Text(string="Right Foot Details")
    attachment = fields.Binary(string="Attachment")

    