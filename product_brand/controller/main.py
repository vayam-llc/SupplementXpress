from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale



class WebsiteSale(WebsiteSale):

    def _get_search_domain(self, search, category, attrib_values):
        print("new func")
        domain = request.website.sale_product_domain()
        brands=[]
        if search:
            for srch in search.split(" "):
                brand_id = request.env['product.brand'].search([('name','ilike',srch)])
                for brand in brand_id:
                    brands.append(brand.id)

                domain += [
                    '|', '|', '|','|', ('name', 'ilike', srch), ('description', 'ilike', srch),
                    ('description_sale', 'ilike', srch), ('product_variant_ids.default_code', 'ilike', srch),('product_brand_id','in',brands)]

        if category:
            domain += [('public_categ_ids', 'child_of', int(category))]

        if attrib_values:
            attrib = None
            ids = []
            for value in attrib_values:
                if not attrib:
                    attrib = value[0]
                    ids.append(value[1])
                elif value[0] == attrib:
                    ids.append(value[1])
                else:
                    domain += [('attribute_line_ids.value_ids', 'in', ids)]
                    attrib = value[0]
                    ids = [value[1]]
            if attrib:
                domain += [('attribute_line_ids.value_ids', 'in', ids)]

        return domain