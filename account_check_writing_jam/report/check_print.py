# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012-Today Ursa Information Systems
#                        <http://www.ursainfosystems.com>.
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

import time
from operator import itemgetter
from openerp.report import report_sxw
from openerp.tools.translate import _

N = 9
STARS = 70
LINEKEYS = ['date_due', 'date_original', 'name', 'amount_original', 'amount_due', 'amount']

class report_print_check(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(report_print_check, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'get_data': self.get_vouchers,
        })

    def _getchunk_line(self, defaults=None):
        """
        Method Prepares a speical line to be printed on check description setion
        with given defaults values.
        @param defaults: dict with default values to be added on lines.
        @return: a dict speical lines to be printed on check.
        """
        if defaults == None:
            defaults = {}
        line = dict.fromkeys(LINEKEYS, "")
        line.update(defaults)
        return line

    def _prepare_line(self, line, credit=False):
        sign = credit and -1 or 1
        return {
            'date_due': line.date_due,
            'date_original': line.date_original,
            'name': line.move_line_id and line.move_line_id.ref or line.name,
            'amount_original': line.amount_original and  sign * line.amount_original or False,
            'amount_due': line.amount_unreconciled and sign * line.amount_unreconciled or False,
            'amount': line.amount and sign * line.amount or False,
        }

    def _prepare_pages(self, voucher, lines, n):
        '''
        Prepare page info for check. Adds the empty lines on description section
        to keep check well fromatted
        @param voucher: voucher browse object to be printed.
        @param lines: total payment lines to be added on check.
        @param n: max line to be printed on description section for page stub.
        '''
        check_lines  = [lines[i:i + n] for i in range(0, len(lines), n)]
        return [{'lines': chunk,
                 'amount': voucher.amount,
                 'amount_words': False,
                 'number': self._get_check_number(voucher),
                 'name': voucher.name,
                 'use_preprint_check': voucher.journal_id.use_preprint_check,
                 'date': voucher.date,
                 'partner': voucher.partner_id.name,
                 'address': voucher.partner_id}
                            for chunk in check_lines]

    def _get_check_number(self, voucher):
        '''
        Wrapper function for special case where customisation may require
        getting check number else where in child parser
        '''
        return voucher.journal_id.use_preprint_check and '' or voucher.check_number

    def _prepare_first_page(self, voucher, stars):
        '''
        Change amounts on first page of check, can be inherited or overridden.
        
        '''
        return {
            'chk_amount': voucher.amount,
            'amount_words': voucher.amount_in_word and
                voucher.amount_in_word.ljust(stars, '*') or ''.ljust(stars, '*')
        }

    def get_vouchers(self, objects, n=N, stars=STARS):
        '''
        Wrapper function to get record to be printed on rml. It will add the
        pages and correction section to be printed.
        @param: objects - a list of objects 
        @param: n - number of max line in description section.
        @param: stars - max number of start to be added after amount fo words to
                     fill the line.
        @returns a list of pages as a dict.
        '''
        res = []
        for voucher in objects:
            res.extend(self._get_data(voucher, n, stars))
        return res

    def _get_data(self, voucher, n=N, stars=STARS):
        '''
        Parses the voucher and chunks it in to a dictionary for the report.
        - It arranges the items section for credit and debit section to be printed.
        - Pad the extra lines on stub description section to be printed as empty spaces.
        - Finally, Add the check amounts to first page and prepare the final value.
        '''
        credit_section = voucher.company_id.credit_section
        suppress_unpaid = voucher.company_id.suppress_unpaid
        #first chunk up the lines
        dr_lines = [self._prepare_line(line) for line in voucher.line_dr_ids
                        if line.amount or not suppress_unpaid]
        cr_lines = [self._prepare_line(line, 1) for line in voucher.line_cr_ids
                        if line.amount or not suppress_unpaid]
        #This section just arranges the items
        if credit_section:
            dr_lines.sort(key=itemgetter('date_original'))
            cr_lines.sort(key=itemgetter('date_original'))
            #credits to next page if needed
            lines = ([self._getchunk_line({'name': _('Invoices')})] + dr_lines +
                     (cr_lines and [self._getchunk_line({'name': _('Credits')})] + cr_lines or []))
        else:
            lines = dr_lines + cr_lines
            lines.sort(key=itemgetter('date_original'))
        #just pad up the lines -
        #only 1 field really necessary RML will handle rest
        lines.extend([self._getchunk_line() for i in range(n - len(lines) % n)])
        pages = self._prepare_pages(voucher, lines, n)
        #now add the check amounts to first page
        pages[0].update(self._prepare_first_page(voucher, stars))
        if not voucher.company_id.multi_stub:
            return [pages[0]]
        return pages

report_sxw.report_sxw(
     'report.account.print.check.top',
     'account.voucher',
     'addons/account_check_writing/report/check_print_top.rml',
     parser=report_print_check,
     header=False
)

report_sxw.report_sxw(
    'report.account.print.check.middle',
    'account.voucher',
    'addons/account_check_writing/report/check_print_middle.rml',
    parser=report_print_check,
    header=False
)

report_sxw.report_sxw(
    'report.account.print.check.bottom',
    'account.voucher',
    'addons/account_check_writing/report/check_print_bottom.rml',
    parser=report_print_check,
    header=False
)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
