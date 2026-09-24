from odoo import fields, models, _


class OutgoingLetter(models.Model):
    _name = 'outgoing.letter'
    _description = 'Outgoing Letter'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    name = fields.Char(
        string='Reference', required=True, copy=False, readonly=True,
        default=lambda self: _('New'), tracking=True)
    title = fields.Char(string='Title', required=True, tracking=True)
    content = fields.Html(string='Content')
    date = fields.Date(string='Date', default=fields.Date.context_today, required=True)
    company_id = fields.Many2one(
        'res.company', string='Company', required=True,
        default=lambda self: self.env.company)

    def action_print(self):
        for letter in self.filtered(lambda l: l.name == _('New')):
            letter.name = self.env['ir.sequence'].next_by_code('outgoing.letter') or _('New')
        return self.env.ref('outgoing_letters.action_report_outgoing_letter').report_action(self)
