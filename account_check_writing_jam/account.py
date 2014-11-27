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

from openerp import SUPERUSER_ID
from openerp.osv import osv, fields
from openerp.tools.translate import _


class account_journal(osv.osv):
    _inherit = "account.journal"

    _columns = {
        'allow_check_writing': fields.boolean('Allow Check Writing',
                help='Check this to be able to write checks using this journal.'),
        'use_preprint_check': fields.boolean('Use Preprinted Checks',
                help="Check this if your checks already have a number preprinted on them. Otherwise check numbers will be printed on paper."),
        'check_sequence_id': fields.many2one('ir.sequence', 'Check Sequence',
                help="This field contains the information related to the numbering of the Check of this journal."),
        }

    def configure_check_journal(self, cr, uid, context=None):
        '''
        This function set up bank journal to be used on check payment by
        setting allow check writing on bank type journals this function will
        be triggered while installing module.
        '''
        journal_ids = self.search(cr, uid, [('type', '=', 'bank')], context=context)
        if journal_ids:
            self.write(cr, uid, journal_ids, {'allow_check_writing': True}, context=context)
        return True

    def onchange_journal_type(self, cr, uid, ids, type, context=None):
        """
        on change journal type enable the allow_check_writing flag to allow
        configuration of check journal.
        """
        return {'value': {'allow_check_writing': type == "bank"}}

    def create_check_sequence(self, cr, uid, vals, context=None):
        """
        Create new no_gap entry sequence for check Journal using given vals.
        """
        val = {
            'name': vals['name'] + _(" : Check Number Sequence"),
            'implementation': 'no_gap',
            'padding': 4,
            'number_increment': 1
        }
        if 'company_id' in vals:
            val['company_id'] = vals['company_id']
        return self.pool.get('ir.sequence').create(cr, uid, val, context)

    def create(self, cr, uid, vals, context=None):
        if not 'check_sequence_id' in vals or not vals['check_sequence_id']  and vals.get('allow_check_writing'):
            # if we have the right to create a journal, we should be able to
            # create it's check number sequence.
            vals.update({'check_sequence_id': self.create_check_sequence(cr, SUPERUSER_ID, vals, context)})
        return super(account_journal, self).create(cr, uid, vals, context)


class tmodel_multi_charts_accounts(osv.TransientModel):

    _inherit = 'wizard.multi.charts.accounts'

    def _prepare_bank_journal(self, cr, uid, line, current_num, default_account_id, company_id, context=None):
        '''
        This function prepares the value to use for the creation of a bank and
        addes the allow_check_writing flag value for Bank Type journal
        :rtype: dict
        '''
        vals = super(tmodel_multi_charts_accounts, self)._prepare_bank_journal(cr, uid, line, current_num, default_account_id, company_id, context=context)
        if line['account_type'] == "bank":
            vals.update({'allow_check_writing': True})
        return vals


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
