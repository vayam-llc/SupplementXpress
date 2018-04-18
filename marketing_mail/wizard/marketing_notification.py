from odoo import models, fields, api


class MarketingNotification(models.TransientModel):
    _name = 'marketing.notification'

    alternative_products = fields.Boolean(string='Alternative products')
    alternative_brands = fields.Boolean(string='Alternative Brands')
    partner_id = fields.Many2one('res.partner')

    #sent mail marketing mail based on alternative products after purchase a product
    @api.multi
    def alternative_product_marketing(self):
        sale_order=self.env['account.payment'].browse(self.env.context['active_id'])
        if self.alternative_products==True:
            template = self.env.ref('marketing_mail.mail_notification_template')
            template.send_mail(sale_order.partner_id.id, force_send=True)
            sale_order.sent_product_marketing=True

