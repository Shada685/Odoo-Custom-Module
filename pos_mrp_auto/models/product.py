from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    manufacture_from_pos = fields.Boolean(
        string='Manufacture from POS',
        help='Automatically create a Manufacturing Order when sold via POS'
    )
