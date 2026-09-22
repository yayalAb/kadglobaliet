from odoo import fields, models


class DeliveryPort(models.Model):
    _name = 'delivery.port'
    _description = 'Delivery Port'
    _order = 'name'

    name = fields.Char(string='Port Name', required=True)
    code = fields.Char(string='Port Code', required=True)
    country_id = fields.Many2one('res.country', string='Country', required=True)
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ('code_uniq', 'unique(code)', 'Port Code must be unique.'),
    ]

    def name_get(self):
        return [(port.id, '%s (%s)' % (port.name, port.code)) for port in self]
