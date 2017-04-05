# -*- coding: utf-8 -*-
# Copyright 2016 Luis Felipe Mileo <mileo@kmee.com.br> - KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class AccountAnalyticLine(models.Model):

    _inherit = 'account.analytic.line'

    userstory_id = fields.Many2one(
        comodel_name='user.story',
        string='User Story',
        related='task_id.userstory_id',
        store=True
    )
