# coding: utf-8
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

from odoo import fields, models


class AccountAnalyticAccount(models.Model):
    _inherit = "account.analytic.account"

    def _remaining_hours_calc(self, name, arg):
        res = {}
        for account in self.browse(ids):
            if account.quantity_max != 0:
                res[account.id] = account.quantity_max - \
                    account.invoiceables_hours
            else:
                res[account.id] = 0.0
            res[account.id] = round(res.get(account.id, 0.0), 2)
        return res

    def _get_invoiceables_hours(self, args,
                                _fields):
        if context is None:
            context = {}
        res = {}
        total = 0
        for _id in ids:
            acl_obj = self.env['account.analytic.line']
            acl_srch = acl_obj.search([('account_id', '=', _id)])
            acl_brw = acl_obj.browse(acl_srch)
            for acl in acl_brw:
                if acl.to_invoice:
                    total = total + (acl.unit_amount -
                                     (acl.unit_amount *
                                      (acl.to_invoice.factor / 100)))
            res[_id] = total
        return res


    invoiceables_hours = fields.Function(_get_invoiceables_hours
                                              type='float',
                                              string='Units Invoiceable',
                                              help='Total units of hours to \
                                              charge.'),
    remaining_hours = fields.Float(compute="_remaining_hours_calc"
                                           string='Remaining Time',
                                           help="Computed using the formula: \
                                           Maximum Time - Total Worked Time"),

