# coding: utf-8
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2014 Vauxoo - http://www.vauxoo.com/
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
"""This file loads the necessary information for the custom timesheet view.
"""
from odoo import fields, models
from odoo.tools.sql import drop_view_if_exists


class CustomTimesheetAll(models.Model):

    """Class that contains the methods needed to return the data to the view.
    """
    _name = "custom.timesheet.all"
    _order = "date desc"
    _auto = False


    period = fields.Char('Period', 128
                              help='Period for the date of summary work.'),
    date = fields.Date('Date', readonly=True
                            help='Date of summary work.'),
    analytic_id = fields.Many2one('account.analytic.account', 'Project'
                                       readonly=True, index=True),
    userstory = fields.Integer('User Story', readonly=True
                                    help='User history id of user history\
                                     assigned on task.'),
    task_id = fields.Many2one('project.task', 'Task title'
                                   readonly=True, index=True, help='Project\
                                    task title.'),
    user_id = fields.Many2one('res.users', 'User'
                                   readonly=True, index=True, help='User of\
                                    summary work.'),
        'name': fields.Char('Description', 264, help='Description of the\
                            summary work.'),
        'unit_amount': fields.Float('Duration', readonly=True, help='Time\
                                    spent on work.'),
    invoiceable = fields.Many2one('hr_timesheet_invoice.factor'
                                       'Invoiceable', readonly=True,
                                       help='Definition of invoicing status of\
                                        the line.'),
    invoiceables_hours = fields.Float('Invoiceable Hours', readonly=True
                                           help='Total hours to charge.'),


    def init(self, cr):
        """Search method that executes query.
        """
        drop_view_if_exists(cr, 'custom_timesheet_all')
        cr.execute('''
            create or replace view custom_timesheet_all as (
                SELECT
                    work.id AS id,
                    to_char(work.date,'MM/YYYY') AS period,
                    date(work.date) AS date,
                    analytic.id AS analytic_id,
                    us.id AS userstory,
                    task.id AS task_id,
                    work.user_id AS user_id,
                    work.name AS name,
                    work.hours AS unit_amount,
                    acc_anal_line.to_invoice AS invoiceable,
                    work.hours - (work.hours * (hr_ts_factor.factor / 100))
                     AS invoiceables_hours
                FROM project_task_work AS work
                LEFT JOIN hr_analytic_timesheet AS tsheet ON
                 tsheet.id = work.hr_analytic_timesheet_id
                LEFT JOIN account_analytic_line AS acc_anal_line ON
                 acc_anal_line.id = tsheet.line_id
                LEFT JOIN hr_timesheet_invoice_factor AS hr_ts_factor ON
                 hr_ts_factor.id = acc_anal_line.to_invoice
                LEFT JOIN account_analytic_account AS analytic ON
                 analytic.id = acc_anal_line.account_id
                LEFT JOIN project_task AS task ON
                 task.id = work.task_id
                LEFT JOIN user_story AS us ON
                 us.id = task.userstory_id
        )''')
