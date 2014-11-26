from openerp import models, fields, api, _

class account_invoice(models.Model):
    _inherit = 'account.invoice'

    @api.one
    @api.depends('number')
    def _compute_has_txn(self):
        if self.number:
            test = self.env['payment.transaction'].search([('reference','=',self.number)], limit=1)
            if test:
                self.txn_exists = True

    txn_exists = fields.Boolean(string='Online Txn', readonly=True,
        compute='_compute_has_txn', default=False,
        help="Indicates that an online transaction has been received")

