from odoo import models,fields,api,_

class user_details_form(models.Model):
    _inherit = 'res.partner'


    wholesaler = fields.Boolean(string='Wholesale', default=False,
                                 help="Check if the contact is a location")