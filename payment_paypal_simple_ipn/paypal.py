
from openerp.osv import osv, fields

class AcquirerPaypal(osv.Model):
    _inherit = 'payment.acquirer'

    def _get_paypal_urls(self, cr, uid, environment=None, context=None):
        """ Paypal URLS """
        if not environment:
            acquirer_id = self.pool['payment.acquirer'].search(cr, uid, [('provider', '=', 'paypal')])[0]
            environment = self.pool['payment.acquirer'].browse(cr, uid, acquirer_id, context=context).environment
        return super(AcquirerPaypal,self)._get_paypal_urls(cr, uid, environment, context=context)

class TxPaypal(osv.Model):
    _inherit = 'payment.transaction'

    def _prepare_new_txn(self, cr, uid, data, context=None):
        # comb post data for creating a new transaction
        if not context:
            context = {}
        invoice = None
        sales_order = None
        reference = data.get('item_number')
        iv_ids = self.pool['account.invoice'].search(cr, uid, [('number','=',reference)], context=context)
        if iv_ids:
            invoice = self.pool['account.invoice'].browse(cr, uid, iv_ids, context=context)
            partner = self.pool['res.partner'].browse(cr, uid, invoice.partner_id.id, context=context)
        else:
            so_ids = self.pool['sales.order'].search(cr, uid, [('name','=',reference)])
            if so_ids:
                sales_order = self.pool['sales.order'].browse(cr, uid, so_ids, context=context)
                Partner = self.pool['res.partner'].browse(cr, uid, sales_order.partner_id.id, context=context)
            else:
                return None
        acquirer = self.pool['payment.acquirer']
        acquirer_id = acquirer.search(cr, uid, [('provider', '=', 'paypal')])[0]
        txn_data = {
            'reference': reference,
            'paypal_txn_id': data.get('txn_id'),
            'paypal_txn_type': data.get('txn_type'),
            'type': 'form',
            'acquirer_id': self.pool['payment.acquirer'].search(cr, uid, [('provider', '=', 'paypal')])[0],
            'state': 'pending',
            'acquirer_reference': data.get('txn_id'),
            'partner_reference': data.get('payer_id'),
            'date_create': invoice and invoice.date_invoice or sales_order.date_order,
            'amount': invoice and invoice.amount_total or sales_order.amount_total,
            'fees': acquirer.paypal_compute_fees(cr, uid, acquirer_id,
                                        invoice and invoice.amount_total or sales_order.amount_total,
                                        invoice and invoice.currency_id.id or sales_order.pricelist_id.currency_id.id,
                                        partner.country_id.id,
                                        context),
            'currency_id': invoice and invoice.currency_id.id or sales_order.pricelist_id.currency_id.id,
            'partner_id': partner.id,
            'partner_name': partner.name,
            'partner_lang': partner.lang,
            'partner_email': partner.email,
            'partner_zip': partner.zip,
            'partner_address': partner.contact_address,
            'partner_city': partner.city,
            'partner_country_id': partner.country_id.id,
            'partner_phone': partner.phone,
        }
        return txn_data

    def _paypal_form_get_tx_from_data(self, cr, uid, data, context=None):
        tx_ids = self.pool['payment.transaction'].search(cr, uid, [('reference', '=', reference)], context=context)
        if not tx_ids:
            new_txn = self._prepare_new_txn(cr, uid, data, context=context)
            new_txn_id = self.create(cr, uid, new_txn, context=context)
        return super(TxPaypal,self)._paypal_form_get_tx_from_data(cr, uid, data, context=context)

