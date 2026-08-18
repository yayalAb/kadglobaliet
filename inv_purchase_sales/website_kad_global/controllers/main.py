# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from markupsafe import escape, Markup


class KadWebsite(http.Controller):

    @http.route('/kad/contact', type='http', auth='public', website=True, methods=['POST'], csrf=True)
    def kad_contact(self, **post):
        """Receive contact and quote form submissions and email the company."""
        name = (post.get('name') or '').strip()
        email = (post.get('email') or '').strip()
        phone = (post.get('phone') or '').strip()
        company = (post.get('company') or '').strip()
        message = (post.get('message') or '').strip()
        form_type = (post.get('form_type') or 'contact').strip()
        product = (post.get('product') or '').strip()
        quantity = (post.get('quantity') or '').strip()
        country = (post.get('country') or '').strip()
        port = (post.get('port') or '').strip()

        if name and email and (message or product):
            rows = [
                ('Form', 'Quote Request' if form_type == 'quote' else 'Contact'),
                ('Name', name),
                ('Email', email),
                ('Phone', phone or 'N/A'),
                ('Company', company or 'N/A'),
                ('Product', product),
                ('Quantity', quantity),
                ('Country', country),
                ('Delivery Port', port),
                ('Message', message or 'N/A'),
            ]
            chunks = []
            for label, value in rows:
                if value:
                    chunks.append('<p><strong>%s:</strong> %s</p>' % (escape(label), escape(value)))
            body_html = Markup(''.join(chunks))
            email_to = request.env.company.email or 'info@kadglobaltrading.com'
            subject = (
                f'KAD Website Quote — {product or name}'
                if form_type == 'quote'
                else f'KAD Website Contact — {name}'
            )
            request.env['mail.mail'].sudo().create({
                'subject': subject,
                'email_from': request.env.company.email_formatted or email_to,
                'reply_to': email,
                'email_to': email_to,
                'body_html': body_html,
            }).send()

        return request.render('website_kad_global.contact_thanks')
