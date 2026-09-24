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
        self.ensure_one()
        self.name = self.env['ir.sequence'].next_by_code('outgoing.letter') or _('New')
        pdf_content, __ = self.env['ir.actions.report']._render_qweb_pdf(
            'outgoing_letters.action_report_outgoing_letter', self.ids)
        attachment = self.env['ir.attachment'].create({
            'name': 'Letter - %s.pdf' % self.name.replace('/', '-'),
            'type': 'binary',
            'raw': pdf_content,
            'res_model': self._name,
            'res_id': self.id,
            'mimetype': 'application/pdf',
        })
        self.message_post(
            body=_('Letter printed with reference %s', self.name),
            attachment_ids=attachment.ids)
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%s?download=true' % attachment.id,
            'target': 'self',
        }
