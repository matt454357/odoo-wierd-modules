# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-Today OpenERP S.A. (<http://www.openerp.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from lxml import etree
from openerp.osv import osv, fields
from openerp.tools.translate import _
from openerp.tools import amount_to_text_en


class account_voucher(osv.Model):
    _inherit = 'account.voucher'

    def _get_currency(self, cr, uid, context=None):
        res = super(account_voucher, self)._get_currency(cr, uid, context)
        if not res:
            res = self.pool.get("res.users").browse(cr, uid, uid).company_id.currency_id.id
        return res

    def _make_journal_search(self, cr, uid, ttype, context=None):
        """ 
        Inherited: Add only check writing journal seacrh behaviour for Checks action view.
        """
        if context is None:
            context = {}
        journal_pool = self.pool.get('account.journal')
        if context.get('write_check'):
            return journal_pool.search(cr, uid, [('allow_check_writing', '=', True)], limit=1, context=context)
        return journal_pool.search(cr, uid, [('type', '=', ttype)], limit=1, context=context)

    _columns = {
        'amount_in_word': fields.char("Amount in words", size=1024),
        'allow_check': fields.related('journal_id', 'allow_check_writing', type='boolean', string='Allow Check Writing'),
        'check_number': fields.char('Check Number', size=32),
        'journal_id': fields.many2one('account.journal', 'Journal', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'check_done': fields.boolean("Check Printed")
    }

    _sql_constraints = [
        ('check_per_journal_uniq', 'unique(check_number, journal_id)', 'Check Number Must be Unique Per Journal!'),
    ]

    def onchange_amount(self, cr, uid, ids, amount, rate, partner_id, journal_id, currency_id, ttype, date, payment_rate_currency_id, company_id, context=None):
        """ 
        Inherited: add amount_in_word and allow_check_writing in @returned value dictionary 
        """
        if not context:
            context = {}
        default = super(account_voucher, self).onchange_amount(cr, uid, ids, amount, rate, partner_id, journal_id, currency_id, ttype, date, payment_rate_currency_id, company_id, context=context)
        if 'value' in default:
            amount = 'amount' in default['value'] and default['value']['amount'] or amount
            currency = self.pool.get('res.currency').browse(cr, uid, currency_id, context=context)
            language = 'en'
            if context.get('lang'):
                language = context.get('lang')[0:2]
            currency = currency.name.lower()
            amount_in_word = amount_to_text_en.amount_to_text(amount, lang=language, currency=currency)
            default['value'].update({'amount_in_word': amount_in_word})
            if journal_id:
                allow_check_writing = self.pool.get('account.journal').browse(cr, uid, journal_id, context=context).allow_check_writing
                default['value'].update({'allow_check': allow_check_writing})
        return default

    def onchange_journal(self, cr, uid, ids, journal_id, line_ids, tax_id, partner_id, date, amount, ttype, company_id, context=None):
        """ 
        Inherited: add currency_id @returned value dictionary 
        """
        vals = super(account_voucher, self).onchange_journal(cr, uid, ids, journal_id, line_ids, tax_id, partner_id, date, amount, ttype, company_id, context=context)
        if vals and not vals.get('value', {})['currency_id']:
            vals['value']['currency_id'] = self.pool.get("res.users").browse(cr, uid, uid).company_id.currency_id.id
        return vals

    def copy(self, cr, uid, ids, default=None, context=None):
        if default is None:
            default = {}
        default['check_number'] = False
        return super(account_voucher, self).copy(cr, uid, ids, default=default, context=context)

    def fields_view_get(self, cr, uid, view_id=None, view_type=False, context=None, toolbar=False, submenu=False):
        """
        Inherited: Add domain 'allow_check_writing = True' on journal_id
                   field and remove 'widget = selection' on the same field
                   because the dynamic domain is not allowed on such widget.
        """
        if context == None:
            context = {}
        res = super(account_voucher, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
        doc = etree.XML(res['arch'])
        nodes = doc.xpath("//field[@name='journal_id']")
        if context.get('write_check', False):
            for node in nodes:
                node.set('domain', "[('type', '=', 'bank'), ('allow_check_writing','=',True)]")
                node.set('widget', '')
            res['arch'] = etree.tostring(doc)
        return res

    def print_check(self, cr, uid, ids, context=None):
        """
        Method will either print the report or will call the Print check wizard.
        This button will appear in from view only so, If check is assigned with
        check number then it will print the check directly or else it will call 
        the betch check batch printing wizard to assign check number first and
        thenprint the check.
        
        @return: return the action (either report action or act_window action)
        """
        if context == None:
            context = {}
        value = {}
        model_data = self.pool.get('ir.model.data')
        check_layout_report = {
            'top': 'account.print.check.top',
            'middle': 'account.print.check.middle',
            'bottom': 'account.print.check.bottom',
        }
        check = self.browse(cr, uid, ids[0], context=context)
        if check.check_number or check.journal_id.use_preprint_check:
            check_layout = check.company_id.check_layout
            value = {
                'type': 'ir.actions.report.xml',
                'report_name': check_layout_report[check_layout],
                'datas': {
                    'model': 'account.voucher',
                    'id': ids and ids[0] or False,
                    'ids': ids and ids or [],
                    'report_type': 'pdf'
                },
                'nodestroy': True
            }
        else:
            form_view = model_data.get_object_reference(cr, uid, 'account_check_writing', 'view_account_check_write')
            value = {
                'name': _('Print Check'),
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'account.check.write',
                'views': [(form_view and form_view[1] or False, 'form'), (False, 'tree')],
                'type': 'ir.actions.act_window',
                'target': 'new',
                'context': context,
            }
        return value

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
