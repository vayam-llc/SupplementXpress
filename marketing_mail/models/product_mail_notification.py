from odoo import models, fields, api
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    sent_product_marketing = fields.Boolean(string="Product marketing")
    sent_brand_marketing = fields.Boolean(string="Brand marketing")

    @api.multi
    def marketing_notification_wizard(self):
        composer_form_view_id = self.env.ref('mail.email_compose_message_wizard_form').id
        try:
            default_template = self.env.ref('marketing_mail.mail_template_sale_suggested', raise_if_not_found=False)
            default_template_id = default_template.id if default_template else False
            template_id = int(self.env['ir.config_parameter'].sudo().get_param('marketing_mail.mail_template_sale_suggested', default_template_id))
        except:
            template_id = False
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'view_id': composer_form_view_id,
            'target': 'new',
            'context': {
                'default_composition_mode': 'mass_mail' if len(self) > 1 else 'comment',
                'default_res_id': self.ids[0],
                'default_model': 'sale.order',
                'default_use_template': bool(template_id),
                'default_template_id': template_id,
                'website_sale_send_recovery_email': True,
                'active_ids': self.ids,
            },
        }



class SaleOrderLine(models.Model):

    _inherit = 'sale.order.line'


    suggested_products = fields.Text()



    @api.model
    def create(self,vals):
        line_id = super(SaleOrderLine, self).create(vals)
        print(line_id.product_id.product_tmpl_id.alternative_product_ids)
        sugg_prod = ""
        for data in line_id.product_id.product_tmpl_id.alternative_product_ids:
            if sugg_prod == "":
                sugg_prod +=data.name+" "
            else:
                sugg_prod += ","+data.name+" "
        line_id.suggested_products = sugg_prod
        return line_id

