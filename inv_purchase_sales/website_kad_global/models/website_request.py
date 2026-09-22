# -*- coding: utf-8 -*-
import re

from odoo import fields, models


class WebsiteRequest(models.Model):
    _name = 'website.request'
    _description = 'Website Form Submission'
    _order = 'create_date desc'
    _rec_name = 'name'

    name = fields.Char(string='Contact Name', required=True)
    email = fields.Char(string='Email')
    phone = fields.Char(string='Phone')
    company = fields.Char(string='Company')
    form_type = fields.Selection([
        ('quote', 'Quote Request'),
        ('contact', 'Contact'),
    ], string='Form Type', default='contact', required=True)
    product = fields.Char(string='Product')
    quantity = fields.Char(string='Quantity')
    country = fields.Char(string='Country')
    port = fields.Char(string='Delivery Port')
    message = fields.Text(string='Message')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('converted', 'Converted to Quotation'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', required=True, copy=False)
    sale_order_id = fields.Many2one('sale.order', string='Quotation', readonly=True, copy=False)

    def _find_or_create_partner(self):
        self.ensure_one()
        partner = self.env['res.partner']
        if self.email:
            partner = partner.search([('email', '=', self.email)], limit=1)
        if not partner:
            partner = partner.create({
                'name': self.company or self.name,
                'email': self.email,
                'phone': self.phone,
            })
        return partner

    def action_convert_to_quotation(self):
        self.ensure_one()
        partner = self._find_or_create_partner()

        order_lines = []
        if self.product:
            product = self.env['product.product'].search([('name', 'ilike', self.product)], limit=1)
            qty_match = re.search(r'[\d.]+', (self.quantity or '').replace(',', ''))
            qty = float(qty_match.group()) if qty_match else 1.0
            if product:
                order_lines.append((0, 0, {
                    'product_id': product.id,
                    'product_uom_qty': qty,
                }))
            else:
                order_lines.append((0, 0, {
                    'name': self.product,
                    'product_uom_qty': qty,
                }))

        note_parts = []
        if self.country:
            note_parts.append("Country: %s" % self.country)
        if self.port:
            note_parts.append("Delivery Port: %s" % self.port)
        if self.message:
            note_parts.append("Message: %s" % self.message)

        sale_order = self.env['sale.order'].create({
            'partner_id': partner.id,
            'origin': 'Website Request #%s' % self.id,
            'order_line': order_lines,
            'note': '\n'.join(note_parts) if note_parts else False,
        })
        self.write({'state': 'converted', 'sale_order_id': sale_order.id})

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'view_mode': 'form',
            'res_id': sale_order.id,
            'target': 'current',
        }

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    def action_view_sale_order(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'view_mode': 'form',
            'res_id': self.sale_order_id.id,
            'target': 'current',
        }
