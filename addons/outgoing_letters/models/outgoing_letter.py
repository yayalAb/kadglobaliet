from odoo import api, fields, models, _
from odoo.exceptions import UserError


class OutgoingLetter(models.Model):
    _name = 'outgoing.letter'
    _description = 'Outgoing Letter'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    name = fields.Char(
        string='Reference', required=True, copy=False, readonly=True,
        default=lambda self: _('New'), tracking=True)
    title = fields.Char(string='Title', tracking=True)
    content = fields.Html(string='Content')
    date = fields.Date(
        string='Date', default=fields.Date.context_today, required=True)
    company_id = fields.Many2one(
        'res.company', string='Company', required=True,
        default=lambda self: self.env.company)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('printable', 'Printable'),
    ], string='Status', default='draft', required=True, copy=False, tracking=True)
    approved_by_id = fields.Many2one(
        'res.users', string='Approved By', readonly=True, copy=False, tracking=True)
    approver_signature = fields.Binary(
        string='Approver Signature', compute='_compute_approver_info')
    approver_name = fields.Char(
        string='Approver Name', compute='_compute_approver_info')

    @api.depends('approved_by_id', 'state', 'write_uid', 'create_uid')
    def _compute_approver_info(self):
        for letter in self:
            approver = letter.approved_by_id or (letter.state in ('approved', 'printable') and (letter.write_uid or letter.create_uid))
            letter.approver_name = approver.name if approver else False
            sig = False
            if approver:
                if hasattr(approver, 'sign_signature') and approver.sign_signature:
                    sig = approver.sign_signature
                elif hasattr(approver, 'employee_id') and approver.employee_id and hasattr(approver.employee_id, 'emp_signature') and approver.employee_id.emp_signature:
                    sig = approver.employee_id.emp_signature
            letter.approver_signature = sig

    def _check_state(self, allowed):
        for letter in self:
            if letter.state not in allowed:
                raise UserError(
                    _('This action is not allowed for letter "%s" in its current status.', letter.title))

    def _check_group(self, group_xmlid):
        if not self.env.user.has_group(group_xmlid):
            raise UserError(
                _('You do not have the rights to perform this action.'))

    def action_submit(self):
        self._check_group('outgoing_letters.group_outgoing_letter_user')
        self._check_state(['draft'])
        self.state = 'submitted'

    def action_approve(self):
        self._check_group('outgoing_letters.group_outgoing_letter_approver')
        self._check_state(['submitted'])
        self.write({
            'state': 'approved',
            'approved_by_id': self.env.user.id,
        })

    def action_set_printable(self):
        self._check_group('outgoing_letters.group_outgoing_letter_approver')
        self._check_state(['approved'])
        self.state = 'printable'

    def action_reset_to_draft(self):
        self._check_group('outgoing_letters.group_outgoing_letter_approver')
        self._check_state(['submitted', 'approved', 'printable'])
        self.write({
            'state': 'draft',
            'approved_by_id': False,
        })

    def action_print(self):
        self.ensure_one()
        self._check_group('outgoing_letters.group_outgoing_letter_user')
        self._check_state(['printable'])
        self.name = self.env['ir.sequence'].next_by_code(
            'outgoing.letter') or _('New')
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
